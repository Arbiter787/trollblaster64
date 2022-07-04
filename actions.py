from __future__ import annotations

import math
from dice import dice_roller
from typing import Optional, Tuple, TYPE_CHECKING

from equipment_types import EquipmentTraits

import color
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the Engine this action belongs to."""
        return self.entity.gamemap.engine

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        'self.engine' is the scope this action is being performed in.

        'self.entity' is the object performing the action.

        This method must be overridden by Action subclasses.
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You pick up the {item.name}.")
                return

        raise exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the item's ability. This action will be given to provide context."""
        if self.item.consumable:
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the staircase.", color.descend
            )
        else:
            raise exceptions.Impossible("There are no stairs here.")


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this action's destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Returns the blocking entity at this action's destination."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Returns the actor at this action's destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    """Attack another actor immediately adjacent to the parent actor."""
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise exceptions.Impossible("Nothing to attack.")
        
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        last_attack_hit = False

        for i in range(self.entity.fighter.attacks_per_round):
            
            # attack info format: [to hit, number of dice, die size, damage bonuses, equipment trait list, critical dice (tuple form)]
            attack_info = self.entity.fighter.damage

            to_hit = attack_info[0]
            num_dice = attack_info[1]
            die_size = attack_info[2]
            dam_bonus = attack_info[3]
            equipment_traits = attack_info[4]
            crit_bonus = attack_info[5]

            if crit_bonus is not None:
                crit_num = crit_bonus[0]
                crit_size = crit_bonus[1]

            deadly = False
            fatal = False

            # TODO: pull data from entity instead of hardcode at 0
            extra_attack_penalty_mod = 0

            # modify attack based on the various item traits
            if equipment_traits is not None:
                for x in equipment_traits:
                    if x == EquipmentTraits.AGILE:
                        extra_attack_penalty_mod += 1
                    elif x == EquipmentTraits.BACKSWING:
                        if last_attack_hit == False:
                            extra_attack_penalty_mod += 1
                    elif x == EquipmentTraits.DEADLY:
                        deadly = True
                    elif x == EquipmentTraits.FATAL:
                        fatal = True
                    elif x == EquipmentTraits.FINESSE:
                        # don't do finesse if the attack is from a monster, since finesse already factors into their to-hit
                        if self.entity is self.engine.player:
                            to_hit -= self.entity.fighter.str_mod
                            to_hit += max(self.entity.fighter.dex_mod, self.entity.fighter.str_mod)
                    elif x == EquipmentTraits.FORCEFUL:
                        for z in range(i):
                            dam_bonus += num_dice
                    elif x == EquipmentTraits.SWEEP:
                        extra_attack_penalty_mod += 1

            # roll attack roll and add to-hit mod, for every attack besides the first in a round subtract 5 (can be modified by weapon)
            nat_roll = dice_roller(1, 20)
            to_hit = to_hit - i * (5 - extra_attack_penalty_mod)
            attack_roll = nat_roll + to_hit

            self.engine.message_log.add_message(
                f"{self.entity.name.capitalize()} rolls a {nat_roll} + {to_hit} to hit {target.name}.",
                attack_color
            )

            # if attack roll exceeds ac by more than 10 or is a nat 20 crit and deal double damage
            if attack_roll >= target.fighter.ac:
                if attack_roll - target.fighter.ac >= 10 or nat_roll == 20:
                    
                    # calculate fatal damage/normal crit damage
                    if fatal == True:
                        damage = dice_roller(num_dice + 1, crit_size) + dam_bonus * 2
                    else:
                        damage = dice_roller(num_dice, die_size) + dam_bonus * 2
                    
                    # if deadly then add the deadly dice
                    if deadly == True:
                        damage += dice_roller(crit_num, crit_size)
                    
                    # inform player of critical
                    self.engine.message_log.add_message(
                        "That was a critical hit!",
                        attack_color
                    )
                else:
                    damage = dice_roller(num_dice, die_size) + dam_bonus
            
            # if attack roll was a miss but was a nat 20 make it a hit
            elif nat_roll == 20 and attack_roll - target.fighter.ac < 10:
                damage = dice_roller(num_dice, die_size) + dam_bonus
            
            # miss
            else:
                damage = 0

            # TODO: pull attack desc from attack itself
            attack_desc = f"{self.entity.name.capitalize()} kicks {target.name}"

            if damage > 0:
                self.engine.message_log.add_message(
                    f"{attack_desc} for {damage} damage.", attack_color
                )
                target.fighter.hp -= damage
                last_attack_hit = True

                # don't keep attacking if they die!
                if not target.is_alive:
                    break

            else:
                self.engine.message_log.add_message(
                    f"{self.entity.name.capitalize()} misses {target.name}.", attack_color
                )
                last_attack_hit = False


class MovementAction(ActionWithDirection):
    """Move the actor one tile in a direction."""
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            raise exceptions.Impossible("That way is blocked.")
        
        # debug logging messages here
        #self.engine.message_log.add_message(f"ancestry: {self.engine.player.fighter.ancestry.hp_boost} class: {self.engine.player.fighter.player_class.hp_boost}")

        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

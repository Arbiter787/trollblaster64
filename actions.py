from __future__ import annotations

import math
import random
from typing import Optional, Tuple, TYPE_CHECKING

import color
from components.equippable import Equippable
from equipment_types import EquipmentType
import exceptions

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor, actions: int = 1) -> None:
        super().__init__()
        self.entity = entity
        self.actions = actions

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

                self.entity.actions.deduct_actions(self.actions)
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
            self.entity.actions.deduct_actions(self.actions)
            self.item.consumable.activate(self)


class DropItem(ItemAction):
    def perform(self) -> None:
        """Remove the item from the inventory. If it's equipped, unequip it first. Dropping a weapon is a free action."""
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item, True)
            if self.item.equippable.equipment_type != EquipmentType.WEAPON:
                self.entity.actions.deduct_actions(self.actions)
        else:
            self.entity.actions.deduct_actions(self.actions)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        """Equip/unequip the item."""
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.actions.deduct_actions(self.actions)
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> None:
        self.entity.actions.deduct_actions(self.actions)
        pass


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.entity.actions.deduct_actions(self.actions)
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
        # Damage = (attack power / defense + 1) - (1/5 defense) rounded up TODO: work out a better defense calc
        damage = math.ceil((self.entity.fighter.power / (target.fighter.defense + 1)) - (target.fighter.defense / 5))
        if damage < 0:
            damage = 0

        self.entity.actions.deduct_actions(self.actions)
        attack_desc = f"{self.entity.name.capitalize()} kicks {target.name}"
        if self.entity is self.engine.player:
            attack_color = color.player_atk
        else:
            attack_color = color.enemy_atk

        # Calculate dodge chance (for now hardcoded at 25%) TODO: Add dodge modifier system
        if random.random() < 0.25:
            self.engine.message_log.add_message(
                f"{self.entity.name.capitalize()} misses {target.name}.",
                attack_color
            )
            return None

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} damage.", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage.", attack_color
            )


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

        self.entity.actions.deduct_actions(self.actions)
        self.entity.move(self.dx, self.dy)


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()

        else:
            return MovementAction(self.entity, self.dx, self.dy).perform()

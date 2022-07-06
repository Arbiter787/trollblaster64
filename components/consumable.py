from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Tuple, List

import numpy as np
import actions
import color
import components.ai
import components.inventory
from components.base_component import BaseComponent
from exceptions import Impossible
import input_handlers
import random
from dice import dice_roller
import tcod.path
import animations

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item."""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this item's ability.

        'action' is the context for this activation.
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory."""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)


class ConfusionConsumable(Consumable):
    def __init__(self, number_of_turns: int, animation: Optional[bool] = False, color: Optional[Tuple[int, int, int]] = color.purple):
        self.number_of_turns = number_of_turns
        self.animation = animation
        self.color = color

    def get_action(self, consumer: Actor) -> input_handlers.SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return input_handlers.SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> Optional[animations.BurstAnimation]:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.in_bounds(*action.target_xy):
            raise Impossible("You cannot target an area that you cannot see.")
        elif not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if not target:
            raise Impossible("You must select a target.")
        if target is consumer:
            raise Impossible("You cannot confuse yourself!")

        self.engine.message_log.add_message(
            f"The {target.name} looks confused, and begins to stumble around!",
            color.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target, previous_ai=target.ai, turns_remaining=self.number_of_turns
        )
        self.consume()
        if self.animation:
            animation = animations.BurstAnimation(target, self.color)
            return animation


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"You use the {self.parent.name}, and recover {amount_recovered} HP!",
                color.health_recovered,
            )
            self.consume()
        else:
            raise Impossible(f"Your health is already full.")


class RadiusDamageConsumable(Consumable):
    def __init__(self, num_dice: int, die_size: int, radius: int, animation: Optional[bool] = False, color: Optional[Tuple[int, int, int]] = color.white):
        self.num_dice = num_dice
        self.die_size = die_size
        self.radius = radius
        self.animation = animation
        self.color = color

    def get_action(self, consumer: Actor) -> input_handlers.AreaRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return input_handlers.AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def activate(self, action: actions.ItemAction) -> Optional[animations.ExplosionAnimation]:
        target_xy = action.target_xy

        if not self.engine.game_map.in_bounds(*action.target_xy):
            raise Impossible("You cannot target an area you cannot see.")
        if not self.engine.game_map.visible[target_xy]:
            raise Impossible("You cannot target an area you cannot see.")

        targets_hit = False
        damage = dice_roller(self.num_dice, self.die_size)

        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is engulfed in a fiery explosion, taking {damage} damage!"
                )
                actor.fighter.take_damage(damage)
                targets_hit = True

        if not targets_hit:
            raise Impossible("There are no targets in the radius.")
        
        self.consume()

        if self.animation:
            animation = animations.ExplosionAnimation(target_xy[0], target_xy[1], self.radius, self.color)
            return animation


class SingleTargetDamageConsumable(Consumable):
    def __init__(self, num_dice, die_size, maximum_range: int, animation: Optional[bool] = False, color: Optional[Tuple[int, int, int]] = color.white):
        self.num_dice = num_dice
        self.die_size = die_size
        self.maximum_range = maximum_range
        self.animation = animation
        self.color = color

    def activate(self, action: actions.ItemAction) -> Optional[animations.BurstAnimation]:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            damage = dice_roller(self.num_dice, self.die_size)

            self.engine.message_log.add_message(
                f"A lightning bolt strikes the {target.name}, dealing {damage} damage!"
            )
            target.fighter.take_damage(damage)
            
            self.consume()

            if self.animation:
                animation = animations.BurstAnimation(target, self.color)
                return animation
        else:
            raise Impossible("No enemy is close enough to strike.")


class ProjectileConsumable(Consumable):
    """A consumable that shoots a visible projectile in a straight line toward a target."""
    def __init__(
        self,
        num_dice: int, 
        die_size: int, 
        reusable: bool = False,
        projectile_color: Tuple[int, int, int] = color.white
    ):
        self.num_dice = num_dice
        self.die_size = die_size
        self.reusable = reusable
        
        self.projectile_color = projectile_color

    def get_action(self, consumer: Actor) -> input_handlers.SingleRangedAttackHandler:
        self.engine.message_log.add_message(
            "Select a target location.", color.needs_target
        )
        return input_handlers.SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )

    def get_path_to(self, origin: Actor, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Compute and return a path from origin to the target coordinates, ignoring terrain.

        If there is no valid path returns an empty list.
        """
        # Create a new array the same size as the gamemap, but with all tiles marked as walkable.
        cost = np.full_like(origin.gamemap.tiles, 1, dtype=np.int8)

        # Create a graph from the cost array and pass that graph to a new pathfinder.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((origin.x, origin.y))  # Set start coordinates.

        # Compute the path to the destination and remove the starting point.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Convert from List[List[int]] to List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]

    def activate(self, action: actions.ItemAction) -> animations.ProjectileAnimation:
        consumer = action.entity
        target = action.target_xy

        if not self.engine.game_map.in_bounds(*action.target_xy):
            raise Impossible("You cannot target an area that you cannot see.")
        elif not self.engine.game_map.visible[action.target_xy]:
            raise Impossible("You cannot target an area that you cannot see.")
        if target[0] == consumer.x and target[1] == consumer.y:
            raise Impossible("You cannot target yourself!")

        path = self.get_path_to(consumer, target[0], target[1])

        x_y = (consumer.x, consumer.y)
        hit_actor = None

        if path:
            for tile_xy in path:
                if not self.engine.game_map.tiles["walkable"][tile_xy[0], tile_xy[1]]:
                    break
                elif self.engine.game_map.get_actor_at_location(tile_xy[0], tile_xy[1]):
                    x_y = tile_xy
                    hit_actor = self.engine.game_map.get_actor_at_location(tile_xy[0], tile_xy[1])
                    break
                else:
                    x_y = tile_xy
            
            self.consume()
            if self.reusable:
                self.parent.place(*x_y, self.engine.game_map)
            
            if hit_actor:
                damage = dice_roller(self.num_dice, self.die_size)

                self.engine.message_log.add_message(
                    f"The {self.parent.name} strikes the {hit_actor.name}, dealing {damage} damage!"
                )
                hit_actor.fighter.take_damage(damage)

            animation = animations.ProjectileAnimation(consumer, x_y[0], x_y[1], color=self.projectile_color)
            return animation

        else:
            raise Impossible("Something went wrong with projectile pathfinding. Tell Luke if you see this!")
            
    
class TeleportConsumable(Consumable):
    def __init__(self, maximum_range: int):
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity

        already_chosen = [(consumer.x, consumer.y)]

        valid_tile = None

        # choose a random tile to teleport to
        for x in range(self.maximum_range ** 2):
            potential_x = 0
            potential_y = 0 
            
            # keep generating tiles until you have one that hasn't been picked already
            while True:
                potential_x = random.randint(consumer.x - self.maximum_range, consumer.x + self.maximum_range)
                potential_y = random.randint(consumer.y - self.maximum_range, consumer.y + self.maximum_range)

                potential_tile = (potential_x, potential_y)

                if potential_tile in already_chosen:
                    continue
                else:
                    break
            
            already_chosen.append(potential_tile)

            # make sure tile is in bounds and walkable
            if not self.engine.game_map.in_bounds(*potential_tile):
                continue
            elif not self.engine.game_map.tiles["walkable"][potential_x, potential_y]:
                continue
            
            # check for actors in potential tile
            actor_occupying = False
            for entity in self.engine.game_map.actors:
                if entity.x == potential_x and entity.y == potential_y:
                    actor_occupying = True
            if actor_occupying:
                continue
            
            valid_tile = potential_tile
            break


        if valid_tile is None:
            raise Impossible("There is nowhere to teleport to!")
        else:
            self.engine.message_log.add_message(
                "With a loud *pop*, you teleport away."
            )
            
            consumer.place(potential_x, potential_y)
            self.consume()

from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Optional

import color
import numpy as np
import tcod.path

from entity import Actor

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine

class BaseAnimation:
    def __init__(self, frames: int = 0) -> None:
        self.frames = frames
    
    def anim_render(self, console: Console, engine: Engine) -> bool:
        """Render the animation. Return True if the current animation is complete."""
        return True

class AttackAnimation(BaseAnimation):
    """Render a burst coming out of the target, in the opposite direction of the attacker."""
    def __init__(self, entity: Actor, attacker: Actor) -> None:
        super().__init__(10)
        self.entity = entity
        self.attacker = attacker

        self.x = entity.x
        self.y = entity.y

        if attacker.x > entity.x and attacker.y == entity.y:
            self.attacker_location = 'right'
        elif attacker.x < entity.x and attacker.y == entity.y:
            self.attacker_location = 'left'
        elif attacker.x == entity.x and attacker.y > entity.y:
            self.attacker_location = 'below'
        elif attacker.x == entity.x and attacker.y < entity.y:
            self.attacker_location = 'above'
        elif attacker.x > entity.x and attacker.y > entity.y:
            self.attacker_location = 'below_right'
        elif attacker.x > entity.x and attacker.y < entity.y:
            self.attacker_location = 'above_right'
        elif attacker.x < entity.x and attacker.y > entity.y:
            self.attacker_location = 'below_left'
        elif attacker.x < entity.x and attacker.y < entity.y:
            self.attacker_location = 'above_left'
    
    def anim_render(self, console: Console, engine: Engine) -> bool:
        x_offset = engine.viewport.x_offset
        y_offset = engine.viewport.y_offset

        if self.attacker_location == 'right':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset, string=chr(0xE104), fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset+1, string=chr(0xE107), fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset-1, string=chr(0xE105), fg=[255, 0, 0])
        elif self.attacker_location == 'left':
            console.print(x=self.x+x_offset+1, y=self.y+y_offset, string=chr(0xE103), fg=[255, 0, 0])
            console.print(x=self.x+x_offset+1, y=self.y+y_offset-1, string=chr(0xE106), fg=[255, 0, 0])
            console.print(x=self.x+x_offset+1, y=self.y+y_offset+1, string=chr(0xE108), fg=[255, 0, 0])
        elif self.attacker_location == 'below':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset-1, string=f"{chr(0xE105)}{chr(0xE101)}{chr(0xE106)}", fg=[255, 0, 0])
        elif self.attacker_location == 'above':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset+1, string=f"{chr(0xE107)}{chr(0xE102)}{chr(0xE108)}", fg=[255, 0, 0])
        elif self.attacker_location == 'below_right':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset-1, string=f"{chr(0xE105)}{chr(0xE101)}", fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset, string=chr(0xE104), fg=[255, 0, 0])
        elif self.attacker_location == 'above_right':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset, string=chr(0xE104), fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset+1, string=f"{chr(0xE107)}{chr(0xE102)}", fg=[255, 0, 0])
        elif self.attacker_location == 'below_left':
            console.print(x=self.x+x_offset, y=self.y+y_offset-1, string=f"{chr(0xE101)}{chr(0xE106)}", fg=[255, 0, 0])
            console.print(x=self.x+1+x_offset, y=self.y+y_offset, string=chr(0xE103), fg=[255, 0, 0])
        elif self.attacker_location == 'above_left':
            console.print(x=self.x+x_offset+1, y=self.y+y_offset, string=chr(0xE103), fg=[255, 0, 0])
            console.print(x=self.x+x_offset, y=self.y+y_offset+1, string=f"{chr(0xE102)}{chr(0xE108)}", fg=[255, 0, 0])


        self.frames -= 1

        if self.frames == 0:
            return True
        else:
            return False


class ProjectileAnimation(BaseAnimation):
    """Render a projectile from the origin actor to a given point."""
    def __init__(self, origin: Actor, target_x: int, target_y: int, color: Optional[Tuple[int, int, int]] = color.white):
        super().__init__(10)
        self.origin = origin
        self.target_x = target_x
        self.target_y = target_y
        self.color = color

        self.last_tile = (self.origin.x, self.origin.y)

        self.path = self.get_path_to(self.origin, self.target_x, self.target_y)
        
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

    def anim_render(self, console: Console, engine: Engine) -> bool:

        x_offset = engine.viewport.x_offset
        y_offset = engine.viewport.y_offset

        if not self.path:
            return True
        
        tile_xy = self.path.pop(0)
        if tile_xy[0] == self.origin.x and tile_xy[1] == self.origin.y:
            return True
        
        # print different tiles based on where the projectile is moving
        if tile_xy[0] != self.last_tile[0]:
            if tile_xy[1] == self.last_tile[1]:
                console.print(x=tile_xy[0] + x_offset, y=tile_xy[1] + y_offset, string="-", fg=self.color)
            elif tile_xy[1] > self.last_tile[1]:
                if tile_xy[0] > self.last_tile[0]:
                    console.print(x=tile_xy[0] + x_offset, y=tile_xy[1] + y_offset, string="\\", fg=self.color)
                else:
                    console.print(x=tile_xy[0] + x_offset, y=tile_xy[1] + y_offset, string="/", fg=self.color)
            else:
                if tile_xy[0] > self.last_tile[0]:
                    console.print(x=tile_xy[0] + x_offset, y=tile_xy[1] + y_offset, string="/", fg=self.color)
                else:
                    console.print(x=tile_xy[0] + x_offset, y=tile_xy[1] + y_offset, string="\\", fg=self.color)
        elif tile_xy[1] != self.last_tile[1]:
            console.print(x=tile_xy[0] + x_offset, y=tile_xy[1] + y_offset, string="|", fg=self.color)

        self.last_tile = tile_xy
        if len(self.path) == 0:
            return True
        else:
            return False

        
class BurstAnimation(BaseAnimation):
    """Render a burst around the origin actor."""
    def __init__(self, origin: Actor, color: Optional[Tuple[int, int, int]] = color.white):
        super().__init__(10)
        self.origin = origin
        self.color = color
        self.x = self.origin.x
        self.y = self.origin.y
    
    def anim_render(self, console: Console, engine: Engine) -> bool:
        
        x_offset = engine.viewport.x_offset
        y_offset = engine.viewport.y_offset

        console.print(x=self.x + x_offset - 1, y=self.y + y_offset - 1, string="\\|/", fg=self.color)
        console.print(x=self.x + x_offset - 1, y=self.y + y_offset, string="-", fg=self.color)
        console.print(x=self.x + x_offset + 1, y=self.y + y_offset, string="-", fg=self.color)
        console.print(x=self.x + x_offset - 1, y=self.y + y_offset + 1, string="/|\\", fg=self.color)

        self.frames -= 1

        if self.frames == 0:
            return True
        else:
            return False


class ExplosionAnimation(BaseAnimation):
    """Render an explosion effect around the origin point with the given radius."""
    def __init__(self, origin_x: int, origin_y: int, radius: int, color: Optional[Tuple[int, int, int]] = color.white):
        super().__init__(10)
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.radius = radius
        self.color = color




from __future__ import annotations

from typing import TYPE_CHECKING

import color
from random import randint

from entity import Actor

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine

class BaseAnimation:
    def __init__(self, frames: int = 0) -> None:
        self.frames = frames
    
    def anim_render(self, console: Console, engine: Engine) -> bool:
        """Return True if the current animation is complete."""
        return True

class AttackAnimation(BaseAnimation):
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
        """Render a particle coming out of the entity being hit and flying off in a random direction. Return True when the animation is complete."""

        x_offset = engine.viewport.x_offset
        y_offset = engine.viewport.y_offset

        if self.attacker_location == 'right':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset, string="-", fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset+1, string="/", fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset-1, string="\\", fg=[255, 0, 0])
        elif self.attacker_location == 'left':
            console.print(x=self.x+x_offset+1, y=self.y+y_offset, string="-", fg=[255, 0, 0])
            console.print(x=self.x+x_offset+1, y=self.y+y_offset-1, string="/", fg=[255, 0, 0])
            console.print(x=self.x+x_offset+1, y=self.y+y_offset+1, string="\\", fg=[255, 0, 0])
        elif self.attacker_location == 'below':
            console.print(x=self.x+x_offset, y=self.y+y_offset-1, string="|", fg=[255, 0, 0])
            console.print(x=self.x+1+x_offset, y=self.y+y_offset-1, string="/", fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset-1, string="\\", fg=[255, 0, 0])
        elif self.attacker_location == 'above':
            console.print(x=self.x+x_offset, y=self.y+y_offset+1, string="|", fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset+1, string="/", fg=[255, 0, 0])
            console.print(x=self.x+x_offset+1, y=self.y+y_offset+1, string="\\", fg=[255, 0, 0])
        elif self.attacker_location == 'below_right':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset, string="-", fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset-1, string="\\", fg=[255, 0, 0])
            console.print(x=self.x+x_offset, y=self.y+y_offset-1, string="|", fg=[255, 0, 0])
        elif self.attacker_location == 'above_right':
            console.print(x=self.x+x_offset-1, y=self.y+y_offset, string="-", fg=[255, 0, 0])
            console.print(x=self.x+x_offset-1, y=self.y+y_offset+1, string="/", fg=[255, 0, 0])
            console.print(x=self.x+x_offset, y=self.y+y_offset+1, string="|", fg=[255, 0, 0])
        elif self.attacker_location == 'below_left':
            console.print(x=self.x+1+x_offset, y=self.y+y_offset, string="-", fg=[255, 0, 0])
            console.print(x=self.x+1+x_offset, y=self.y+y_offset-1, string="/", fg=[255, 0, 0])
            console.print(x=self.x+x_offset, y=self.y+y_offset-1, string="|", fg=[255, 0, 0])
        elif self.attacker_location == 'above_left':
            console.print(x=self.x+x_offset+1, y=self.y+y_offset, string="-", fg=[255, 0, 0])
            console.print(x=self.x+x_offset+1, y=self.y+y_offset+1, string="\\", fg=[255, 0, 0])
            console.print(x=self.x+x_offset, y=self.y+y_offset+1, string="|", fg=[255, 0, 0])


        self.frames -= 1

        if self.frames == 0:
            return True
        else:
            return False




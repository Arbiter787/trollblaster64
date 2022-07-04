from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np # type: ignore
from tcod.console import Console
from game_map import GameMap
import math

import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class Viewport:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine
        self.game_map = engine.game_map

        self.x_offset = 0
        self.y_offset = 0

    def get_map_limits(self, level_size, drawing_size, centre):
        """
        Gets the dimensions and offset for the draw map function
        :param level_size: the size of the level
        :param drawing_size: the size of the window/region being drawn to
        :param centre: the coordinate that the window should be centred on
        :return: a tuple of (min, max, offset)
        """

        draw_min = 0
        draw_max = level_size
        draw_offset = 0

        if level_size <= drawing_size:
            draw_offset += (drawing_size - level_size) // 2
        else:
            if centre <= drawing_size // 2:
                draw_max = drawing_size
            elif centre >= level_size - (drawing_size // 2):
                draw_min = level_size - drawing_size
            else:
                draw_min = centre - (drawing_size // 2)
                draw_max = draw_min + drawing_size
            draw_offset -= draw_min
        return draw_min, draw_max, draw_offset

    def render(self, console: Console) -> None:
        """
        Renders the map.

        If a tile is a "visible" array, then draw it with the "light" colors.
        If it isn't, but it's in the "explored" array, draw it with the "dark" colors.
        Otherwise, the default is "SHROUD".
        """
        y_min, y_max, self.y_offset = self.get_map_limits(self.game_map.height, console.height-5, self.engine.player.y)
        x_min, x_max, self.x_offset = self.get_map_limits(self.game_map.width, console.width, self.engine.player.x)

        viewport_visible = self.game_map.visible[x_min:x_max, y_min:y_max]
        viewport_explored = self.game_map.explored[x_min:x_max, y_min:y_max]
        viewport_tiles = self.game_map.tiles[x_min:x_max, y_min:y_max]

        console_x_min = 0
        console_y_min = 0
        console_x_max = console.width
        console_y_max = console.height

        if self.game_map.width < console.width:
            console_x_min += self.x_offset
            console_x_max -= self.x_offset

            if console_x_max != self.game_map.width + self.x_offset:
                console_x_max -= 1
        
        if self.game_map.height < console.height:
            console_y_min += self.y_offset
            console_y_max -= self.y_offset

            if console_y_max != self.game_map.height + 5 + self.y_offset:
                console_y_max -= 1

        console.rgb[console_x_min : console_x_max, console_y_min : console_y_max-5] = np.select(
            condlist=[viewport_visible, viewport_explored],
            choicelist=[viewport_tiles["light"], viewport_tiles["dark"]],
            default=tile_types.SHROUD,
        )

        entities_sorted_for_rendering = sorted(
            self.game_map.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.game_map.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x + self.x_offset, y=entity.y + self.y_offset, string=entity.char, fg=entity.color
                )
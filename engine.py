from __future__ import annotations

import lzma
import pickle
from typing import TYPE_CHECKING, Optional, Tuple

from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
import render_functions

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap, GameWorld
    from animations import BaseAnimation
    from viewport import Viewport


class Engine:
    game_map: GameMap
    game_world: GameWorld
    viewport: Viewport

    def __init__(self, player: Actor):
        self.message_log = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player

    def handle_enemy_turns(self) -> list[BaseAnimation]:
        animations = []
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    # give each ai a number of moves according to its speed
                    if entity.speed >= 0:
                        for i in range(0, entity.speed + 1):
                            # get any animations caused by ai actions
                            new_animation = entity.ai.perform()
                            if new_animation is not None:
                                if len(new_animation) > 0:
                                    for i in new_animation:
                                        animations.append(i)
                    
                    # if ai is slow then potentially skip its turn
                    elif entity.speed < 0:
                        if entity.turn_skip < 0:
                            pass
                        elif entity.turn_skip >= 0:
                            new_animation = entity.ai.perform()
                            if new_animation is not None:
                                if len(new_animation) > 0:
                                    for i in new_animation:
                                        animations.append(i)
                            entity.reset_turn_skip()

                except exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.
        
        return animations

    def update_fov(self) -> None:
        """Recompute the visible area based on the player's point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, b_console: Console, i_console: Console, m_console: Console, ui_console: Console, render_center: Optional[Tuple[int, int]] = None) -> None:
        
        if render_center:
            self.viewport.render(b_console, i_console, m_console, render_center)
        else:
            self.viewport.render(b_console, i_console, m_console)

        render_functions.render_lower_bar(ui_console)

        self.message_log.render(console=ui_console, x=21, y=ui_console.height-5, width=40, height=5)

        render_functions.render_bar(
            console=ui_console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_dungeon_level(
            console=ui_console,
            dungeon_level=self.game_world.current_floor,
            location=(0, ui_console.height-2),
        )

        render_functions.render_names_at_mouse_location(
            console=ui_console, x=21, y=ui_console.height-6, engine=self
        )

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)

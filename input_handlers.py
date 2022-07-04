from __future__ import annotations
from hashlib import new

import os

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

import tcod.event
import traceback

import actions
import animations
from actions import (
    Action,
    BumpAction,
    PickupAction,
    WaitAction
)
import color
import exceptions
import setup_game
from equipment_types import EquipmentType

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
}

WAIT_KEYS = {
    tcod.event.K_PERIOD,
    tcod.event.K_KP_5,
    tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.K_RETURN,
    tcod.event.K_KP_ENTER,
}

CURSOR_Y_KEYS = {
    tcod.event.K_UP: -1,
    tcod.event.K_DOWN: 1,
    tcod.event.K_PAGEUP: -10,
    tcod.event.K_PAGEDOWN: 10,
}


ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned then it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: "tcod.event.Quit") -> Optional[Action]:
        raise SystemExit()


class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[BaseEventHandler]:
        """Any key returns to the parent event handler."""
        return self.parent


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine, animation: Optional[list[animations.BaseAnimation]] = []):
        self.engine = engine
        self.animation = animation

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine, self.animation)  # Return to the main handler.
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            new_animations = action.perform()

            # get any animations from the action and append them to queued animations
            if new_animations is not None:
                if len(new_animations) > 0:
                    for i in new_animations:
                        self.animation.append(i)

        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Skip enemy turn on exceptions.

        new_animations = self.engine.handle_enemy_turns()
        if len(new_animations) > 0:
            for i in new_animations:
                self.animation.append(i)

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x - self.engine.viewport.x_offset, event.tile.y - self.engine.viewport.y_offset):
            self.engine.mouse_location = event.tile.x - self.engine.viewport.x_offset, event.tile.y - self.engine.viewport.y_offset

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

        # check if any animations are queued to play
        if len(self.animation) > 0:
            for i in self.animation:
                done = i.anim_render(console, self.engine)
                if done:
                    self.animation.remove(i)  # when animations are done, remove them from queue


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.K_LSHIFT,
            tcod.event.K_RSHIFT,
            tcod.event.K_LCTRL,
            tcod.event.K_RCTRL,
            tcod.event.K_LALT,
            tcod.event.K_RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)


class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        y = 0

        width = len(self.TITLE) + 4

        if self.engine.player.x <= 30:
            x = console.width - width
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=12,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}"
        )
        console.print(
            x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}"
        )
        console.print(
            x=x + 1, y=y + 3, string=f"XP for next level: {self.engine.player.level.experience_to_next_level}"
        )

        console.print(
            x=x + 1, y=y + 5, string=f"To-hit: {self.engine.player.fighter.damage[0]}"
        )
        console.print(
            x=x + 1, y=y + 6, string=f"AC: {self.engine.player.fighter.ac}"
        )

        console.print(
            x=x + 1, y=y + 8, string=f"Str: {self.engine.player.fighter.str} (mod = {self.engine.player.fighter.str_mod})"
        )
        console.print(
            x=x + 1, y=y + 9, string=f"Dex: {self.engine.player.fighter.dex} (mod = {self.engine.player.fighter.dex_mod})"
        )
        console.print(
            x=x + 1, y=y + 10, string=f"Con: {self.engine.player.fighter.con} (mod = {self.engine.player.fighter.con_mod})"
        )


class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    # TODO: finish feats
    def get_available_feats(self, feat_type: str, level: int) -> list[str]:
        """Get the feats available for a specific category and level."""

        if feat_type == 'class_feat':
            player_class = self.engine.player.fighter.player_class.class_id

            if player_class == 'fighter':
                pass
    
    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        next_choice = self.engine.player.fighter.player_class.choice_reason[0]

        if self.engine.player.x <= 30:
            x = console.width - 35
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=6,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=1, string="Congratulations! You leveled up!")
        if next_choice == 'class_feat':
            console.print(x=x + 1, y=2, string="Select a class feat.")
        
        elif next_choice == 'skill_feat':
            console.print(x=x + 1, y=2, string="Select a skill feat.")
        
        elif next_choice == 'general_feat':
            console.print(x=x + 1, y=2, string="Select a general feat.")
        
        elif next_choice == 'ancestry_feat':
            console.print(x=x + 1, y=2, string="Select an ancestry feat.")
        
        elif next_choice == 'skill_increase':
            console.print(x=x + 1, y=2, string="Select a skill to increase.")
        
        elif next_choice == 'ability_boost':
            console.print(x=x + 1, y=2, string="Select an ability score to boost by 2.")
        
        elif next_choice == 'weapon_group':
            console.print(x=x + 1, y=2, string="Select a weapon group to specialize in.")

        console.print(
            x=x + 1,
            y=4,
            string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        #if 0 <= index <= 2:
        if index == 0:
            self.engine.player.level.increase_level()
            self.engine.player.fighter.heal(self.engine.player.fighter.player_class.hp_boost // self.engine.player.level.current_level)
            pass
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)
            return None

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """
        Don't allow the player to click to exit the menu, like normal.
        """
        return None


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then is up to the subclass.
    """

    TITLE = "<missing title>"

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.number_of_items_in_inventory = len(self.engine.player.inventory.items)
        
        self.max_name = 0
        for item in self.engine.player.inventory.items:
            if self.max_name < len(item.name):
                self.max_name = len(item.name)
        
        self.cursor = 0

    def on_render(self, console: tcod.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)

        height = self.number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        y = 0

        width = max(self.max_name + 4, len(self.TITLE) + 4)

        if self.engine.player.x <= 30:
            x = console.width - width
            info_side = "left"
        else:
            x = 0
            info_side = "right"

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        if self.number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)

                is_equipped = self.engine.player.equipment.item_is_equipped(item)

                item_string = f"({item_key}) {item.name}"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                if self.cursor == i:
                    console.print(x + 1, y + i + 1, item_string, fg=(0, 0, 0), bg=(255, 255, 255))
                    
                    # determine height of info window based on item
                    if item.equippable is not None:
                        if item.equippable.equipment_type == EquipmentType.WEAPON:
                            if item.equippable.equipment_traits is not None:
                                info_height = 6 + len(item.equippable.equipment_traits)
                            else:
                                info_height = 5
                        else:
                            info_height = 3
                    else:
                        info_height = 3

                    if item.desc_string is not None:
                        info_width = max(len(item.name), len(item.desc_string) + 2)
                    else:
                        info_width = max(len(item.name), 21)

                    # draw an information window for item stats
                    if info_side == "right":
                        console.draw_frame(
                            x=x+width,
                            y=y,
                            width=info_width,
                            height=info_height,
                            title=item.name,
                            clear=True,
                            fg=(255, 255, 255),
                            bg=(0, 0, 0),
                        )

                        if item.equippable is not None:
                            if item.equippable.equipment_type == EquipmentType.WEAPON:
                                console.print(x + width + 1, y + 1, f"Weapon Type: {item.equippable.equipment_category.value}")
                                console.print(x + width + 1, y + 2, f"Damage: {item.equippable.num_dice}d{item.equippable.die_size} + {self.engine.player.fighter.damage[3]}")
                                console.print(x + width + 1, y + 3, f"To Hit Bonus: {item.equippable.hit_bonus}")
                                if item.equippable.equipment_traits is not None:
                                    console.print(x + width + 1, y + 4, f"Traits:")
                                    trait_num = 1
                                    for trait in item.equippable.equipment_traits:
                                        console.print(x + width + 2, y + trait_num + 4, trait.value)
                                        trait_num += 1
                            elif item.equippable.equipment_type in [EquipmentType.CHEST, EquipmentType.SHIELD]:
                                console.print(x + width + 1, y + 1, f"AC Bonus: +{item.equippable.ac_bonus}")
                        else:
                            console.print(x + width + 1, y + 1, item.desc_string)
                    
                    elif info_side == "left":
                        console.draw_frame(
                            x=x-info_width,
                            y=y,
                            width=info_width,
                            height=info_height,
                            title=item.name,
                            clear=True,
                            fg=(255, 255, 255),
                            bg=(0, 0, 0),
                        )

                        if item.equippable is not None:
                            if item.equippable.equipment_type == EquipmentType.WEAPON:
                                console.print(x - info_width + 1, y + 1, f"Weapon Type: {item.equippable.equipment_category.value}")
                                console.print(x - info_width + 1, y + 2, f"Damage: {item.equippable.num_dice}d{item.equippable.die_size} + {self.engine.player.fighter.damage[3]}")
                                console.print(x - info_width + 1, y + 3, f"To Hit Bonus: {item.equippable.hit_bonus}")
                                if item.equippable.equipment_traits is not None:
                                    console.print(x - info_width + 1, y + 4, f"Traits:")
                                    trait_num = 1
                                    for trait in item.equippable.equipment_traits:
                                        console.print(x - info_width + 2, y + trait_num + 4, trait.value)
                                        trait_num += 1
                            elif item.equippable.equipment_type in [EquipmentType.CHEST, EquipmentType.SHIELD]:
                                console.print(x - info_width + 1, y + 1, f"AC Bonus: +{item.equippable.ac_bonus}")
                        else:
                            console.print(x - info_width + 1, y + 1, item.desc_string)
                
                else:
                    console.print(x + 1, y + i + 1, item_string)
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.K_a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)

        elif key in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.number_of_items_in_inventory - 1
            elif adjust > 0 and self.cursor == self.number_of_items_in_inventory - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the inventory.
                self.cursor = max(0, min(self.cursor + adjust, self.number_of_items_in_inventory - 1))
            return None

        elif key in CONFIRM_KEYS:
            selected_item = player.inventory.items[self.cursor]
            return self.on_item_selected(selected_item)

        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when user selects a valid item."""
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select an item to use."

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return actions.EquipAction(self.engine.player, item)
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select an item to drop."

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x+self.engine.viewport.x_offset, y+self.engine.viewport.y_offset] = color.white
        console.rgb["fg"][x+self.engine.viewport.x_offset, y+self.engine.viewport.y_offset] = color.black

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the viewport size.
            x = max(0 - self.engine.viewport.x_offset, min(x, self.engine.viewport.width - self.engine.viewport.x_offset - 1))
            y = max(0 - self.engine.viewport.y_offset, min(y, self.engine.viewport.height - self.engine.viewport.y_offset - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)

        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        
        x, y = event.tile

        mod_x = x - self.engine.viewport.x_offset
        mod_y = y - self.engine.viewport.y_offset

        if self.engine.game_map.in_bounds(mod_x, mod_y):
            if event.button == 1:
                return self.on_index_selected(mod_x, mod_y)
            return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x= x - self.radius - 1 + self.engine.viewport.x_offset,
            y=y - self.radius - 1 + self.engine.viewport.y_offset,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player

        if key == tcod.event.K_PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)

        elif key in WAIT_KEYS:
            action = WaitAction(player)

        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()

        elif key == tcod.event.K_v:
            return HistoryViewer(self.engine)

        elif key == tcod.event.K_g:
            action = PickupAction(player)

        elif key == tcod.event.K_i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.K_c:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            return LookHandler(self.engine)

        # No valid key was pressed.
        return action


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
        if event.sym == tcod.event.K_ESCAPE:
            self.on_quit()
        elif event.sym == tcod.event.K_n:
            return MainMenu()


class HistoryViewer(EventHandler):
    """Print the message history on a larger window which can be navigated."""
    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "-|Message History|-", alignment=tcod.CENTER
        )

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))

        elif event.sym == tcod.event.K_HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.K_END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None

class MainMenu(BaseEventHandler):
    """Handle the main menu rendering and input."""

    def on_render(self, console: tcod.console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(setup_game.background_image, 0, 0)

        console.print(
            console.width // 2,
            console. height // 2 - 4,
            "TrollBlaster 64",
            fg=color.menu_title,
            bg=color.black,
            alignment=tcod.CENTER,
            bg_blend=tcod.BKGND_ALPHA(64),
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Wmss",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_c:
            try:
                return MainGameEventHandler(setup_game.load_game("savegame.sav"))
            except FileNotFoundError:
                return PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.K_n:
            return MainGameEventHandler(setup_game.new_game())

        return None

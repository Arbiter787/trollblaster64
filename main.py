#!/usr/bin/env python3
import traceback

import tcod

import color
import exceptions
import input_handlers
import setup_game


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game Saved.")


def main() -> None:
    screen_width = 720
    screen_height = 480

    flags = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

    tileset = tcod.tileset.load_tilesheet(
        #"dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
        "Talryth_square_15x15.png",16 ,16, tcod.tileset.CHARMAP_CP437
    )

    handler: input_handlers.BaseEventHandler = input_handlers.MainMenu()

    with tcod.context.new(
        width=screen_width,
        height=screen_height,
        tileset=tileset,
        title="RL Project",
        vsync=True,
        sdl_window_flags=flags
    ) as context:
        try:
            while True:
                root_console = context.new_console(magnification=1, order="F")
                handler.on_render(console=root_console)
                context.present(root_console, integer_scaling=True)

                try:
                    for event in tcod.event.get():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit.
            save_game(handler, "savegame.sav")
            raise
        except BaseException:  # Save on any other unexpected exception.
            save_game(handler, "savegame.sav")
            raise


if __name__ == "__main__":
    main()

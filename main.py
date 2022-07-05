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
        while True:
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
            
            except SystemExit:  # Ask user for confirmation, then save and quit.
                
                # store the old input handler so it can be saved if necessary
                old_handler = handler

                # switch handler to the quit confirmation handler
                handler = input_handlers.QuitConfirm(handler, "Are you sure you want to quit?\nPress Esc to quit, any other key to cancel")
                
                # get user input and render until quit is confirmed/canceled (basically mini main loop)
                done = False
                while not done:
                    root_console = context.new_console(magnification=1, order="F")
                    handler.on_render(console=root_console)
                    context.present(root_console, integer_scaling=True)

                    for event in tcod.event.wait():
                        # only care about key events
                        if isinstance(event, tcod.event.KeyDown):
                            try:
                                # if key event doesn't quit the game, return to hold handler
                                context.convert_event(event)
                                handler = handler.handle_events(event)
                                done = True
                            except SystemExit:
                                # if key event raises SystemExit again, quit for real
                                save_game(old_handler, "savegame.sav")
                                raise 
                continue

            except BaseException:  # Save on any other unexpected exception.
                save_game(handler, "savegame.sav")
                raise
            
            break


if __name__ == "__main__":
    main()

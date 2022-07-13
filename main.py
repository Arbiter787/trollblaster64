#!/usr/bin/env python3
import traceback

import tcod
import tcod.render
import tcod.sdl.render
import tcod.sdl.video

import color
import exceptions
import input_handlers
import tilemaps


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """If the current event handler has an active Engine then save it."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game Saved.")

def render_context(
    context: tcod.context.Context, 
    console_render_tiles: tcod.render.SDLConsoleRender,
    console_render_text: tcod.render.SDLConsoleRender,
    handler: input_handlers.BaseEventHandler
) -> None:
    """Render the given context using the provided console render and input handler."""

    try:
        mag = handler.engine.magnification
    except AttributeError:
        mag = 2
    
    # console to render base map objects (background console)
    b_console = context.new_console(magnification=mag, order="F")

    # console to render items
    i_console = context.new_console(magnification=mag, order="F")
    i_console.rgba[:] = 0x20, (0, 0, 0, 0), (0, 0, 0, 0)

    # console to render actors (monster console)
    m_console = context.new_console(magnification=mag, order="F")
    m_console.rgba[:] = 0x20, (0, 0, 0, 0), (0, 0, 0, 0)

    # console to render animations
    a_console = context.new_console(magnification=mag, order="F")
    a_console.rgba[:] = 0x20, (0, 0, 0, 0), (0, 0, 0, 0)

    # console to render UI elements
    ui_console=context.new_console(magnification=0.5, order="F")
    ui_console.rgba[:] = 0x20, (0, 0, 0, 0), (0, 0, 0, 0)
    
    handler.on_render(b_console, i_console, m_console, a_console, ui_console)
    
    tex = console_render_tiles.render(b_console)
    tex.blend_mode = 1
    context.sdl_renderer.copy(tex)

    context.sdl_renderer.copy(console_render_tiles.render(i_console))
    context.sdl_renderer.copy(console_render_tiles.render(m_console))
    context.sdl_renderer.copy(console_render_tiles.render(a_console))
    
    tex = console_render_text.render(ui_console)
    tex.blend_mode = 1
    context.sdl_renderer.copy(tex)

    context.sdl_renderer.copy(console_render_text.render(ui_console))
    
    context.sdl_renderer.present()

def main() -> None:
    screen_width = 720
    screen_height = 480

    flags = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED

    tileset = tcod.tileset.load_tilesheet(
        #"dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
        "Talryth_square_15x15.png",16 ,16, tcod.tileset.CHARMAP_CP437
    )

    tileset_gfx = tcod.tileset.load_tilesheet(
        "wmss_32x32.png", 10, 10, tilemaps.main_tilemap
    )

    handler: input_handlers.BaseEventHandler = input_handlers.MainMenu()
    
    with tcod.context.new(
        width=screen_width,
        height=screen_height,
        tileset=tileset_gfx,
        title="Trollblaster 64 Context",
        vsync=True,
        sdl_window_flags=flags
    ) as context:

        # sdl_renderer = tcod.sdl.render.new_renderer(context.sdl_window, target_textures=True, vsync=True)
        atlas = tcod.render.SDLTilesetAtlas(context.sdl_renderer, tileset)
        atlas_tiles = tcod.render.SDLTilesetAtlas(context.sdl_renderer, tileset_gfx)
        console_render_tiles = tcod.render.SDLConsoleRender(atlas_tiles)
        console_render_text = tcod.render.SDLConsoleRender(atlas)

        context.sdl_renderer.integer_scaling = True

        while True:
            try:
                while True:
                    context.sdl_renderer.draw_blend_mode = 1
                    render_context(context, console_render_tiles, console_render_text, handler)
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
                    render_context(context, console_render_tiles, console_render_text, handler)
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

from typing import Tuple

import numpy as np #type: ignore

# Tile graphics structure type compatible with Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "4B"),  # 4 unsigned bytes, for RGBA colors.
        ("bg", "4B"),
    ]
)

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", graphic_dt),  # Graphics for when this tile is not in FOV.
        ("light", graphic_dt),  # Graphics for when this tile is in FOV.
    ]
)

def new_tile(
    *,  # Enforce the use of keywords
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int, int], Tuple[int, int, int, int]],
    light: Tuple[int, Tuple[int, int, int, int], Tuple[int, int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)

# SHROUD represents unexplored, unseen tiles.
SHROUD = np.array((ord(" "), (255, 255, 255, 255), (0, 0, 0, 255)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(0xE001, (255, 255, 255, 255), (0, 0, 0, 255)),
    light=(0xE000, (255, 255, 255, 255), (0, 0, 0, 255)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(0xE003, (255, 255, 255, 255), (0, 0, 0, 255)),
    light=(0xE002, (255, 255, 255, 255), (0, 0, 0, 255)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(0xE005, (255, 255, 255, 255), (0, 0, 0, 255)),
    light=(0xE004, (255, 255, 255, 255), (0, 0, 0, 255)),
)
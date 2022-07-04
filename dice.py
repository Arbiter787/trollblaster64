from __future__ import annotations

from random import randint

def dice_roller(num_dice: int, dice_size: int) -> int:
    """Rolls a number of dice of a specified size and returns the total result."""
    total = 0
    for i in range(num_dice):
        total += randint(1, dice_size)
    return total
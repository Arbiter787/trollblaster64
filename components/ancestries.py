from __future__ import annotations
from lib2to3.pytree import Base

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from fighter import BaseStats

# TODO: Finish ancestry support and ready player customization
class BaseAncestry(BaseComponent):
    parent: BaseStats

    def __init__(
        self,
        str_boost: int = 0,
        dex_boost: int = 0,
        con_boost: int = 0,
        int_boost: int = 0,
        wis_boost: int = 0,
        cha_boost: int = 0,
        speed: int = 0,
        size: int = 0,
        hp_boost: int = 8,
        traits: list[str] = [''],
        senses: list[str] = [''],
    ):
        self.str_boost = str_boost
        self.dex_boost = dex_boost
        self.con_boost = con_boost
        self.int_boost = int_boost
        self.wis_boost = wis_boost
        self.cha_boost = cha_boost
        
        self.speed = speed
        self.size = size
        self.hp_boost = hp_boost
        self.traits = traits
        self.senses = senses 
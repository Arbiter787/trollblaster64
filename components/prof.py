from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from fighter import Player


class Proficiencies(BaseComponent):
    parent: Player

    def __init__(
        self,
        prof_unarmed: int= 0,
        prof_martial: int = 0,
        prof_simple: int = 0,
        prof_advanced: int = 0,
        prof_traits: list[int] = [],

        prof_unarmored: int = 0,
        prof_light: int = 0,
        prof_med: int = 0,
        prof_heavy: int = 0,
        
        prof_perception: int = 0,
        prof_acrobatics: int = 0,
        prof_arcana: int = 0,
        prof_athletics: int = 0,
        prof_intimidation: int = 0,
        prof_medicine: int = 0,
        prof_nature: int = 0,
        prof_occultism: int = 0,
        prof_performance: int = 0,
        prof_religion: int = 0,
        prof_stealth: int = 0,
    ) -> None:
        
        self._prof_unarmed = prof_unarmed
        self._prof_martial = prof_martial
        self._prof_simple = prof_simple
        self._prof_advanced = prof_advanced
        self._prof_traits = prof_traits

        self._prof_unarmored = prof_unarmored
        self._prof_light = prof_light
        self._prof_med = prof_med
        self._prof_heavy = prof_heavy
        
        self._prof_perception = prof_perception

        self._prof_acrobatics = prof_acrobatics
        self._prof_arcana = prof_arcana
        self._prof_athletics = prof_athletics
        self._prof_intimidation = prof_intimidation
        self._prof_medicine = prof_medicine
        self._prof_nature = prof_nature
        self._prof_occultism = prof_occultism
        self._prof_performance = prof_performance
        self._prof_religion = prof_religion
        self._prof_stealth = prof_stealth
    
    @property
    def prof_unarmed(self):
        return max(self.parent.player_class.weapon_prof[0], self._prof_unarmed)
    
    @property
    def prof_simple(self):
        return max(self.parent.player_class.weapon_prof[1], self._prof_simple)
    
    @property
    def prof_martial(self):
        return max(self.parent.player_class.weapon_prof[2], self._prof_martial)
    
    @property
    def prof_advanced(self):
        return max(self.parent.player_class.weapon_prof[3], self._prof_advanced)

    @property
    def prof_unarmored(self):
        return max(self.parent.player_class.armor_prof[0], self._prof_unarmored)
    
    @property
    def prof_light(self):
        return max(self.parent.player_class.armor_prof[1], self._prof_light)
    
    @property
    def prof_med(self):
        return max(self.parent.player_class.armor_prof[2], self._prof_med)
    
    @property
    def prof_heavy(self):
        return max(self.parent.player_class.armor_prof[3], self._prof_heavy)

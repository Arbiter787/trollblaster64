from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
    from fighter import Player

# TODO: Finish class support and ready player customization
class BaseClass(BaseComponent):
    parent: Player

    def __init__(
        self,
        hp_boost: int = 10,
        perception_prof: int = 0,
        fort_prof: int = 0,
        refl_prof: int = 0,
        will_prof: int = 0,
        weapon_prof: tuple[int, int, int, int] = [0, 0, 0, 0],  # [unarmed, simple, martial, advanced]
        armor_prof: tuple[int, int, int, int] = [0, 0, 0, 0],  # [unarmored, light, medium, heavy]
        skill_prof: tuple[int, int, int, int, int, int, int, int, int, int] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        class_prof: int = 2,
        class_id: str = 'null',
    ):
        self._hp_boost = hp_boost
        self.perception_prof = perception_prof
        self.fort_prof = fort_prof
        self.refl_prof = refl_prof
        self.will_prof = will_prof
        self.weapon_prof = weapon_prof
        self.armor_prof = armor_prof
        self.skill_prof = skill_prof
        self.class_prof = class_prof

        self.need_player_choice = False
        self.choice_reason = []

        self.class_id = class_id

    @property
    def attacks_per_round(self) -> int:
        """Each character gets 1 extra attack for every five levels, plus any extra attacks from their weapons."""
        return (1 + (self.parent.parent.level.current_level // 5)) + self.parent.parent.equipment.extra_attacks
    
    @property
    def hp_boost(self) -> int:
        return (self._hp_boost + self.parent.con_mod) * self.parent.parent.level.current_level
    
    def on_level_up(self, level: int) -> None:
        """Implements what happens when a class levels up."""
        raise NotImplementedError()
    

class Fighter(BaseClass):
    def __init__(self):
        super().__init__(
            hp_boost=10, 
            perception_prof=4, 
            fort_prof=4, 
            refl_prof=4, 
            will_prof=2, 
            weapon_prof=[4, 4, 4, 2], 
            armor_prof=[2, 2, 2, 2], 
            skill_prof=[0, 0, 2, 0, 0, 0, 0, 0, 0, 0], 
            class_prof=2,
            class_id='fighter',
        )

    
    @property
    def class_damage_bonus(self) -> int:
        if self.parent.parent.level.current_level >= 7 and self.parent.parent.level.current_level < 15:
            if self.parent.parent.equipment.weapon_prof_bonus == 4:
                return 2
            elif self.parent.parent.equipment.weapon_prof_bonus == 6:
                return 3
            elif self.parent.parent.equipment.weapon_prof_bonus == 8:
                return 4
        elif self.parent.parent.level.current_level >= 15:
            if self.parent.parent.equipment.weapon_prof_bonus == 4:
                return 4
            elif self.parent.parent.equipment.weapon_prof_bonus == 6:
                return 6
            elif self.parent.parent.equipment.weapon_prof_bonus == 8:
                return 8
        return 0


    def on_level_up(self, level: int):
        if level % 2 == 0:
            self.need_player_choice = True
            self.choice_reason.append('class_feat')
            self.choice_reason.append('skill_feat')
        
        if level == 3:
            self.will_prof = 4
        
        if level in [3, 7, 11, 15, 19]:
            self.need_player_choice = True
            self.choice_reason.append('general_feat')
        
        if level % 2 != 0:
            self.need_player_choice = True
            self.choice_reason.append('skill_increase')
        
        if level % 5 == 0:
            self.need_player_choice = True
            self.choice_reason.append('ability_boost')
        
        if level in [5, 9, 13, 17]:
            self.need_player_choice = True
            self.choice_reason.append('ancestry_feat')
        
        if level == 5:
            self.need_player_choice = True
            self.choice_reason.append('weapon_group')

        if level == 7:
            self.perception_prof = 6
        
        if level == 9:
            self.will_prof = 6
        
        if level == 11:
            self.armor_prof = [4, 4, 4, 4]
            self.class_prof = 4
        
        if level == 13:
            self.need_player_choice = True
            self.choice_reason.append('weapon_group')
            self.weapon_prof = [6, 6, 6, 4]
        
        if level == 15:
            self.refl_prof = 6

        if level == 17:
            self.armor_prof = [6, 6, 6, 6]
        
        if level == 19:
            self.weapon_prof = [8, 8, 8, 6]
            self.class_prof = 6
            


    

from __future__ import annotations
from lib2to3.pytree import Base

from typing import TYPE_CHECKING

import color
from components.base_component import BaseComponent
from components.prof import Proficiencies
from equipment_types import EquipmentTraits
from render_order import RenderOrder
from dice import dice_roller

from components.ancestries import BaseAncestry
from components.classes import BaseClass



if TYPE_CHECKING:
    from entity import Actor


class BaseStats(BaseComponent):
    parent: Actor

    def __init__(self, hp: int = 5) -> None:
        self._hp = hp
        self.max_hp = hp
    
    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))  # Clamp hp between 0 and the max_hp.
        if self.hp == 0 and self.parent.ai:
            self.die()
    
    def die(self) -> None:
        """Kills the actor and turns it into a corpse."""
        player_dead = False
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = color.player_die
            player_dead = True
        else:
            death_message = f"{self.parent.name} falls over dead!"
            death_message_color = color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

        if player_dead == False:
            level_diff = ((self.engine.player.level.current_level - self.parent.level.current_level) * -1)
            if level_diff < 0:
                xp = (100 // (level_diff * 1.5)) * -1
            elif level_diff == 0:
                xp = 100
            elif level_diff > 0:
                xp = (100 * (level_diff * 1.5))
            self.engine.player.level.add_xp(xp)

    def heal(self, amount: int) -> int:
        """Heals the actor for 'amount', and returns the amount healed."""
        if self.hp == self.max_hp:  # If hp is already at max, stop and return 0
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:  # If hp would be above max after heal, clamp to max
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        """Causes the actor to take 'amount' damage directly to HP."""
        self.hp -= amount


class Player(BaseStats):
    parent: Actor

    def __init__(
        self, 
        str: int = 16, 
        dex: int = 14, 
        con: int = 14, 
        int: int = 10, 
        wis: int = 10, 
        cha: int = 10, 
        ancestry: BaseAncestry = BaseAncestry(),
        player_class: BaseClass = BaseClass(),
        proficiencies: Proficiencies = Proficiencies(),
    ) -> None:

        self.ancestry = ancestry
        self.ancestry.parent = self

        self.player_class = player_class
        self.player_class.parent = self

        self.proficiencies = proficiencies
        self.proficiencies.parent = self

        self.str = str + self.ancestry.str_boost
        self.dex = dex + self.ancestry.dex_boost
        self.con = con + self.ancestry.con_boost
        self.int = int + self.ancestry.int_boost
        self.wis = wis + self.ancestry.wis_boost
        self.cha = cha + self.ancestry.cha_boost

        self._hp = 5

    @property
    def attacks_per_round(self) -> int:
        return self.player_class.attacks_per_round

    @property
    def max_hp(self) -> int:
        return self.ancestry.hp_boost + self.player_class.hp_boost

    @property
    def str_mod(self) -> int:
        return (self.str-10)//2
    
    @property
    def dex_mod(self) -> int:
        return (self.dex-10)//2

    @property
    def con_mod(self) -> int:
        return (self.con-10)//2
    
    @property
    def int_mod(self) -> int:
        return (self.int-10)//2

    @property
    def wis_mod(self) -> int:
        return (self.wis-10)//2
    
    @property
    def cha_mod(self) -> int:
        return (self.cha-10)//2

    # TODO: prof bonuses
    @property
    def ac(self) -> int:
        return 10 + self.dex_mod + self.ac_bonus

    @property
    def ac_bonus(self) -> int:
        if self.parent.equipment:
            return self.parent.equipment.ac_bonus
        else:
            return self.proficiencies.prof_unarmored

    @property
    def damage(self) -> tuple[int, int, int, int, list[EquipmentTraits], tuple[int, int]]:
        if self.parent.equipment.weapon is not None:
            num_dice = self.parent.equipment.damage[0]
            die_size = self.parent.equipment.damage[1]
            dam_bonus = self.parent.equipment.damage[2] + self.str_mod
            to_hit = self.str_mod + self.parent.equipment.weapon_prof_bonus
            attack_traits = self.parent.equipment.weapon.equippable.equipment_traits
            crit_bonus = self.parent.equipment.weapon.equippable.crit_bonus
        else:
            num_dice = 1
            die_size = 4
            dam_bonus = self.str_mod
            to_hit = self.str_mod + self.proficiencies.prof_unarmed
            attack_traits = [EquipmentTraits.AGILE]
            crit_bonus = None
        
        return to_hit, num_dice, die_size, dam_bonus, attack_traits, crit_bonus
    
    @property
    def speed(self) -> int:
        return self.ancestry.speed


class Monster(BaseStats):
    parent: Actor

    def __init__(
        self,
        str_mod: int = 0, 
        dex_mod: int = 0, 
        con_mod: int = 0, 
        int_mod: int = 0, 
        wis_mod: int = 0, 
        cha_mod: int = 0,
        max_hp: int = 10,
        ac: int = 10,
        speed: int = 0,
        fort: int = 0,
        refl: int = 0,
        will: int = 0,
        attacks: list[tuple[int, int, int, int, list[EquipmentTraits]]] = [[0, 1, 4, 0, None]],  # [to hit, num dice, dice size, damage modifier, attack traits]
        attacks_per_round: int = 1,
        crit_bonus: list[tuple[int, int]] = None,  # bonus added with traits such as fatal and deadly - [num dice, dice size], in attack order
    ):

        self.str_mod = str_mod
        self.dex_mod = dex_mod
        self.con_mod = con_mod
        self.int_mod = int_mod
        self.wis_mod = wis_mod
        self.cha_mod = cha_mod

        self.max_hp = max_hp
        self._hp = max_hp

        self.ac = ac
        self.speed = speed

        self.fort = fort
        self.refl = refl
        self.will = will

        self.attacks = attacks
        self.attacks_per_round = attacks_per_round
        self.crit_bonus = crit_bonus
    
    @property
    def damage(self) -> tuple[int, int, int, int, list[EquipmentTraits], tuple[int, int]]:
        choice = dice_roller(1, len(self.attacks))
        to_hit, num_dice, die_size, dam_bonus, attack_traits = self.attacks[choice - 1]
        if self.crit_bonus is not None:
            return to_hit, num_dice, die_size, dam_bonus, attack_traits, self.crit_bonus[choice - 1]
        else:
            return to_hit, num_dice, die_size, dam_bonus, attack_traits, self.crit_bonus

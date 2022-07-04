from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Optional

from components.base_component import BaseComponent
from equipment_types import EquipmentCategory, EquipmentTraits, EquipmentType

if TYPE_CHECKING:
    from entity import Item


class Equippable(BaseComponent):
    parent: Item

    def __init__(
        self,
        equipment_type: EquipmentType,
        equipment_category: Optional[EquipmentCategory] = None,
        equipment_traits: Optional[list[EquipmentTraits]] = None,
        damage_bonus: int = 0,
        ac_bonus: int = 0,
        num_dice: int = 1,
        die_size: int = 4,
        hit_bonus: int = 0,
        extra_attacks: int = 0,
        crit_bonus: Optional[tuple[int, int]] = None,  # die amount, die size
        reach: int = 0,
    ):
        self.equipment_type = equipment_type
        self.equipment_category = equipment_category
        self.equipment_traits = equipment_traits
        self.damage_bonus = damage_bonus
        self.ac_bonus = ac_bonus

        self.num_dice = num_dice
        self.die_size = die_size
        self.hit_bonus = hit_bonus
        self.extra_attacks = extra_attacks
        self.crit_bonus = crit_bonus

        self.reach = reach

        if equipment_traits is not None:
            for i in equipment_traits:
                if i == EquipmentTraits.AGILE:
                    self.extra_attacks += 1
                elif i == EquipmentTraits.PARRY:
                    self.ac_bonus += 1
                elif i == EquipmentTraits.REACH:
                    self.reach = 5

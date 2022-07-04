from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from components.base_component import BaseComponent
from dice import dice_roller
from equipment_types import EquipmentCategory, EquipmentType

if TYPE_CHECKING:
    from entity import Actor, Item


class Equipment(BaseComponent):
    parent: Actor

    def __init__(
        self,
        weapon: Optional[Item] = None,
        shield: Optional[Item] = None,
        chest: Optional[Item] = None,
        head: Optional[Item] = None,
        legs: Optional[Item] = None,
        hands: Optional[Item] = None,
        feet: Optional[Item] = None,
    ):
        self.weapon = weapon
        self.shield = shield
        self.chest = chest
        self.head = head
        self.legs = legs
        self.hands = hands
        self.feet = feet

    @property
    def slots(self) -> list[Tuple[str, Item]]:
        slots = [
            ("weapon", self.weapon),
            ("shield", self.shield),
            ("chest", self.chest),
            ("head", self.head),
            ("legs", self.legs),
            ("hands", self.hands),
            ("feet", self.feet),
        ]
        return slots

    @property
    def ac_bonus(self) -> int:
        bonus = 0

        for i in self.slots:  # Iterate through the list of slots and add each bonus
            slot, item = i
            if item is not None and item.equippable is not None:
                bonus += item.equippable.ac_bonus
        
        try:
            if self.chest.equippable.equipment_category == EquipmentCategory.UNARMORED:
                prof_bonus = self.parent.fighter.proficiencies.prof_unarmored
            elif self.chest.equippable.equipment_category == EquipmentCategory.LIGHT:
                prof_bonus = self.parent.fighter.proficiencies.prof_light
            elif self.chest.equippable.equipment_category == EquipmentCategory.MEDIUM:
                prof_bonus = self.parent.fighter.proficiencies.prof_med
            elif self.chest.equippable.equipment_category == EquipmentCategory.HEAVY:
                prof_bonus = self.parent.fighter.proficiencies.prof_heavy
        except AttributeError:
            prof_bonus = self.parent.fighter.proficiences.prof_unarmored

        return bonus + prof_bonus
    
    @property
    def damage(self) -> int:
        try: 
            bonus = self.parent.fighter.player_class.class_damage_bonus
        except AttributeError:
            bonus = 0
        return self.weapon.equippable.num_dice, self.weapon.equippable.die_size, self.weapon.equippable.damage_bonus + bonus
    
    @property
    def weapon_prof_bonus(self) -> int:
        
        bonus = 0
        for i in self.slots:  # Iterate through the list of slots and add each bonus
            slot, item = i
            if item is not None and item.equippable is not None:
                bonus += item.equippable.hit_bonus
        
        try:
            if self.weapon.equippable.equipment_category == EquipmentCategory.SIMPLE:
                prof_bonus = self.parent.fighter.proficiencies.prof_simple
            elif self.weapon.equippable.equipment_category == EquipmentCategory.MARTIAL:
                prof_bonus = self.parent.fighter.proficiencies.prof_martial
            elif self.weapon.equippable.equipment_category == EquipmentCategory.ADVANCED:
                prof_bonus = self.parent.fighter.proficiencies.prof_advanced
        except AttributeError:
            prof_bonus = self.parent.fighter.proficiencies.prof_unarmed
        
        return prof_bonus + bonus

    @property
    def extra_attacks(self) -> int:
        bonus = 0
        for i in self.slots:  # Iterate through the list of slots and add each bonus
            slot, item = i
            if item is not None and item.equippable is not None:
                bonus += item.equippable.extra_attacks
        
        return bonus

    def item_is_equipped(self, item: Item) -> bool:
        for i in self.slots:
            slot, slot_item = i
            if slot_item == item:
                return True
        return False

    def unequip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You remove the {item_name}."
        )

    def equip_message(self, item_name: str) -> None:
        self.parent.gamemap.engine.message_log.add_message(
            f"You equip the {item_name}."
        )

    def equip_to_slot(self, slot: str, item: Item, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if current_item is not None:
            self.unequip_from_slot(slot, add_message)

        setattr(self, slot, item)

        if add_message:
            self.equip_message(item.name)

    def unequip_from_slot(self, slot: str, add_message: bool) -> None:
        current_item = getattr(self, slot)

        if add_message:
            self.unequip_message(current_item.name)

        setattr(self, slot, None)

    def toggle_equip(self, equippable_item: Item, add_message: bool = True) -> None:
        if equippable_item.equippable:
            if equippable_item.equippable.equipment_type == EquipmentType.WEAPON:
                slot = "weapon"
            elif equippable_item.equippable.equipment_type == EquipmentType.SHIELD:
                slot = "shield"
            elif equippable_item.equippable.equipment_type == EquipmentType.CHEST:
                slot = "chest"
            elif equippable_item.equippable.equipment_type == EquipmentType.HEAD:
                slot = "head"
            elif equippable_item.equippable.equipment_type == EquipmentType.LEGS:
                slot = "legs"
            elif equippable_item.equippable.equipment_type == EquipmentType.HANDS:
                slot = "hands"
            else:
                slot = "feet"

            if getattr(self, slot) == equippable_item:
                self.unequip_from_slot(slot, add_message)
            else:
                self.equip_to_slot(slot, equippable_item, add_message)

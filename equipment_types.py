from enum import auto, Enum


class EquipmentType(Enum):
    WEAPON = auto()
    SHIELD = auto()
    CHEST = auto()
    HEAD = auto()
    LEGS = auto()
    HANDS = auto()
    FEET = auto()

class EquipmentCategory(Enum):
    SIMPLE = auto()
    MARTIAL = auto()
    ADVANCED = auto()
    UNARMORED = auto()
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()

class EquipmentTraits(Enum):
    AGILE = auto()
    BACKSWING = auto()
    DEADLY = auto()
    DISARM = auto()
    FATAL = auto()
    FINESSE = auto()
    FORCEFUL = auto()
    GRAPPLE = auto()
    PARRY = auto()
    REACH = auto()
    SHOVE = auto()
    SWEEP = auto()
    THROWN = auto()
    TRIP = auto()
    TWO_HAND = auto()
    VERSATILE_B = auto()
    VERSATILE_P = auto()
    VERSATILE_S = auto()
    VOLLEY = auto()





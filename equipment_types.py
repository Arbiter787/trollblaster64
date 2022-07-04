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
    SIMPLE = "Simple"
    MARTIAL = "Martial"
    ADVANCED = "Advanced"
    UNARMORED = "Unarmored"
    LIGHT = "Light"
    MEDIUM = "Medium"
    HEAVY = "Heavy"

class EquipmentTraits(Enum):
    AGILE = "Agile"
    BACKSWING = "Backswing"
    DEADLY = "Deadly"
    DISARM = "Disarm"
    FATAL = "Fatal"
    FINESSE = "Finesse"
    FORCEFUL = "Forceful"
    GRAPPLE = "Grapple"
    PARRY = "Parry"
    REACH = "Reach"
    SHOVE = "Shove"
    SWEEP = "Sweep"
    THROWN = "Thrown"
    TRIP = "Trip"
    TWO_HAND = "Two Hand"
    VERSATILE_B = "Versatile B"
    VERSATILE_P = "Versatile P"
    VERSATILE_S = "Versatile S"
    VOLLEY = "Volley"





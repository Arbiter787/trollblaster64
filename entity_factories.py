from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.equippable import Equippable
from equipment_types import EquipmentCategory, EquipmentTraits, EquipmentType
from components.fighter import Monster, Player
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item
import components.classes

# PLAYER
player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Player(
        player_class=components.classes.Fighter(),
    ),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=250),
)

# ENEMIES
goblin = Actor(
    char="g",
    color=(63, 127, 63),
    name="Goblin",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Monster(
        str_mod=0,
        dex_mod=3,
        con_mod=1,
        int_mod=0,
        wis_mod=-1,
        cha_mod=1,
        max_hp=6,
        ac=16,
        speed=0,
        fort=5,
        refl=7,
        will=3,
        attacks=[[8, 1, 6, 0, [EquipmentTraits.AGILE, EquipmentTraits.FINESSE]]],
        attacks_per_round=2,
    ),
    inventory=Inventory(capacity=0),
    level=Level(current_level=-1),
)
orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Monster(
        str_mod=3,
        dex_mod=2,
        con_mod=3,
        int_mod=-1,
        wis_mod=1,
        cha_mod=0,
        max_hp=15,
        ac=15,
        speed=0,
        fort=6,
        refl=4,
        will=2,
        attacks=[[7, 1, 6, 3, [EquipmentTraits.AGILE, EquipmentTraits.DISARM]], [7, 1, 4, 3, [EquipmentTraits.AGILE]]],
        attacks_per_round=2,
    ),
    inventory=Inventory(capacity=0),
    level=Level(current_level=0),
)
troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Monster(
        str_mod=5,
        dex_mod=2,
        con_mod=6,
        int_mod=-2,
        wis_mod=0,
        cha_mod=-2,
        max_hp=115,
        ac=15,
        speed=0,
        fort=12,
        refl=6,
        will=2,
        attacks=[[8, 2, 10, 5, [EquipmentTraits.REACH]], [8, 2, 8, 5, [EquipmentTraits.AGILE, EquipmentTraits.REACH]]],
        attacks_per_round=2,
    ),
    inventory=Inventory(capacity=0),
    level=Level(current_level=5),
)
ogre = Actor(
    char="O",
    color=(0, 82, 0),
    name="Ogre",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Monster(
        str_mod=5,
        dex_mod=-1,
        con_mod=4,
        int_mod=-2,
        wis_mod=0,
        cha_mod=-2,
        max_hp=50,
        ac=14,
        speed=0,
        fort=8,
        refl=3,
        will=2,
        attacks=[[9, 1, 10, 7, [EquipmentTraits.DEADLY, EquipmentTraits.REACH, EquipmentTraits.TRIP]]],
        crit_bonus=[[1, 10]]
    ),
    inventory=Inventory(capacity=0),
    level=Level(current_level=3),
)

# CONSUMABLES
confusion_scroll = Item(
    char="~",
    color=(207, 63, 255),
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=5),
)
fireball_scroll = Item(
    char="~",
    color=(255, 0, 0),
    name="Fireball Scroll",
    consumable=consumable.FireballDamageConsumable(damage=12, radius=3),
)
health_kit = Item(
    char="+",
    color=(127, 0, 255),
    name="Health Kit",
    consumable=consumable.HealingConsumable(amount=10),
)
lightning_scroll = Item(
    char="~",
    color=(0, 255, 255),
    name="Lightning Scroll",
    consumable=consumable.LightningDamageConsumable(damage=10, maximum_range=5),
)

# WEAPONS
dagger = Item(
    char="/",
    color=(0, 191, 255),
    name="Dagger",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.SIMPLE,
        equipment_traits=[EquipmentTraits.AGILE, EquipmentTraits.FINESSE, EquipmentTraits.THROWN, EquipmentTraits.VERSATILE_P],
        num_dice=1,
        die_size=4,
    )
)
sword = Item(
    char="/",
    color=(0, 191, 255),
    name="Shortsword",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.MARTIAL,
        equipment_traits=[EquipmentTraits.AGILE, EquipmentTraits.FINESSE, EquipmentTraits.VERSATILE_S],
        num_dice=1,
        die_size=6,
    )
)
axe = Item(
    char="/",
    color=(0, 191, 255),
    name="Battle axe",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.MARTIAL,
        equipment_traits=[EquipmentTraits.SWEEP],
        num_dice=1,
        die_size=8,
    )
)

# SHIELDS
wood_shield = Item(
    char=")",
    color=(107, 94, 56),
    name="Wooden Shield",
    equippable=Equippable(
        equipment_type=EquipmentType.SHIELD,
        ac_bonus=1,
    )
)
iron_shield = Item(
    char=")",
    color=(120, 120, 120),
    name="Iron Shield",
    equippable=Equippable(
        equipment_type=EquipmentType.SHIELD,
        ac_bonus=2,
    )
)

# CHEST ARMOR
leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=Equippable(
        equipment_type=EquipmentType.CHEST,
        equipment_category=EquipmentCategory.LIGHT,
        ac_bonus=1,
    )
)
chain_mail = Item(
    char="[",
    color=(120, 120, 120),
    name="Chain Mail",
    equippable=Equippable(
        equipment_type=EquipmentType.CHEST,
        equipment_category=EquipmentCategory.MEDIUM,
        ac_bonus=4,
    )
)

# HELMETS


# LEGGINGS


# GLOVES


# BOOTS


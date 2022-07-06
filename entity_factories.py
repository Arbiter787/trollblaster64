from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.equippable import Equippable
from equipment_types import EquipmentCategory, EquipmentTraits, EquipmentType
from components.fighter import Monster, Player
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item
import color
import components.classes

# PLAYER
player = Actor(
    char="@",
    color=color.white,
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
    color=color.purple,
    name="Confusion Scroll",
    consumable=consumable.ConfusionConsumable(number_of_turns=5, animation=True, color=color.purple),
    desc_string="Confuses an enemy for 5 turns"
)
fireball_scroll = Item(
    char="~",
    color=color.red,
    name="Fireball Scroll",
    consumable=consumable.RadiusDamageConsumable(num_dice=6, die_size=6, radius=3),
    desc_string="Deals 6d6 damage in a radius"
)
health_kit = Item(
    char="+",
    color=color.purple,
    name="Health Kit",
    consumable=consumable.HealingConsumable(amount=20),
    desc_string="Heals for 20 HP"
)
lightning_scroll = Item(
    char="~",
    color=color.yellow,
    name="Lightning Scroll",
    consumable=consumable.SingleTargetDamageConsumable(num_dice=4, die_size=12, maximum_range=5, animation=True, color=color.light_blue),
    desc_string="Deals 4d12 damage to nearby enemy"
)
teleport_scroll = Item(
    char="~",
    color=color.grey,
    name="Teleportation Scroll",
    consumable=consumable.TeleportConsumable(maximum_range=50),
    desc_string="Teleports you randomly"
)
throwing_star = Item(
    char="x",
    color=color.grey,
    name="Throwing Star",
    consumable=consumable.ProjectileConsumable(1, 6, True, color.grey),
    desc_string="Can be thrown at an enemy"
)


# WEAPONS
dagger = Item(
    char="/",
    color=color.grey,
    name="Dagger",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.SIMPLE,
        equipment_traits=[EquipmentTraits.AGILE, EquipmentTraits.FINESSE, EquipmentTraits.THROWN, EquipmentTraits.VERSATILE_P],
        num_dice=1,
        die_size=4,
        base_name="Dagger",
    )
)
shortsword = Item(
    char="/",
    color=color.grey,
    name="Shortsword",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.MARTIAL,
        equipment_traits=[EquipmentTraits.AGILE, EquipmentTraits.FINESSE, EquipmentTraits.VERSATILE_S],
        num_dice=1,
        die_size=6,
        base_name="Shortsword",
    )
)
longsword = Item(
    char="/",
    color=color.grey,
    name="Longsword",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.MARTIAL,
        equipment_traits=[EquipmentTraits.VERSATILE_P],
        num_dice=1,
        die_size=8,
        base_name="Longsword",
    )
)
rapier = Item(
    char="/",
    color=color.grey,
    name="Rapier",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.MARTIAL,
        equipment_traits=[EquipmentTraits.DEADLY, EquipmentTraits.DISARM, EquipmentTraits.FINESSE],
        num_dice=1,
        die_size=6,
        crit_bonus=[1, 8],
        base_name="Rapier",
    )
)
axe = Item(
    char="/",
    color=color.grey,
    name="Battle axe",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.MARTIAL,
        equipment_traits=[EquipmentTraits.SWEEP],
        num_dice=1,
        die_size=8,
        base_name="Battle axe",
    )
)
club = Item(
    char="/",
    color=color.brown,
    name="Club",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.SIMPLE,
        equipment_traits=[EquipmentTraits.THROWN],
        num_dice=1,
        die_size=6,
        base_name="Club",
    )
)
light_hammer = Item(
    char="/",
    color=color.grey,
    name="Light hammer",
    equippable=Equippable(
        equipment_type=EquipmentType.WEAPON,
        equipment_category=EquipmentCategory.MARTIAL,
        equipment_traits=[EquipmentTraits.AGILE, EquipmentTraits.THROWN],
        num_dice=1,
        die_size=6,
        base_name="Light hammer",
    )
)

# SHIELDS
wood_shield = Item(
    char=")",
    color=color.brown,
    name="Wooden Shield",
    equippable=Equippable(
        equipment_type=EquipmentType.SHIELD,
        ac_bonus=1,
        base_name="Wooden Shield",
    )
)
iron_shield = Item(
    char=")",
    color=color.grey,
    name="Iron Shield",
    equippable=Equippable(
        equipment_type=EquipmentType.SHIELD,
        ac_bonus=2,
        base_name="Iron Shield",
    )
)

# CHEST ARMOR
leather_armor = Item(
    char="[",
    color=color.brown,
    name="Leather Armor",
    equippable=Equippable(
        equipment_type=EquipmentType.CHEST,
        equipment_category=EquipmentCategory.LIGHT,
        ac_bonus=1,
        base_name="Leather Armor",
    )
)
chain_mail = Item(
    char="[",
    color=color.grey,
    name="Chain Mail",
    equippable=Equippable(
        equipment_type=EquipmentType.CHEST,
        equipment_category=EquipmentCategory.MEDIUM,
        ac_bonus=4,
        base_name="Chain Mail",
    )
)

# HELMETS


# LEGGINGS


# GLOVES


# BOOTS


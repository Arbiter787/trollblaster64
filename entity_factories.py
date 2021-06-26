from components.ai import HostileEnemy
from components import consumable, equippable
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Actor, Item

# PLAYER
player = Actor(
    char="@",
    color=(255, 255, 255),
    name="Player",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    inventory=Inventory(capacity=26),
    level=Level(level_up_base=200),
)

# ENEMIES
orc = Actor(
    char="o",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=10, base_defense=0, base_power=3),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=35),
)
troll = Actor(
    char="T",
    color=(0, 127, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=16, base_defense=1, base_power=5),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=100),
)
ogre = Actor(
    char="O",
    color=(0, 82, 0),
    name="Ogre",
    ai_cls=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(hp=30, base_defense=2, base_power=8),
    inventory=Inventory(capacity=0),
    level=Level(xp_given=250),
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
    equippable=equippable.Dagger()
)
sword = Item(
    char="/",
    color=(0, 191, 255),
    name="Sword",
    equippable=equippable.Sword()
)
axe = Item(
    char="/",
    color=(0, 191, 255),
    name="Axe",
    equippable=equippable.Axe()
)

# SHIELDS
wood_shield = Item(
    char=")",
    color=(107, 94, 56),
    name="Wooden Shield",
    equippable=equippable.WoodShield()
)
iron_shield = Item(
    char=")",
    color=(120, 120, 120),
    name="Iron Shield",
    equippable=equippable.IronShield()
)

# CHEST ARMOR
leather_armor = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Armor",
    equippable=equippable.LeatherArmor()
)
chain_mail = Item(
    char="[",
    color=(120, 120, 120),
    name="Chain Mail",
    equippable=equippable.ChainMail()
)

# HELMETS
iron_helmet = Item(
    char="[",
    color=(120, 120, 120),
    name="Iron Helmet",
    equippable=equippable.IronHelmet()
)

# LEGGINGS
leather_pants = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Pants",
    equippable=equippable.LeatherPants()
)
chain_leggings = Item(
    char="[",
    color=(120, 120, 120),
    name="Chain Leggings",
    equippable=equippable.ChainLeggings()
)

# GLOVES
leather_gloves = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Gloves",
    equippable=equippable.LeatherGloves()
)

# BOOTS
leather_boots = Item(
    char="[",
    color=(139, 69, 19),
    name="Leather Boots",
    equippable=equippable.LeatherBoots()
)
iron_boots = Item(
    char="[",
    color=(120, 120, 120),
    name="Iron Boots",
    equippable=equippable.IronBoots()
)

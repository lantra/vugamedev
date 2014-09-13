"""The code for making equipment and the data"""
import libtcodpy as libtcod
import rogueutil as rutil
import math

class Weapon:
    """The diffrent classes of items will determing their function, in this case the basics are defined for the weapon type
the name of the weapon (axe) its characther for drawing (')'), it's base color (libtcod.gray), its base damage (5), it's dex_modifier, how easy it is to hit with that weapon, (0), the agi_modifier, how easy it is to move with that weapon (0), the material of the item that mutates the values, same with the magical component, and the tier is the level at which the item will spawn, every vanilla item is tier "1" and can only be changed by the material"""
    def __init__(self, name, char, color, base_damage, dex_modifier, agi_modifier, w_range=1, material=None, magical=None, tier=1, base_type='none'):
        self.name = name
        self.base_type = base_type
        self.char = char
        self.color = color
        self.base_stat = base_damage #changed for easy integration with material component
        self.dex_modifier = dex_modifier
        self.agi_modifier = agi_modifier
        self.tier = tier
        self.w_range = w_range
        
        self.material = material        
        if self.material:  #set the owner of material to the weapon
            self.material.owner = self
            self.material.mutate() #intialize the MUTATION!!!


    def add_magic_component(self, magic_component):
        self.magic = magic_component       
        if self.magic:
            self.magic.owner = self
            self.magic.mutate() 

    def test(self):
        print self.name + ' ' + self.char + ' ' + str(self.base_stat)

class Armor:
    """The diffrent classes of items will determing their function, in this case the basics are defined for the armor type
the name of the weapon (axe) its characther for drawing (')'), it's base color (libtcod.gray), its base damage (5), it's dex_modifier, how easy it is to hit with that weapon, (0), the agi_modifier, how easy it is to move with that weapon (0), the material of the item that mutates the values, same with the magical component, and the tier is the level at which the item will spawn, every vanilla item is tier "1" and can only be changed by the material"""
    def __init__(self, name, char, color, base_ac, dex_modifier, agi_modifier, slot, material=None, magical=None, tier=1):
        self.name = name
        self.char = char
        self.color = color
        self.base_stat = base_ac #changed for easy integration with material component
        self.dex_modifier = dex_modifier
        self.agi_modifier = agi_modifier
        self.tier = tier
        self.slot = slot
        
        self.material = material        
        if self.material:  #set the owner of material to the armor
            self.material.owner = self
            self.material.mutate() #intialize the MUTATION!!!


    def add_magical_component(self, magic_component):
        self.magic = magic_component        
        if self.magic: 
            self.magic.owner = self
            self.magic.mutate() 
 

class Material:
    """the possible materials, the prefix is the name that gets added to the front of the item (Iron Battleaxe), the color the item changes to (libtcod.sky), the basestate change so for the battle axe it would add (1) to it's base damage of (5), tier is the tier level the item changes to) agi mod should only affect armors.""" 
    def __init__(self, prefix, color, base_stat_change, tier, formagic=False):
        self.prefix = prefix
        self.color = color
        self.base_stat_change = base_stat_change
        self.tier = tier
        self.formagic = formagic

    def mutate(self):
        self.owner.base_stat += self.base_stat_change
        self.owner.name = self.prefix + ' ' + self.owner.name + ' (' + str(self.owner.base_stat) + ',' + str(self.owner.dex_modifier) + ',' + str(self.owner.agi_modifier) + ')' if not self.formagic else self.prefix + ' ' + self.owner.name
        self.owner.color = self.color


class Magic:
    """makes add's a bonus property to equipment"""
    def __init__(self, name, prefix, stat, change, special, tier, color=libtcod.purple):
        self.name  = name
        self.prefix = prefix # bool value
        self.stat = stat # the stat that changes
        self.change = change #the amount the stat changes
        self.tier = tier #the new tier level of the item (not useful yet)
        self.special = special
        self.color = color

    def mutate(self):
        self.owner.name = self.name + ' ' + self.owner.name + ' (' + str(self.owner.base_stat) + ',' + str(self.owner.dex_modifier) + ',' + str(self.owner.agi_modifier) + ')' if self.prefix else self.owner.name + ' ' + self.name + ' (' + str(self.owner.base_stat) + ',' + str(self.owner.dex_modifier) + ',' + str(self.owner.agi_modifier) + ')'
        self.owner.color = self.color

def make_weapon(tier, formagic = False):
    """Make a weapon based on the tier input"""
    materials = {}
    if tier == 1:    
        materials['iron'] = 90
        materials['wood'] = 10

    elif tier == 2:    
        materials['steel'] = 90
        materials['elm wood'] = 10

    elif tier == 3:   
        materials['darksteel'] = 90
        materials['dark wood'] = 10

    choice = rutil.random_choice(materials)
    weapons = {}

    if choice == 'iron' or choice == 'steel' or choice == 'darksteel':

        weapons['sword'] = 5
        weapons['mace'] = 5
        weapons['warhammer'] = 5
        weapons['battleaxe'] = 5
        weapons['greataxe'] = 5
        weapons['dagger'] = 5

    else:
        weapons['bow'] = 5

    #define the materials then choose a material for the weapon based off of the tiers


    if choice == 'iron':
        material_component = Material("Iron", libtcod.grey, 1, 1, formagic)
    
    elif choice == 'steel':
        material_component = Material("Steel", libtcod.sky, 2, 2, formagic)

    elif choice == 'darksteel':
        material_component = Material("Dark Steel", libtcod.dark_sky, 3, 3, formagic)

    elif choice == 'wood':
        material_component = Material("Wood", libtcod.dark_orange, 1, 1, formagic)

    elif choice == 'elm wood':
        material_component = Material("Elm Wood", libtcod.dark_orange, 2, 1, formagic)

    elif choice == 'dark wood':
        material_component = Material("Dark Wood", libtcod.darker_red, 3, 1, formagic)

    choice = rutil.random_choice(weapons)
    
    if choice == 'sword':
        weapon = Weapon(name="Sword", char='/', color=libtcod.grey, base_damage=4, dex_modifier=2, agi_modifier=1, material=material_component, base_type="1h")

    elif choice == 'mace':
        weapon = Weapon(name="Mace", char='(', color=libtcod.grey, base_damage=5, dex_modifier=1, agi_modifier=0, material=material_component, base_type="1h")

    elif choice == 'warhammer':
        weapon = Weapon(name="Warhammer", char='(', color=libtcod.grey, base_damage=8, dex_modifier=-2, agi_modifier=-1, material=material_component, base_type="2h")

    elif choice == 'battleaxe':
        weapon = Weapon(name="Battle Axe", char=')', color=libtcod.grey, base_damage=5, dex_modifier=0, agi_modifier=1, material=material_component, base_type="1h")

    elif choice == 'greataxe':
        weapon = Weapon(name="Great Axe", char='(', color=libtcod.grey, base_damage=7, dex_modifier=-1, agi_modifier=0, material=material_component, base_type="2h")

    elif choice == 'dagger':
        weapon = Weapon(name="Dagger", char='-', color=libtcod.grey, base_damage=3, dex_modifier=1, agi_modifier=3, material=material_component, base_type="small")

    elif choice == 'bow':
        weapon = Weapon(name="Bow", char=')', color=libtcod.dark_orange, base_damage=1, dex_modifier=0, agi_modifier=0, material=material_component, base_type="Bow")

    return weapon

def make_armor(tier, formagic=False):

    materials = {}
    if tier == 1: 
        materials['wood'] = 10
        materials['leather'] = 40  
        materials['iron'] = 40
        materials['steel'] = 10

    elif tier == 2:    
        materials['steel'] = 45
        materials['darksteel'] = 10
        materials['studdedleather'] = 45

    elif tier == 3:   
        materials['darksteel'] = 50
        materials['bloodleather'] = 50

    armors = {} # the dict for the armors
    

    #define the materials then choose a material for the weapon based off of the tiers
    choice = rutil.random_choice(materials)

    if choice == 'iron':
        material_component = Material("Iron", libtcod.grey, 1, 1, formagic)
    
    elif choice == 'steel':
        material_component = Material("Steel", libtcod.sky, 2, 2, formagic)

    elif choice == 'darksteel':
        material_component = Material("Dark Steel", libtcod.dark_sky, 3, 3, formagic)
    
    elif choice == 'wood':
        material_component = Material("Wooden", libtcod.dark_orange, 0, 1, formagic)

    elif choice == 'leather':
        material_component = Material("Leather", libtcod.dark_orange, 1, 1, formagic)

    elif choice == 'studdedleather':
        material_component = Material("Studded Leather", libtcod.dark_orange, 2, 2, formagic)

    elif choice == 'bloodleather':
        material_component = Material("Blood Leather", libtcod.darker_red, 3, 3, formagic)

    #because armors behave diffrently these are the values that need to change    
    if choice == 'wood':
        armors['shield'] = 100

    elif choice == 'leather' or choice == 'studdedleather' or choice == 'bloodleather':
        armors['armor'] = 100  

    else:
        armors['chainmail'] = 35
        armors['scalemail'] = 25
        armors['platemail'] = 25
        armors['shield'] = 15

    choice = rutil.random_choice(armors)

    if choice == 'shield':
        armor = Armor(name="Shield", char='O', color=libtcod.grey, base_ac=1, dex_modifier=0, agi_modifier=0, slot='left hand', material=material_component)

    elif choice == 'armor':
        armor = Armor(name="Armor", char='#', color=libtcod.grey, base_ac=1, dex_modifier=0, agi_modifier=3, slot='body', material=material_component)

    elif choice == 'chainmail':
        armor = Armor(name="Chainmail", char='#', color=libtcod.grey, base_ac=2, dex_modifier=0, agi_modifier=0, slot='body', material=material_component)

    elif choice == 'scalemail':
        armor = Armor(name="Scalemail", char='#', color=libtcod.grey, base_ac=3, dex_modifier=0, agi_modifier=-1, slot='body', material=material_component)

    elif choice == 'platemail':
        armor = Armor(name="Platemail", char='#', color=libtcod.grey, base_ac=4, dex_modifier=0, agi_modifier=-3, slot='body', material=material_component)

    return armor    

def magic_weapon(tier):

    magic = {}
    magic['sharpness'] = 10
    magic['death'] = 1
    magic['health'] = 10
    magic['accurate'] = 10
    magic['parrying'] = 10
    magic['flambouyent'] = 10
    magic['fire'] = 5
    magic['explosive'] = 1
    
    choice = rutil.random_choice(magic)
    
    if choice == 'sharpness':
        magic_component = Magic(name='of Sharpness', prefix=False, stat='wep_damage', change=tier, special=None, tier=0)     

    elif choice == 'death':
        magic_component = Magic(name='of Death', prefix=False, stat='wep_damage', change=tier*5, special='death', tier=0)
    
    elif choice == 'health':
        magic_component = Magic(name='of Health', prefix=False, stat='hp', change=tier*5, special=None, tier=0)

    elif choice == 'accurate': 
        magic_component = Magic(name='of Accuarcy', prefix=False, stat='dex', change=tier, special=None, tier=0)
    
    elif choice == 'parrying':
        magic_component = Magic(name='of Parrying', prefix=False, stat='agi', change=tier, special=None, tier=0)

    elif choice == 'flambouyent':
        magic_component = Magic(name='Flambouyent', prefix=True, stat='cha', change=tier, special=None, tier=0)

    elif choice == 'fire':
        magic_component = Magic(name='Flaming', prefix=True, stat=None, change=None, special='flaming', tier=0, color=libtcod.flame)

    elif choice == 'explosive':
        magic_component = Magic(name='Explosive', prefix=True, stat=None, change=None, special='explosive', tier=0)

    weapon = make_weapon(tier, True)

    weapon.add_magic_component(magic_component)
   
    return weapon   
    
    

 


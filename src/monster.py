"""The monster module, used to generate monster for the game"""
import libtcodpy as libtcod
import rogueutil as rutil 
 
class Monster:
    def __init__(self, base_type, dr = 0, family_component=None, base_type_component=None, boss_type_component=None):
        self.base_type = base_type
        self.dr = dr
        self.name = ""
        self.hp = 0
        self.wep_damage = 0
        self.agi = 0
        self.strength = 0
        self.fatigue = 0
        self.dex = 0
        self.ac = 0 
        self.color = None
        self.symbol = None
        self.attack_type = 'melee'
        self.attack_range = 1
        self.special = None



        self.family_component = family_component
        if self.family_component:
            self.family_component.owner = self
            self.family_component.mutate()

        self.base_type_component = base_type_component
        if self.base_type_component:
            self.base_type_component.owner = self
            self.base_type_component.mutate()

        self.boss_type_component = boss_type_component
        if self.boss_type_component:
            self.boss_type_component.owner = self
            self.boss_type_component.mutate()


    def test(self):
        print self.name + " " + str(self.hp) + " " + str(self.wep_damage) + " " + str(self.dr) + " " + self.symbol

class Family:
    #orc, elf, troll, wolf each one will have base stats that. 
    def __init__(self, name, hp, wep_damage, agi, strength, fatigue, dex, ac, color, symbol, dr): 

        self.name = name
        self.hp = hp
        self.wep_damage = wep_damage
        self.agi = agi
        self.strength = strength
        self.fatigue = fatigue
        self.dex = dex
        self.ac = ac
        self.color = color
        self.symbol = symbol
        self.dr = dr # dr change (so an orc will have a base DR of 1, or maybe 0.)

    def mutate(self):
        self.owner.name += self.name
        self.owner.hp += self.hp
        self.owner.wep_damage += self.wep_damage
        self.owner.agi += self.agi
        self.owner.strength += self.strength
        self.owner.fatigue += self.fatigue
        self.owner.dex += self.dex
        self.owner.ac += self.ac
        self.owner.color = self.color
        self.owner.symbol = self.symbol
        self.owner.dr += self.dr

class Type:
    def __init__(self, name, hp=0, wep_damage=0, agi=0, strength=0, fatigue=0, dex=0, ac=0, dr=0, color=None, symbol=None, prefix=True, attack_type='melee', attack_range=1): 
        
        self.prefix = prefix
        self.name = name
        self.hp = hp
        self.wep_damage = wep_damage
        self.agi = agi
        self.strength = strength
        self.fatigue = fatigue
        self.dex = dex
        self.ac = ac
        self.color = color
        self.symbol = symbol
        self.dr = dr # dr change (so an Orc Savage will have a dr of 2.)
        self.attack_type = attack_type
        self.attack_range = attack_range
        

    def mutate(self):
        if self.prefix == True:
            self.owner.name = self.name + " " + self.owner.name
        else:
            self.owner.name = self.owner.name + " " + self.name

        self.owner.hp += self.hp
        self.owner.wep_damage += self.wep_damage
        self.owner.agi += self.agi
        self.owner.strength += self.strength
        self.owner.fatigue += self.fatigue
        self.owner.dex += self.dex
        self.owner.ac += self.ac
        self.owner.dr += self.dr
        self.owner.attack_type = self.attack_type
        self.owner.attack_range = self.attack_range
        
        if self.color != None:       
            self.owner.color = self.color

        if self.symbol != None:      
            self.owner.symbol = self.symbol
        

class Boss:
    def __init__(self, hp=0, wep_damage=0, agi=0, strength=0, fatigue=0, dex=0, ac=0, dr=0, color=libtcod.fuchsia, symbol=None, special=None): 
        
        self.name = rutil.otherworld_boss_names()
        self.hp = hp
        self.wep_damage = wep_damage
        self.agi = agi
        self.strength = strength
        self.fatigue = fatigue
        self.dex = dex
        self.ac = ac
        self.color = color
        self.symbol = symbol
        self.dr = dr
        self.special = special

    def mutate(self):
        
        self.owner.name = self.name
        self.owner.hp += self.hp
        self.owner.wep_damage += self.wep_damage
        self.owner.agi += self.agi
        self.owner.strength += self.strength
        self.owner.fatigue += self.fatigue
        self.owner.dex += self.dex
        self.owner.ac += self.ac
        self.owner.dr += self.dr
        self.owner.special = self.special
        
        if self.color != None:       
            self.owner.color = self.color

        if self.symbol != None:      
            self.owner.symbol = self.symbol



def make_monster(dr, rsc=False):
    """Rsc is return seprate components"""
    base_types = {}
    base_types["humaniod"] = 50
    base_types["beast"] = 15
    base_types["undead"] = 15

    base_type = rutil.random_choice(base_types)

    families = {}
    type_components = {}
    
    if base_type == "humaniod":
        #families
        families["orc"] = 15
        families["elf"] = 15
        families["outlaw"] = 15
        families["troll"] = 15
        families["minotaur"] = 15
        families["derranged halfling"] = 15
        families["ratman"] = 15

        #type components
        type_components["none"] = 15
        type_components["warrior"] = 15
        type_components["savage"] = 15
        type_components["beserker"] = 15
        type_components["rogue"] = 15
        type_components["defender"] = 15
        type_components["marauder"] = 15
        type_components["elite"] = 15
        type_components["archer"] = 15


        
    elif base_type == "beast":
        families["wolf"] = 15
        families["worg"] = 15
        families["lizard"] = 15
        families["rat"] = 15

        #type components
        type_components["none"] = 15
        type_components["ravenous"] = 15
        type_components["giant"] = 15
        type_components["mutated"] = 15
        type_components["rabid"] = 15

    elif base_type == "undead":
        families["zombie"] = 15
        families["skeleton"] = 15
        families["death knight"] = 15

        type_components["none"] = 15
        type_components["warrior"] = 15
        type_components["long dead"] = 15
        type_components["necrotic"] = 15



    choice = rutil.random_choice(families)
    choice2 = rutil.random_choice(type_components)
    #Family types yo
    #humaniods
    if base_type == "humaniod":
        if choice == "orc":
            family = Family(name="Orc", hp=7, wep_damage=3, agi=8, strength=10, fatigue=15, dex=8, ac=0, color=libtcod.green, symbol='o', dr=1)
    
        elif choice == "elf":
            family = Family(name="Elf", hp=5, wep_damage=2, agi=14, strength=6, fatigue=15, dex=12, ac=0, color=libtcod.yellow, symbol='e', dr=1) 

        elif choice == "outlaw":
            family = Family(name="Outlaw", hp=10, wep_damage=3, agi=10, strength=8, fatigue=10, dex=10, ac=0, color=libtcod.darker_gray, symbol='@', dr=1)
        elif choice == "troll":
            family = Family(name="Troll", hp=15, wep_damage=5, agi=6, strength=12, fatigue=30, dex=8, ac=2, color=libtcod.darker_green, symbol='T', dr=3)
        elif choice == "minotaur":
            family = Family(name="Minotaur", hp=20, wep_damage=6, agi=8, strength=14, fatigue=45, dex=8, ac=1, color=libtcod.darker_orange, symbol='M', dr=4)
        elif choice == "derranged halfling":
            family = Family(name="Derranged Halfling", hp=4, wep_damage=2, agi=12, strength=8, fatigue=20, dex=12, ac=1, color=libtcod.red, symbol='h', dr=2)
        elif choice == "ratman":
            family = Family(name="Ratman", hp=10, wep_damage=4, agi=12, strength=8, fatigue=15, dex=12, ac=1, color=libtcod.orange, symbol='R', dr=2)

        #now to decide DA BASECOMPONENT
        #type components

        if choice2 == "none":
            type_component = None

        elif choice2 == "warrior":
            type_component = Type("Warrior", hp=3, wep_damage=0, agi=0, strength=2, fatigue=3, dex=2, ac=1, dr=1, color=None, symbol=None, prefix=False)

        elif choice2 == "savage":
            type_component = Type("Savage", hp=0, wep_damage=0, agi=0, strength=4, fatigue=5, dex=0, ac=0, dr=0, color=None, symbol=None, prefix=False)

        elif choice2 == "beserker":
            type_component = Type("Beserker", hp=10, wep_damage=2, agi=-2, strength=4, fatigue=10, dex=0, ac=0, dr=2, color=libtcod.darker_red, symbol=None, prefix=False)

        elif choice2 == "rogue":
            type_component = Type("Rogue", hp=0, wep_damage=2, agi=4, strength=0, fatigue=3, dex=4, ac=0, dr=1, color=None, symbol=None, prefix=False)

        elif choice2 == "defender":
            type_component = Type("Defender", hp=5, wep_damage=0, agi=0, strength=2, fatigue=10, dex=0, ac=3, dr=2, color=None, symbol=None, prefix=False)

        elif choice2 == "marauder":
            type_component = Type("Marauder", hp = 5, wep_damage=4, agi=0, strength=2, fatigue=10, dex=2, ac=2, dr=3, color=None, symbol=None, prefix=False)

        elif choice2== "elite":
            type_component = Type("Elite", hp=10, wep_damage=2, agi=2, strength=2, fatigue=10, dex=2, ac=2, dr=3, color=None, symbol=None, prefix=True)

        elif choice2 == "archer" and (choice != "troll" or choice != "minotaur" or not rsc):
            type_component = Type("Archer", hp=0, wep_damage=0, agi=0, strength=-6, fatigue=5, dex=-4, ac=0, dr=1, color=None, symbol=None, prefix=False, attack_type='ranged', attack_range='5')


#SAY WHAT BEASTS SON
    elif base_type == "beast":
        if choice == "wolf":
            family = Family(name="Wolf", hp=10, wep_damage=1, agi=12, strength=8, fatigue=15, dex=0, ac=0, color=libtcod.gray, symbol='w', dr=1) 

        elif choice == "worg":
            family = Family(name="Worg", hp=15, wep_damage=3, agi=12, strength=12, fatigue=25, dex=10, ac=2, color=libtcod.darker_gray, symbol='W', dr=3)

        elif choice == "lizard":
            family = Family(name="Lizard", hp=4, wep_damage=1, agi=16, strength=4, fatigue=5, dex=10, ac=1, color=libtcod.orange, symbol='l', dr=0)

        elif choice == "rat":
            family = Family(name="rat", hp=2, wep_damage=1, agi=18, strength=2, fatigue=4, dex=10, ac=0, color=libtcod.dark_orange, symbol='r', dr=0)

        if choice2 == "none":
            type_component = None

        elif choice2 == "ravenous":
            type_component = Type("Ravenous", hp=5, wep_damage=2, agi=0, strength=2, fatigue=0, dex=2, ac=0, dr=1, color=None, symbol=None, prefix=True)

        elif choice2 == "giant":
            type_component = Type("Giant", hp=20, wep_damage=4, agi=-4, strength=4, fatigue=5, dex=0, ac=1, dr=2, color=None, symbol=None, prefix=True)

        elif choice2 == "mutated":
            type_component = Type("Mutated", hp=10, wep_damage=2, agi=0, strength=4, fatigue=10, dex=0, ac=2, dr=3, color=None, symbol=None, prefix=True)

        elif choice2 == "rabid":
            type_component = Type("Rabid", hp=5, wep_damage=0, agi=0, strength=2, fatigue=5, dex=2, ac=0, dr=1, color=None, symbol=None, prefix=True)

            

    #THE UNDEAD... OH SNAP!
    elif base_type == "undead":
        if choice == "zombie":
            family = Family(name="zombie", hp=1, wep_damage=2, agi=6, strength=12, fatigue=25, dex=8, ac=4, color=libtcod.white, symbol='z', dr=1)

        elif choice == "skeleton":
            family = Family(name="Skeleton", hp=25, wep_damage=2, agi=4, strength=8, fatigue=5, dex=10, ac=3, color=libtcod.white, symbol='s', dr=1)

        elif choice == "death knight":
            family = Family(name="Death Kngiht", hp=35, wep_damage=9, agi=12, strength=14, fatigue=30, dex=14, ac=4, color=libtcod.black, symbol='D', dr=5)

        if choice2 == "none":
            type_component = None

        elif choice2 == "warrior":
            type_component = Type("Warrior", hp=3, wep_damage=0, agi=0, strength=2, fatigue=3, dex=2, ac=1, dr=1, color=None, symbol=None, prefix=False)

        elif choice2 == "long dead":
            type_component = Type("Long Dead", hp=0, wep_damage=0, agi=-2, strength=-2, fatigue=0, dex=0, ac=1, dr=0, color=None, symbol=None, prefix=True)

        elif choice2 == "necrotic":
            type_component = Type("Necrotic", hp=5, wep_damage=2, agi=0, strength=2, fatigue=0, dex=2, ac=1, dr=1, color=None, symbol=None, prefix=True)

    
    monster = Monster(base_type, family_component=family,base_type_component=type_component) #this makes computing dr for bosses a little easier

    if not rsc:

        if monster.dr == dr or monster.dr == dr + 1 or monster.dr == dr - 1: #check difficulty rating to see if it matches
            return monster
        else:
            monster = make_monster(dr)
            return monster
    elif rsc:
        if monster.dr == dr or monster.dr == dr + 1 or monster.dr == dr - 1: #check difficulty rating to see if it matches
            return base_type, family, type_component
        else:
            base_type, family, type_component = make_monster(dr, True)
            return base_type, family, type_component

def make_mini_boss(dr):
    """generate a boss, with stats based on dr rating"""
    #bosses = {}

    #bosses[basic_boss] = 100
    
    base_type, family, type_component = make_monster(dr, rsc=True)

    basic_boss = Boss(hp=5*dr, wep_damage=dr*2, agi=0, strength=dr, fatigue=5*dr, dex=0, ac=dr, dr=dr*10, color=libtcod.fuchsia, symbol=None, special=None)
    
    boss = Monster(base_type, family_component=family, base_type_component=type_component, boss_type_component=basic_boss)

    return boss
    


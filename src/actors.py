"""The framework for player characthers"""
import rogueutil as rutil


BASELINE_STR = 10  #damage mod
BASELINE_AGI = 10  #evasivness mod
BASELINE_DEX = 10  #dexterity mod
BASELINE_INT = 10  #magic effectiveness mod
BASELINE_WIS = 10  #Mana affinity increase
BASELINE_CON = 10  #Health increase 
BASELINE_CHA = 10  #Ratings increase

class Actor():
    def __init__(self, background_component):
        self.name = self.get_name()
        self.str = BASELINE_STR
        self.agi = BASELINE_AGI
        self.int = BASELINE_INT
        self.wis = BASELINE_WIS
        self.con = BASELINE_CON
        self.cha = BASELINE_CHA
        self.inventory = []
        self.exp = 0

    def get_name():
        return rutil.otherworld_names()

    def get_background(self):
        pass

    def get_training(self):
        pass

    def get_specialization(self):
        pass

    def die(self):
        pass

    def actor_export(self):
        pass

    def actor_import(self)
        pass

class Background():
    def __init__(self):
        pass

class Training():
    def __init__(self):
        pass

class Specialization():
    def __init__(self):
        pass

import libtcodpy as libtcod
import rogueutil as rutil
import math
import textwrap
import time
import shelve
import combat
import equipment
import monster




SCREEN_WIDTH = 80 #constant for screen width
SCREEN_HEIGHT = 50 #constant for screen height
LIMIT_FPS = 20 #FPS limiter
MAP_WIDTH = 80 #constant for the map width
MAP_HEIGHT = 43 #constant for the map height
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10
INVENTORY_WIDTH = 50
LEVEL_SCREEN_WIDTH = 40
CHARACTER_SCREEN_WIDTH = 30
MAX_TRAP = 3
MAX_BOSS = 2 # max amount of bosses that will spawn on any relevant level

#sizes and coordinates relevant for the GUI
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

#define colors
color_dark_wall = libtcod.Color(28, 28, 28)
color_light_wall = libtcod.Color(156, 156, 156)
color_dark_ground = libtcod.Color( 0, 0, 100)
color_light_ground = libtcod.Color(139, 69, 19)


#**************************Function and Classes**********************

class Object:
    """this is a generic object: the player, a monster, an item, the stairs
    it's always represented by a character on screen"""
    def __init__(self, x, y, char, name, color, blocks=False, always_visible=False, fighter=None, ai=None, item=None, equipment=None, trap=None, actor=None, boss=None, animation=None):
        self.always_visible = always_visible
        self.name = name
        self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color

        self.fighter = fighter
        if self.fighter:  #let the fighter component know who owns it
            self.fighter.owner = self

        self.ai = ai
        if self.ai:  #let the AI component know who owns it
            self.ai.owner = self

        self.item = item
        if self.item:  #let the Item component know who owns it
            self.item.owner = self


        self.equipment = equipment
        if self.equipment:  #let the Equipment component know who owns it
            self.equipment.owner = self

            #there must be an Item component for the Equipment component to work properly
            self.item = Item()
            self.item.owner = self


        self.trap = trap
        if self.trap:
            self.trap.owner = self

        self.actor = actor
        if self.actor:
            self.actor.owner = self

        self.boss = boss
        if self.boss:
            self.boss.owner = self

        self.animation = animation
        if self.animation:
            self.animation.owner = self

    def move (self, dx, dy):
        """move by the given ammount, change in x and change in y if destination is not blocked"""
        if self.animation or not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy


    def move_to(self, x, y):
        """override to move to a tile no matter what"""
        self.x = x
        self.y = y


    def draw(self):
        """set the color and then draw the character that represents this
        object"""
        #only show if it's visible to the player; or it's set to "always visible" and on an explored tile
        if (libtcod.map_is_in_fov(fov_map, self.x, self.y) or
            (self.always_visible and s_map[self.x][self.y].explored)):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        """erase the character that represents this object"""
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)


    def move_towards(self, target_x, target_y):
        #vector from this object to the target, and distance
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        """
        if is_blocked(self.x + dx, self.y + dy)
            if is_blocked(self.x + dx, self.y) and
        """

        self.move(dx, dy)

    def distance_to(self, other):
        #return the distance to another object
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def distance_to_tile(self, x, y):
        #return the distance to another tile
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def send_to_back(self):
        #make this object be drawn first, so all others appear above it if they're in the same tile.
        global objects
        objects.remove(self)
        objects.insert(0, self)

    def distance(self, x, y):
        #return the distance to some coordinates
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def get_pos(self):
        return self.x, self.y

    def calc_path(self, path, ox, oy, dx, dy):
        libtcod.path_compute(path, ox, oy, dx, dy)

    def walk_path(self, l_path):
        return libtcod.path_walk(l_path, True)



class Actor:
    def __init__(self, cha=10):

        self.ratings = 0.0
        self.base_fame = 1.0
        self.base_cha = cha
        self.resource = self.get_resource()
        self.max_res = 20
        self.res = self.max_res

        self.abilities = []
        chg = Ability("Charge", 5, charge)
        self.abilities.append(chg)
        ren = Ability("Rend", 5, rend)
        self.abilities.append(ren)
        ww = Ability("Whirl Wind", 10, whirlwind)
        self.abilities.append(ww)
        clv = Ability("Cleave", 5, cleave)
        self.abilities.append(clv)



    @property
    def cha(self):
        bonus = sum(equipment.cha_bonus for equipment in get_all_equipped(self.owner))
        return self.base_cha + bonus

    @property
    def fame(self):
        bonus = self.cha * 0.1
        return self.base_fame * bonus

    def get_resource(self):
        """plug in for later"""
        return 'Focus'

    def modify_rating(self, change):
        if change > 0:
            self.ratings += change * self.fame
        else:
            self.ratings -= change / self.fame

class Ability:
    def __init__(self,name, cost, use_function):
        self.name = name
        self.cost = cost
        self.use_function = use_function

    def use(self):
        if self.cost <= player.actor.res:
            if self.use_function() != 'cancelled':
                player.actor.res -= self.cost
        else:
            message("You don't have enough " + player.actor.resource + " to use this ability.", libtcod.cyan)
            return 'cancelled'

class Animation:
    def __init__(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.turns = 0

    def magic_projectile(self, target_x, target_y):

        objects.append(self.owner)
        while self.owner.distance_to_tile(target_x, target_y) >= 0:
            self.owner.clear()
            self.owner.move_towards(target_x, target_y)
            render_all()
            libtcod.console_flush()
            #time.sleep(.05)

        animation = False
        self.owner.clear()
        objects.remove(self.owner)

    def arrow(self, target_x, target_y):
        target = None

        while self.owner.distance_to_tile(target_x, target_y) >= 1:
            game_state = 'animation'
            target = None
            #check for monsters
            for object in objects:
                if object.fighter and self.owner.x == object.fighter.owner.x and self.owner.y == object.fighter.owner.y and self.turns != 0:
                    target = object
                    break

            if target != None:
                break

            self.owner.clear()
            self.owner.move_towards(target_x, target_y)
            render_all()
            libtcod.console_flush()
            self.turns += 1
            #time.sleep(.01)

        if target == None:
            self.owner.clear()
            self.owner.move_to(target_x, target_y)
            render_all()
            libtcod.console_flush()
            for object in objects:
                if object.fighter and self.target_x == object.fighter.owner.x and self.target_y == object.fighter.owner.y:
                    target = object
                    break


        if target == None:
            game_state = 'playing'
            target = None
            return target
        else:
            game_state = 'playing'
            return target


    def delete_self(self):
        objects.remove(self.owner)

class Special:
    def __init__(self, on_hit, aura, function):
        self.on_hit = on_hit #bool
        self.aura = aura #bool
        self.function = function

        if aura:
            player.fighter.add_aura(function)

    def proc_on_hit(self, attacker, defender):
        self.function(attacker, defender)

class StatusEffect:
    def __init__(self, function, t, run_time):
        self.function = function
        self.t = 0
        self.run_time = run_time

    def proc(self):
        if self.t < self.run_time:
            self.t += 1
            self.function(self.owner)#the function that saves the owner
        else:
            self.owner.status_effects.remove(self)


class Fighter:
    """combat-related properties and methods (monster, player, NPC)."""
    def __init__(self, hp, agi, strength, dex=10, ac=0, fatigue=25, wep_damage=2, dr=0, death_function=None,  player = False):
        self.death_function = death_function
        self.base_max_hp = hp
        self.base_wep_damage = wep_damage
        self.hp = hp
        self.base_agi = agi
        self.base_strength = strength
        self.fatigue = fatigue
        self.base_max_fatigue = fatigue
        self.base_dex = dex
        self.base_ac = ac
        self.player = player
        self.dr = dr
        self.specials = []
        self.status_effects = []

        #stances
        self.stance_unassigned = 0
        self.stance_power = 0
        self.stance_recklessness = 0
        self.stance_evasiveness = 0
        self.stance_aggresiveness = 0

        #calclule and intialize values based on the player
        if not player:
            self.xp = dr * 30

        else:
            self.xp = 0
            #intialize stances
            self.stance_unassigned = 5

    @property
    def strength(self):
        bonus = sum(equipment.strength_bonus for equipment in get_all_equipped(self.owner))
        return self.base_strength + bonus

    @property
    def max_hp(self):
        bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_hp + bonus

    @property
    def agi(self):
        bonus = sum(equipment.agi_bonus for equipment in get_all_equipped(self.owner))
        return self.base_agi + bonus

    @property
    def dex(self):
        bonus = sum(equipment.dex_bonus for equipment in get_all_equipped(self.owner))
        return self.base_dex + bonus

    @property
    def max_fatigue(self):
        bonus = sum(equipment.max_fatigue_bonus for equipment in get_all_equipped(self.owner))
        return self.base_max_fatigue + bonus

    @property
    def ac(self):
        bonus = sum(equipment.ac_bonus for equipment in get_all_equipped(self.owner))
        return self.base_ac + bonus

    @property
    def wep_damage(self):
        bonus = sum(equipment.wep_damage for equipment in get_all_equipped(self.owner))
        return self.base_wep_damage + bonus


    def take_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.hp -= damage
            #check for death. if there's a death function, call it
            if self.hp <= 0:
                function = self.death_function
                if function is not None:
                    function(self.owner)

                if self.owner != player:  #yield experience to the player and ratings!
                    player.fighter.xp += self.xp
                    player.actor.modify_rating(self.xp / 5)

    def fatigue_damage(self, damage):
        #apply damage if possible
        if damage > 0:
            self.fatigue -= damage
            #if fatigue is less than 0 set it back to 0
            if self.fatigue <= 0:
                fatigue = 0

    def attack(self, target):
        #a simple formula for attack damage
        hit = combat.roll_to_hit(self, target, message, player.actor)
        #check for an on-hit event
        if self.player and hit == 'hit' and target.fighter:
            if get_equipped_in_slot('right hand').special:
                if get_equipped_in_slot('right hand').special.on_hit:
                    get_equipped_in_slot('right hand').special.proc_on_hit(self, target)

        if self.owner.actor:
            if self.owner.actor.resource == 'Focus' and self.owner.actor.res < self.owner.actor.max_res:
                self.owner.actor.res += 1


    def heal(self, amount):
        #heal by the given amount, without going over the maximum
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def restore(self, ammount):
        #heal by the given amount, without going over the maximum
        self.fatigue += amount
        if self.fatigue > self.max_fatigue:
            self.fatigue = self.max_fatigue

    def shoot(self, target_tile_x, target_tile_y):
        arrow_component = Animation(target_tile_x, target_tile_y)
        arrow = Object(self.owner.x, self.owner.y, '-', 'Arrow', libtcod.dark_orange, animation=arrow_component)
        objects.append(arrow)
        target = arrow.animation.arrow(target_tile_x, target_tile_y)
        objects.remove(arrow)#add item conversion code here

        if target != None:
            hit = combat.roll_to_rhit(self, target, message, player.actor)
            if self.player and hit == 'hit' and target.fighter: #check for a hit event
                if get_equipped_in_slot('right hand').special:
                    if get_equipped_in_slot('right hand').special.on_hit:
                        get_equipped_in_slot('right hand').special.proc_on_hit(self, target)
        else:
            pass

    def add_status_effect(self, effect):
        self.status_effects.append(effect)
        effect.owner = self

class BasicMonster:
    #AI for a basic monster.
    def __init__(self, attack_type='melee', attack_range=0):
        self.attack_type = attack_type
        self.attack_range = attack_range
        self.path = None


    def take_turn(self):
        #a basic monster takes its turn. If you can see it, it can see you
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            #move towards player if far away
            if monster.distance_to(player) >= 2 and self.attack_type == 'melee':
                monster.move_towards(player.x, player.y)

            elif monster.distance_to(player) > self.attack_range and self.attack_type == 'ranged':
                monster.move_towards(player.x, player.y)

            #attacks if the player is alive
            elif player.fighter.hp > 0 and self.attack_type == 'melee':
                monster.fighter.attack(player)

            elif monster.distance_to(player) < self.attack_range and player.fighter.hp > 0 and self.attack_type == 'ranged':
                monster.fighter.shoot(player.x, player.y)

            #make a status check!
            status_check(self.owner.fighter)

        else:
            #wander aimlessly when the player is not in view
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))

class ConfusedMonster:
    #AI for a temporarily confused monster (reverts to previous AI after a while).
    def __init__(self, old_ai, num_turns=10):
        self.old_ai = old_ai
        self.num_turns = num_turns

    def take_turn(self):
        if self.num_turns > 0:  #still confused...
            #move in a random direction, and decrease the number of turns confused
            self.owner.move(libtcod.random_get_int(0, -1, 1), libtcod.random_get_int(0, -1, 1))
            self.num_turns -= 1

        else:  #restore the previous AI (this one will be deleted because it's not referenced anymore)
            self.owner.ai = self.old_ai
            message('The ' + self.owner.name + ' is no longer confused!', libtcod.red)

class Trap:
    def __init__(self, trigger_function=None):
        self.trigger_function = trigger_function
        self.triggered = False


    def trigger(self):
        if self.triggered == False:
            self.trigger_function()
            self.owner.char = '^'
            self.triggered = True
        else:
            message('You evade the trap!', libtcod.yellow)

class Tile:
    """a tile of the map and its properties"""
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        self.explored = False

        #by default if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight


class Rect:
    """a rectangle for drawing on a map, used for rooms."""
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def center(self):
        """defines the center of the rectangle for use in dung gen"""
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) /2
        return (center_x, center_y)

    def intersect(self, other):
        """returns true if this rectange intersecnts with another one"""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
        self.y1 <= other.y2 and self.y2 >= other.y1)

class Item:
    def __init__(self, use_function=None, is_qty=False, qty=0):
        self.use_function = use_function
        self.is_qty = is_qty
        self.qty = qty

    #an item that can be picked up and used.
    def pick_up(self):
        #add to the player's inventory and remove from the map
        if len(inventory) >= 26:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', libtcod.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', libtcod.green)

            #special case: automatically equip, if the corresponding equipment slot is unused
            equipment = self.owner.equipment
            if equipment and get_equipped_in_slot(equipment.slot) is None:
                equipment.equip()

    def use(self):
        #just call the "use_function" if it is defined

        #special case: if the object has the Equipment component, the "use" action is to equip/dequip
        if self.owner.equipment:
            self.owner.equipment.toggle_equip()
            return

        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  #destroy after use, unless it was cancelled for some reason

    def drop(self):
        #add to the map and remove from the player's inventory. also, place it at the player's coordinates
        #special case: if the object has the Equipment component, dequip it before dropping
        if self.owner.equipment:
            self.owner.equipment.dequip()

        objects.append(self.owner)
        inventory.remove(self.owner)
        self.owner.x = player.x
        self.owner.y = player.y
        message('You dropped a ' + self.owner.name + '.', libtcod.yellow)


class Equipment:
    #an object that can be equipped, yielding bonuses. automatically adds the Item component.
    def __init__(self, slot, strength_bonus=0, ac_bonus=0, max_hp_bonus=0, agi_bonus=0, max_fatigue_bonus=0, dex_bonus=0, wep_damage=0, cha_bonus=0, base_type=None, damage_type='slashing',w_range='1', special=None):
        self.strength_bonus = strength_bonus
        self.ac_bonus = ac_bonus
        self.max_hp_bonus = max_hp_bonus
        self.agi_bonus = agi_bonus
        self.max_fatigue_bonus = max_fatigue_bonus
        self.dex_bonus = dex_bonus
        self.slot = slot
        self.is_equipped = False
        self.wep_damage = wep_damage
        self.cha_bonus = cha_bonus
        self.base_type = base_type
        self.damage_type = damage_type
        self.w_range = w_range
        self.special = None


    def toggle_equip(self):  #toggle equip/dequip status
        if self.is_equipped:
            self.dequip()
        else:
            self.equip()

    def equip(self):

        #if the slot is already being used, dequip whatever is there first
        old_equipment = get_equipped_in_slot(self.slot)
        if old_equipment is not None:
            old_equipment.dequip()

        #equip object and show a message about it
        self.is_equipped = True
        message('Equipped ' + self.owner.name + ' on ' + self.slot + '.', libtcod.light_green)

    def dequip(self):
        #dequip object and show a message about it
        if not self.is_equipped: return
        self.is_equipped = False
        message('Dequipped ' + self.owner.name + ' from ' + self.slot + '.', libtcod.light_yellow)

    def parse_input(self, stat, change, special=None):
        """parse input from the equipment.py and convert into useable data for the equipment"""
        if stat == None:
            pass

        else:
            stats = {
                'strength' : self.strength_bonus,
                'ac' : self.ac_bonus,
                'hp' : self.max_hp_bonus,
                'agi' : self.agi_bonus,
                'ftg' : self.max_fatigue_bonus,
                'dex' : self.dex_bonus,
                'wep_damage' : self.wep_damage,
                'cha' : self.cha_bonus }
            stats[stat] += change

        if special != None:
            fire = Special(True, False, flaming)
            death = Special(True, False, instadeath)
            explosive = Special(True, False, explode)

            specials = {
                'flaming' : fire,
                'death' : death,
                'explosive' : explosive }
            self.special = specials[special]



def player_death(player):
    """the game ended!"""
    global game_state, money
    message(player.name + " has died! His adventures come to end and your ratings boost!" , libtcod.dark_red)
    game_state = 'dead'
    player.actor.modify_rating(player.actor.fame * player.actor.fame * 100)
    money = player.actor.ratings * 10

    #transform the player into a corpse!
    player.char = '%'
    player.color = libtcod.dark_red
    msgbox(player.name + ' died and made the studio ' + str(money) + '!', CHARACTER_SCREEN_WIDTH)

def status_check(checker):
    global turn, game_state

    #check fatigue
    if turn % 5 == 0:

        if checker.fatigue <= checker.max_fatigue - 5:
            checker.fatigue += 5

        elif checker.fatigue > checker.max_fatigue - 5:
            checker.fatigue = checker.max_fatigue

        else:
            pass

    if checker.player:
        if checker.hp < checker.max_hp / 5:
            checker.owner.actor.modify_rating(5)

        else:
            pass

    for effects in checker.status_effects:
        effects.proc()

def monster_death(monster):
    """transform it into a nasty corpse! it doesn't block, can't be
    attacked and doesn't move"""
    death_message = random_monster_death_message()
    message(monster.name.capitalize() + ' ' + death_message, libtcod.dark_red)
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()

def boss_death(monster):
    """transform it into a nasty corpse! it doesn't block, can't be
    attacked and doesn't move"""
    message(monster.name.capitalize() + ' dies! You gain some fame among the viewers', libtcod.dark_red)
    player.actor.base_fame += .01
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name

    weapon = equipment.magic_weapon(dungeon_level % 2 + dungeon_level / 2)
    equipment_component = Equipment(slot='right hand', dex_bonus=weapon.dex_modifier, agi_bonus=weapon.agi_modifier, wep_damage=weapon.base_stat,
        base_type=weapon.base_type)
    equipment_component.parse_input(weapon.magic.stat, weapon.magic.change, weapon.magic.special)
    item = Object(monster.x, monster.y, weapon.char, weapon.name, weapon.color, equipment=equipment_component)
    objects.append(item)
    monster.send_to_back()


def random_monster_death_message(): #monster_type
    """defines a death message for a monster"""
    x = libtcod.random_get_int(0, 0, 3)
    if x == 0:
        return "splatters!"
    elif x == 1:
        return "is decapitated, and it's head rolls off!"
    elif x == 2:
        return "crumples over and groans it's last!"
    elif x == 3:
        return "looks suprsied as you evisrate him!"
    else:
        return "screams in agony and falls over!"

def menu(header, options, width):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

    #present the root console to the player and wait for a key-press
    libtcod.console_flush()
    key = libtcod.console_wait_for_keypress(True)

    #convert the ASCII code to an index; if it corresponds to an option, return it
    index = key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None
    if key.vk == libtcod.KEY_ENTER and key.lalt:  #(special case) Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

def inventory_menu(header):
    #show a menu with each item of the inventory as an option
    if len(inventory) == 0:
        options = ['Inventory is empty.']
    else:
        options = []
        for item in inventory:
            text = item.name
            #show additional information, in case it's equipped
            if item.equipment and item.equipment.is_equipped:
                text = text + ' (on ' + item.equipment.slot + ')'

            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(inventory) == 0: return None
    return inventory[index].item

def ability_menu(header):
    #show a menu with each of PC's spells or abilities as options
    if len(player.actor.abilities) == 0:
        options = ['You have no activatable abilities.']
    else:
        options = []
        for ability in player.actor.abilities:
            text = ability.name + " (" + str(ability.cost) + ")"
            options.append(text)

    index = menu(header, options, INVENTORY_WIDTH)

    #if an item was chosen, return it
    if index is None or len(player.actor.abilities) == 0: return None
    return player.actor.abilities[index]

def get_names_under_mouse():
    global mouse

    #return a string with the names of all objects under the mouse
    (x, y) = (mouse.cx, mouse.cy)

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and libtcod.map_is_in_fov(fov_map, obj.x, obj.y) and obj.trap == None]#don't show up if it's a TRAP!

    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def handle_keys():
    """function to get keyboard input from player to intergrate into game"""
    global key, turn;

    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif key.vk == libtcod.KEY_BACKSPACE:
        return 'exit'  #exit game

    if game_state == 'playing' and game_state != 'animation':
        #movement keys
        if key.vk == libtcod.KEY_UP or key.vk == libtcod.KEY_KP8:
            player_move_or_attack(0, -1)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_DOWN or key.vk == libtcod.KEY_KP2:
            player_move_or_attack(0, 1)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_LEFT or key.vk == libtcod.KEY_KP4:
            player_move_or_attack(-1, 0)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_RIGHT or key.vk == libtcod.KEY_KP6:
            player_move_or_attack(1, 0)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_HOME or key.vk == libtcod.KEY_KP7:
            player_move_or_attack(-1, -1)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_PAGEUP or key.vk == libtcod.KEY_KP9:
            player_move_or_attack(1, -1)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_END or key.vk == libtcod.KEY_KP1:
            player_move_or_attack(-1, 1)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_PAGEDOWN or key.vk == libtcod.KEY_KP3:
            player_move_or_attack(1, 1)
            return 'player_took_turn'
        elif key.vk == libtcod.KEY_KP5:
            turn += 1
            status_check(player.fighter)
            return 'player_took_turn'
         #do nothing, pass turn
        elif game_state != 'animation':
            #test for other keys
            key_char = chr(key.c)

            if key_char == 'g':
                #pick up an item
                for object in objects:  #look for an item in the player's tile
                    if object.x == player.x and object.y == player.y and object.item:
                        object.item.pick_up()
                        break
                return 'player_took_turn'#makes it so a turn is taken

            if key_char == 'i':
                #show the inventory; if an item is selected, use it
                chosen_item = inventory_menu('Press the key next to an item to use it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.use()
                    turn +=1
                    return 'player_took_turn'#makes it so a turn is taken
                else:
                    return 'didnt-take-turn'#just looking at the inventory doesn't take a turn

            if key_char == 'd':
                #the drop menu
                chosen_item = inventory_menu('Press the key next to an item to drop it, or any other to cancel.\n')
                if chosen_item is not None:
                    chosen_item.drop()
                    return 'didnt-take-turn'
                else:
                    return 'didnt-take-turn'

            if key_char == 'z':
                #show the inventory; if an item is selected, use it
                ability = ability_menu('Select an ability:.\n')
                if ability is not None:
                    ability.use()
                    turn +=1
                    return 'player_took_turn'#makes it so a turn is taken
                else:
                    return 'didnt-take-turn'#just looking at the inventory doesn't take a turn

            if key_char == '<':
                #go down stairs, if the player is on them
                if stairs.x == player.x and stairs.y == player.y:
                    next_level()
                return 'didnt-take-turn'#changing stances don't use a turn

            if key_char == 'c':
                #show character information
                level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
                msgbox('Character Information\n\nLevel: ' + str(player.level) + '\nExperience: ' + str(player.fighter.xp) +
                    '\nExperience to level up: ' + str(level_up_xp) + '\n\nMaximum HP: ' + str(player.fighter.max_hp) + '\n Maximum FTG: ' + str(player.fighter.max_fatigue) +
                    '\nStr: ' + str(player.fighter.strength) + '\nAgi: ' + str(player.fighter.agi) + '\nDex: ' + str(player.fighter.dex) + '\nAC: ' + str(player.fighter.ac), CHARACTER_SCREEN_WIDTH)
                return 'didnt-take-turn'#looking at char screen don't use a turn


            if key_char == 't':

                if get_equipped_in_slot('right hand').base_type == 'Bow':
                #test values
                    message('Left-click a target tile for your arrow, or right-click to cancel.', libtcod.light_cyan)
                    (x, y) = target_tile()
                    player.fighter.shoot(x, y)
                    turn += 1
                    return 'player_took_turn'#makes it so a turn is taken
                else:
                    message('No bow equiped.', libtcod.light_cyan)

            #stances
            if key_char == 's':
                display = True
                choice = None
                while display:  #keep asking until user quits
                    #
                    choice = menu('Allocate Stance Points:\nUnassiagned Points:' + str(player.fighter.stance_unassigned), ["Add to Power: " + str(player.fighter.stance_power) + ' +1 to damage done\n', 'Subtract from Power','Add to Recklessness: ' + str(player.fighter.stance_recklessness) + ' +1 to critically hit, +1 to critically miss', 'Subtract from Recklessness', 'Add to Evasiveness: ' + str(player.fighter.stance_evasiveness) + ' + 1 to be missed.', 'Subtract from Evasiveness', 'Add to Aggresiveness: ' + str(player.fighter.stance_aggresiveness) + ' +1 to hit.', 'Subtract from Aggresiveness', 'Exit Menu'], LEVEL_SCREEN_WIDTH*2)


                    if choice == 0:

                        if player.fighter.stance_unassigned > 0:
                            player.fighter.stance_power += 1
                            player.fighter.stance_unassigned -= 1
                        else:
                            pass

                    elif choice == 1:
                        if player.fighter.stance_power > 0:
                            player.fighter.stance_unassigned += 1
                            player.fighter.stance_power -= 1
                        else:
                            pass

                    elif choice == 2:
                        if player.fighter.stance_unassigned > 0:
                            player.fighter.stance_recklessness += 1
                            player.fighter.stance_unassigned -= 1
                        else:
                            pass

                    elif choice == 3:
                        if player.fighter.stance_recklessness > 0:
                            player.fighter.stance_unassigned += 1
                            player.fighter.stance_recklessness -= 1
                        else:
                            pass

                    elif choice == 4:
                        if player.fighter.stance_unassigned > 0:
                            player.fighter.stance_evasiveness += 1
                            player.fighter.stance_unassigned -= 1
                        else:
                            pass

                    elif choice == 5:
                        if player.fighter.stance_evasiveness > 0:
                            player.fighter.stance_unassigned += 1
                            player.fighter.stance_evasiveness -= 1
                        else:
                            pass

                    elif choice == 6:
                        if player.fighter.stance_unassigned > 0:
                            player.fighter.stance_aggresiveness += 1
                            player.fighter.stance_unassigned -= 1
                        else:
                            pass

                    elif choice == 7:
                        if player.fighter.stance_aggresiveness > 0:
                            player.fighter.stance_unassigned += 1
                            player.fighter.stance_aggresiveness -= 1
                        else:
                            pass
                    else:
                        display = False

                    time.sleep(.2)
                return 'didnt-take-turn'#changing stances don't use a turn
            return 'didnt-take-turn'


def make_map():
    global s_map, objects, stairs, dungeon_level

    #the list of objects with just the player
    objects = [player]

    #fill map with "blocked" tiles
    s_map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]

    rooms = []
    num_rooms = 0

    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)

        new_room = Rect(x, y, w, h)

        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break

        if not failed:
            #this means there are no intersections, so this room is valid

            #"paint" it to the map's tiles
            create_room(new_room)
            #add some contents to this room, such as monsters
            place_objects(new_room)

            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel

                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()

                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    place_traps(prev_x, new_x, prev_y, False)#place traps in the hall way

                    create_v_tunnel(prev_y, new_y, new_x)
                    place_traps(prev_y, new_y, new_x, True)

                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    place_traps(prev_y, new_y, prev_x, True)

                    create_h_tunnel(prev_x, new_x, new_y)
                    place_traps(prev_x, new_x, new_x, True)

            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1

    #create stairs at the center of the last room
    stairs = Object(new_x, new_y, '<', 'stairs', libtcod.white, always_visible=True)
    objects.append(stairs)
    stairs.send_to_back()  #so it's drawn below the monsters

def player_move_or_attack(dx, dy):
    global fov_recompute, turn

    #the coordinates the player is moving to/attacking
    x = player.x + dx
    y = player.y + dy

    #increase turn count by uno
    turn += 1
    #try to find an attackable object there
    target = None
    trap = None
    for object in objects:
        if object.fighter and object.x == x and object.y == y:
            target = object
            break

        if object.trap and object.x == x and object.y == y:
            trap  = object
            break

    #attack if target found, move otherwise
    if target is not None:
        player.fighter.attack(target)
        status_check(player.fighter)

    elif trap is not None:
        object.trap.trigger()
        player.move(dx, dy)
        fov_recompute = True
        status_check(player.fighter)
    else:
        player.move(dx, dy)
        fov_recompute = True
        status_check(player.fighter)


def from_dungeon_level(table):
    #returns a value that depends on level. the table specifies what value occurs after each level, default is 0.
    for (value, level) in reversed(table):
        if dungeon_level >= level:
            return value
    return 0

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    #now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    #finally, some centered text with the values
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
        name + ': ' + str(value) + '/' + str(maximum))

def render_all():
    """draw the information to the screen"""
    global color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute

    if fov_recompute == True:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)

        #go through all tiles, and set their background color according to the FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = s_map[x][y].block_sight
                if not visible:
                    #it's out of the player's FOV
                    if s_map[x][y].explored:
                        if wall:
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET )
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET )
                    #since it's visible, explore it
                    s_map[x][y].explored = True

    #draw all objects in the list, except the player. we want it to
    #always appear over all other objects! so it's drawn later.
    for object in objects:
        if object != player:
            object.draw()
    player.draw()

    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


    #prepare to render the GUI panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)
    libtcod.console_set_default_foreground(con, libtcod.white)

    #render status bars
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        libtcod.light_red, libtcod.darker_red)


    render_bar(1, 2, BAR_WIDTH, 'FTG', player.fighter.fatigue, player.fighter.max_fatigue,
        libtcod.light_green, libtcod.darker_green)

    render_bar(1, 3, BAR_WIDTH, player.actor.resource, player.actor.res, player.actor.max_res,
        libtcod.sky, libtcod.darker_sky)

    #show the dungeon level
    libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT, 'Dungeon level ' + str(dungeon_level))
    #show the ratings
    libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT, 'Ratings ' + str(player.actor.ratings))

    #print the game messages, one line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
        y += 1


    #display names of objects under the mouse
    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, get_names_under_mouse())


    #blit the contents of "panel" to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)


def create_room(room):
    #go through the tiles in the rectangle and make them passable
    global s_map

    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            s_map[x][y].blocked = False
            s_map[x][y].block_sight = False

def create_h_tunnel(x1, x2, y):
    global s_map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        s_map[x][y].blocked = False
        s_map[x][y].block_sight = False


def create_v_tunnel(y1, y2, x):
    global s_map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        s_map[x][y].blocked = False
        s_map[x][y].block_sight = False

def place_traps(cord1, cord2, cord3, xoy):
    """place a trap in the hall... maybe, using the x ,and x1 values from a h hall for example, and the third p is the y cordinate for a h hall,
       if it is an v hall way then xoy will be True,  """
    global traps

    chance = libtcod.random_get_int(0, 0, 100)
    if chance >= 85: #there is a 15% chance that a trap spawns in anyone hall way.

        if traps < MAX_TRAP: #and there aren't too many traps on a level already
            traps += 1
            cord = libtcod.random_get_int(0, min(cord1, cord2) + 1, max(cord1, cord2) -1)
            trap_component = Trap(trigger_function=stone_fall)
            trap = Object(cord3 if xoy else cord, cord if xoy else cord3, ' ', "Trap", libtcod.red, trap=trap_component)
            objects.append(trap)

        else: pass


def place_objects(room):
#this is where we decide the chance of each monster or item appearing.
    global bosses

    #maximum number of monsters per room
    max_monsters = from_dungeon_level([[2, 1], [3, 4], [5, 6]])

    #chance of each monster
    monster_chances = {}
    monster_chances['d1'] = from_dungeon_level([[95, 1], [0, 2]])
    monster_chances['d2'] = from_dungeon_level([[95, 2], [0, 4]])
    monster_chances['d3'] = from_dungeon_level([[95, 4], [0, 6]])
    monster_chances['d4'] = from_dungeon_level([[95, 6], [0, 8]])
    monster_chances['d5'] = from_dungeon_level([[95, 9]])
    if bosses <= MAX_BOSS:
        monster_chances['boss'] = from_dungeon_level(([[5, 2]]))
        bosses += 1

    #maximum number of items per room
    max_items = from_dungeon_level([[1, 1], [2, 4]])

    #chance of each item (by default they have a chance of 0 at level 1, which then goes up)
    item_chances = {}

    item_chances['tier1weapon'] = from_dungeon_level([[25,1], [0, 3]])
    item_chances['tier2weapon'] = from_dungeon_level([[25,3], [0, 6]])
    item_chances['tier3weapon'] = from_dungeon_level([[25,6]])
    item_chances['tier1armor'] = from_dungeon_level([[20,1], [0, 3]])
    item_chances['tier2armor'] = from_dungeon_level([[20,3], [0, 6]])
    item_chances['tier3armor'] = from_dungeon_level([[20,6]])
    item_chances['amulet of health'] = from_dungeon_level([[5, 2]])
    item_chances['heal'] = 35  #healing potion always shows up, even if all other items have 0 chance
    item_chances['lightning'] = from_dungeon_level([[25, 4]])
    item_chances['fireball'] =  from_dungeon_level([[25, 6]])
    item_chances['confuse'] =   from_dungeon_level([[10, 2]])


    #choose random number of monsters
    num_monsters = libtcod.random_get_int(0, 0, max_monsters)

    for i in range(num_monsters):
        #choose random spot for this monster
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = rutil.random_choice(monster_chances)
            if choice == 'd1':
                #create a d1 monster
                m = monster.make_monster(1)
                fighter_component = Fighter(hp=m.hp, fatigue=m.fatigue, dex=m.dex, agi=m.agi, strength=m.strength, ac=m.ac, wep_damage=m.wep_damage, death_function=monster_death, dr=m.dr)
                ai_component = BasicMonster(attack_type=m.attack_type, attack_range=m.attack_range)

                badguy = Object(x, y, m.symbol, m.name, m.color, blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'd2':
                #create a d1 monster
                m = monster.make_monster(2)
                fighter_component = Fighter(hp=m.hp, fatigue=m.fatigue, dex=m.dex, agi=m.agi, strength=m.strength, ac=m.ac, wep_damage=m.wep_damage, death_function=monster_death, dr=m.dr)
                ai_component = BasicMonster(attack_type=m.attack_type, attack_range=m.attack_range)

                badguy = Object(x, y, m.symbol, m.name, m.color, blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'd3':
                #create a d1 monster
                m = monster.make_monster(3)
                fighter_component = Fighter(hp=m.hp, fatigue=m.fatigue, dex=m.dex, agi=m.agi, strength=m.strength, ac=m.ac, wep_damage=m.wep_damage, death_function=monster_death, dr=m.dr)
                ai_component = BasicMonster(attack_type=m.attack_type, attack_range=m.attack_range)

                badguy = Object(x, y, m.symbol, m.name, m.color, blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'd4':
                #create a d1 monster
                m = monster.make_monster(4)
                fighter_component = Fighter(hp=m.hp, fatigue=m.fatigue, dex=m.dex, agi=m.agi, strength=m.strength, ac=m.ac, wep_damage=m.wep_damage, death_function=monster_death, dr=m.dr)
                ai_component = BasicMonster(attack_type=m.attack_type, attack_range=m.attack_range)

                badguy = Object(x, y, m.symbol, m.name, m.color, blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'd5':
                #create a d1 monster
                m = monster.make_monster(5)
                fighter_component = Fighter(hp=m.hp, fatigue=m.fatigue, dex=m.dex, agi=m.agi, strength=m.strength, ac=m.ac, wep_damage=m.wep_damage, death_function=monster_death, dr=m.dr)
                ai_component = BasicMonster(attack_type=m.attack_type, attack_range=m.attack_range)

                badguy = Object(x, y, m.symbol, m.name, m.color, blocks=True, fighter=fighter_component, ai=ai_component)

            elif choice == 'boss':
                #create a boss
                m = monster.make_mini_boss(dungeon_level % 2 + dungeon_level / 2)
                fighter_component = Fighter(hp=m.hp, fatigue=m.fatigue, dex=m.dex, agi=m.agi, strength=m.strength, ac=m.ac, wep_damage=m.wep_damage, death_function=boss_death, dr=m.dr)
                ai_component = BasicMonster(attack_type=m.attack_type, attack_range=m.attack_range)

                badguy = Object(x, y, m.symbol, m.name, m.color, blocks=True, fighter=fighter_component, ai=ai_component)


        objects.append(badguy)

    #choose random number of items
    num_items = libtcod.random_get_int(0, 0, max_items)

    for i in range(num_items):
        #choose random spot for this item
        x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
        y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

        #only place it if the tile is not blocked
        if not is_blocked(x, y):
            choice = rutil.random_choice(item_chances)
            if choice == 'heal':
                #create a healing potion
                item_component = Item(use_function=light_heal)
                item = Object(x, y, '!', 'healing potion', libtcod.violet, item=item_component)

            elif choice == 'lightning':
                #create a lightning bolt scroll
                item_component = Item(use_function=cast_lightning)
                item = Object(x, y, '#', 'scroll of lightning bolt', libtcod.light_yellow, item=item_component)

            elif choice == 'fireball':
                #create a fireball scroll
                item_component = Item(use_function=cast_fireball)
                item = Object(x, y, '#', 'scroll of fireball', libtcod.light_yellow, item=item_component)

            elif choice == 'confuse':
                #create a confuse scroll
                item_component = Item(use_function=cast_confuse)
                item = Object(x, y, '#', 'scroll of confusion', libtcod.light_yellow, item=item_component)

            elif choice == 'tier1weapon':
                # generate a tier 1 weapon
                weapon = equipment.make_weapon(1)#The function to make the weapon with tier 1
                equipment_component = Equipment(slot='right hand', dex_bonus=weapon.dex_modifier, agi_bonus=weapon.agi_modifier, wep_damage=weapon.base_stat, base_type=weapon.base_type)
                item = Object(x, y, weapon.char, weapon.name, weapon.color, equipment=equipment_component)

            elif choice == 'tier2weapon':
                # generate a tier 2 weapon
                weapon = equipment.make_weapon(2)#The function to make the weapon with tier 2
                equipment_component = Equipment(slot='right hand', dex_bonus=weapon.dex_modifier, agi_bonus=weapon.agi_modifier, wep_damage=weapon.base_stat, base_type=weapon.base_type)
                item = Object(x, y, weapon.char, weapon.name, weapon.color, equipment=equipment_component)

            elif choice == 'tier3weapon':
                # generate a tier 3 weapon
                weapon = equipment.make_weapon(3)#The function to make the weapon with tier 2
                equipment_component = Equipment(slot='right hand', dex_bonus=weapon.dex_modifier, agi_bonus=weapon.agi_modifier, wep_damage=weapon.base_stat, base_type=weapon.base_type)
                item = Object(x, y, weapon.char, weapon.name, weapon.color, equipment=equipment_component)

            elif choice == 'amulet of health':
                equipment_component = Equipment(slot='neck', max_hp_bonus=20)
                item = Object(x, y, '.', 'amulet of health', libtcod.yellow, equipment=equipment_component)

            elif choice == 'tier1armor':
                # generate a tier 1 armor
                armor = equipment.make_armor(1)#The function to make the armor with tier 1
                equipment_component = Equipment(slot=armor.slot, dex_bonus=armor.dex_modifier, agi_bonus=armor.agi_modifier, ac_bonus=armor.base_stat)
                item = Object(x, y, armor.char, armor.name, armor.color, equipment=equipment_component)

            elif choice == 'tier2armor':
                # generate a tier 2 armor
                armor = equipment.make_armor(2)#The function to make the armor with tier 2
                equipment_component = Equipment(slot=armor.slot, dex_bonus=armor.dex_modifier, agi_bonus=armor.agi_modifier, ac_bonus=armor.base_stat)
                item = Object(x, y, armor.char, armor.name, armor.color, equipment=equipment_component)

            elif choice == 'tier3armor':
                # generate a tier 3 armor
                armor = equipment.make_armor(3)#The function to make the armor with tier 3
                equipment_component = Equipment(slot=armor.slot, dex_bonus=armor.dex_modifier, agi_bonus=armor.agi_modifier, ac_bonus=armor.base_stat)
                item = Object(x, y, armor.char, armor.name, armor.color, equipment=equipment_component)

            objects.append(item)
            item.send_to_back()  #items appear below other objects
            item.always_visible = True  #items are visible even out-of-FOV, if in an explored area

def next_level():
    global dungeon_level, turn, traps, bosses

    #advance to the next level
    message('You take a moment to rest, and recover your strength.', libtcod.light_violet)
    player.fighter.heal(player.fighter.max_hp / 2)  #heal the player by 50%

    message('After a rare moment of peace, you descend deeper into the heart of the dungeon...', libtcod.red)
    dungeon_level += 1
    turn = 0
    traps = 0
    bosses = 0

    make_map()  #create a fresh new level
    initialize_fov()

def get_equipped_in_slot(slot):  #returns the equipment in a slot, or None if it's empty
    for obj in inventory:
        if obj.equipment and obj.equipment.slot == slot and obj.equipment.is_equipped:
            return obj.equipment
    return None

def is_blocked(x, y):
    #first test the map tile
    if s_map[x][y].blocked:
        return True

    #now check for any blocking objects
    for object in objects:
        if object.blocks and object.x == x and object.y == y:
            return True

    return False

def message(new_msg, color = libtcod.white):
    #split the message if necessary, among multiple lines
    new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

    for line in new_msg_lines:
        #if the buffer is full, remove the first line to make room for the new one
        if len(game_msgs) == MSG_HEIGHT:
            del game_msgs[0]

        #add the new line as a tuple, with the text and the color
        game_msgs.append( (line, color) )

def get_all_equipped(obj):  #returns a list of equipped items
    if obj == player:
        equipped_list = []
        for item in inventory:
            if item.equipment and item.equipment.is_equipped:
                equipped_list.append(item.equipment)
        return equipped_list
    else:
        return []  #other objects have no equipment

def closest_monster(max_range):
    #find closest enemy, up to a maximum range, and in the player's FOV
    closest_enemy = None
    closest_dist = max_range + 1  #start with (slightly more than) maximum range

    for object in objects:
        if object.fighter and not object == player and libtcod.map_is_in_fov(fov_map, object.x, object.y):
            #calculate distance between this object and the player
            dist = player.distance_to(object)
            if dist < closest_dist:  #it's closer, so remember it
                closest_enemy = object
                closest_dist = dist
    return closest_enemy

def target_tile(max_range=None):
    #return the position of a tile left-clicked in player's FOV (optionally in a range), or (None,None) if right-clicked.
    global key, mouse
    while True:
        #render the screen. this erases the inventory and shows the names of objects under the mouse.
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()
        (x, y) = (mouse.cx, mouse.cy)

        if mouse.rbutton_pressed or key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

        #accept the target if the player clicked in FOV, and in case a range is specified, if it's in that range
        if (mouse.lbutton_pressed and libtcod.map_is_in_fov(fov_map, x, y) and
            (max_range is None or player.distance(x, y) <= max_range)):
            return (x, y)

def target_monster(max_range=None):
    #returns a clicked monster inside FOV up to a range, or None if right-clicked
    while True:
        (x, y) = target_tile(max_range)
        if x is None:  #player cancelled
            return None

        #return the first clicked monster, otherwise continue looping
        for obj in objects:
            if obj.x == x and obj.y == y and obj.fighter and obj != player:
                return obj



def new_mission():
    global player, inventory, game_msgs, game_state, dungeon_level, turn, animation, traps, bosses, studio

    #create object representing the player
    fighter_component = Fighter(hp=100, fatigue=100, agi=10, dex=12, strength=10, death_function=player_death, player=True)
    actor_component = Actor()
    player_name = rutil.otherworld_names()
    player = Object(0, 0, '@', player_name, libtcod.white, blocks=True, fighter=fighter_component, actor=actor_component)
    player.level = 1


    #the list of objects starting with the player
    objects = [player]

    studio = False #quick play
    turn = 0
    game_state = 'playing' #game state global variable
    #create the list of game messages and their colors, starts empty
    game_msgs = []
    #set teh dungeon level
    dungeon_level = 1

    bosses = 0 #ammount of bosses on map

    #a variable that determines the traps for easy checks
    traps = 0

    #generate the map
    make_map()

    initialize_fov()#instialize fov map

    #inventory list
    inventory = []

    #initial equipment: a dagger
    equipment_component = Equipment(slot='right hand', wep_damage=4, agi_bonus=1, dex_bonus=1)
    dagger = Object(0, 0, '-', 'Rusty dagger (4, 1, 1)', libtcod.sky, equipment=equipment_component)
    inventory.append(dagger)
    equipment_component.equip()
    dagger.always_visible = True

    #initial equipment: cloth armor
    equipment_component1 = Equipment(slot='body', agi_bonus=2)
    armor = Object(0, 0, '#', 'clothes (0, 0, 2)', libtcod.sky, equipment=equipment_component1)
    inventory.append(armor)
    equipment_component1.equip()
    armor.always_visible = True

    #welcome message
    message(player.name + " arrives to his mission... datastream intialized.", libtcod.white)

def new_mission_studio(actor):
    global player, inventory, game_msgs, game_state, dungeon_level, turn, animation, traps, bosses, studio, money

    #the list of objects starting with the player
    player = actor.actor
    objects = [player]

    studio = True #special gamesdtate for studionisms
    turn = 0
    game_state = 'playing' #game state global variable
    #create the list of game messages and their colors, starts empty
    game_msgs = []
    #set teh dungeon level
    dungeon_level = 1
    money = 0.0

    bosses = 0 #ammount of bosses on map

    #a variable that determines the traps for easy checks
    traps = 0

    #generate the map
    make_map()

    initialize_fov()#instialize fov map

    #inventory list
    inventory = []

    #initial equipment: a dagger
    equipment_component = Equipment(slot='right hand', wep_damage=4, agi_bonus=1, dex_bonus=1)
    dagger = Object(0, 0, '-', 'Rusty dagger (4, 1, 1)', libtcod.sky, equipment=equipment_component)
    inventory.append(dagger)
    equipment_component.equip()
    dagger.always_visible = True

    #initial equipment: cloth armor
    equipment_component1 = Equipment(slot='body', agi_bonus=2)
    armor = Object(0, 0, '#', 'clothes (0, 0, 2)', libtcod.sky, equipment=equipment_component1)
    inventory.append(armor)
    equipment_component1.equip()
    armor.always_visible = True

    #welcome message
    message(player.name + " arrives to his mission... datastream intialized.", libtcod.white)


def check_level_up():
    #see if the player's experience is enough to level-up
    level_up_xp = LEVEL_UP_BASE + player.level * LEVEL_UP_FACTOR
    if player.fighter.xp >= level_up_xp:
        #it is! level up
        player.level += 1
        player.fighter.xp -= level_up_xp
        message('Your battle skills grow stronger! You reached level ' + str(player.level) + '!', libtcod.yellow)

        choice = None
        while choice == None:  #keep asking until a choice is made
            choice = menu('Level up! Choose a stat to raise:\n',
                ['Constitution (+20 HP, from ' + str(player.fighter.base_max_hp) + ')',
                'Strength (+1 attack, from ' + str(player.fighter.base_strength) + ')',
                'Agility (+1 agi, from ' + str(player.fighter.base_agi) + ')',
                'Dexeterity (+ 1 dex from ' +  str(player.fighter.base_dex) + ')'], LEVEL_SCREEN_WIDTH)

        if choice == 0:
            player.fighter.base_max_hp += 20
            player.fighter.hp += 20
        elif choice == 1:
            player.fighter.base_strength += 1
        elif choice == 2:
            player.fighter.base_agi += 1
        elif choice == 3:
            player.fighter.base_dex += 1



def initialize_fov():
    global fov_recompute, fov_map
    fov_recompute = True

    libtcod.console_clear(con)  #unexplored areas start black (which is the default background color)

    #create the FOV map, according to the generated map
    fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            libtcod.map_set_properties(fov_map, x, y, not s_map[x][y].block_sight, not s_map[x][y].blocked)


def play_rogue():
    """Game Main Loop function for rogue"""
    global key, mouse

    player_action = None

    mouse = libtcod.Mouse()
    key = libtcod.Key()
    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        render_all()

        libtcod.console_flush()
        check_level_up()

        #erase all objects at their old locations, before they move
        for object in objects:
            object.clear()


        #handle keys and exit game if needed
        player_action = handle_keys()
        if player_action == 'exit':
            save_game()
            time.sleep(.01) #hack to not brake game
            break

        #let monsters take their turn
        if game_state == 'playing' and player_action != 'didnt-take-turn' and player_action == 'player_took_turn':
            for object in objects:
                if object.ai:
                    object.ai.take_turn()


def load_game():
    #open the previously saved shelve and load the game data
    global s_map, objects, player, inventory, game_msgs, game_state, stairs, dungeon_level

    file = shelve.open('savegame', 'r')
    s_map = file['s_map']
    objects = file['objects']
    player = objects[file['player_index']]  #get index of player in objects list and access it
    inventory = file['inventory']
    game_msgs = file['game_msgs']
    game_state = file['game_state']
    stairs = objects[file['stairs_index']]
    dungeon_level = file['dungeon_level']
    file.close()

    initialize_fov()


def msgbox(text, width=50):
    menu(text, [], width)  #use menu() as a sort of "message box"

def save_game():
    #open a new empty shelve (possibly overwriting an old one) to write the game data
    file = shelve.open('savegame', 'n')
    file['s_map'] = s_map
    file['objects'] = objects
    file['player_index'] = objects.index(player)  #index of player in objects list
    file['inventory'] = inventory
    file['game_msgs'] = game_msgs
    file['game_state'] = game_state
    file['stairs_index'] = objects.index(stairs)
    file['dungeon_level'] = dungeon_level
    file.close()

#SPELLS AND ABILITIES **************************************

def light_heal():
    #heal the player
    if player.fighter.hp == player.fighter.max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'

    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(40)

def beer():

    if player.fighter.fatigue == player.fighter.max_fatigue:
        message('You are already at full fatigue!', libtcod.red)
        return 'cancelled'

    message('The sweet beer goes down easy! The viewers love it!')
    player.fighter.restore(20)
    player.actor.modify_rating(10.0)

def cast_lightning():
    #find closest enemy (inside a maximum range) and damage it
    monster = closest_monster(5)#find closest monster in range 5
    if monster is None:  #no enemy found within maximum range
        message('No enemy is close enough to strike.', libtcod.red)
        return 'cancelled'

    #zap it!
    message('A lighting bolt strikes the ' + monster.name + ' with a loud thunder! The damage is '
        + str(40) + ' hit points.', libtcod.light_blue)
    monster.fighter.take_damage(40)

def cast_confuse():

    #ask the player for a target to confuse
    message('Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan)
    monster = target_monster(8)
    if monster is None: return 'cancelled'

    #replace the monster's AI with a "confused" one; after some turns it will restore the old AI
    old_ai = monster.ai
    monster.ai = ConfusedMonster(old_ai)
    monster.ai.owner = monster  #tell the new component who owns it
    message('The eyes of the ' + monster.name + ' look vacant, as he starts to stumble around!', libtcod.light_green)


def cast_fireball():
    #ask the player for a target tile to throw a fireball at
    message('Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan)
    (x, y) = target_tile()
    if x is None: return 'cancelled'
    message('The fireball explodes, burning everything within ' + str(3) + ' tiles!', libtcod.orange)

    for obj in objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= 3 and obj.fighter:
            message('The ' + obj.name + ' gets burned for ' + str(25) + ' hit points.', libtcod.orange)
            obj.fighter.take_damage(25)

def burn(burnee):
    message(burnee.owner.name + ' burns for 3 damage!', libtcod.flame)
    burnee.take_damage(3) #burn someone for three damage! OH SNAP ~a status effect, effect.


def charge():
    message('Left-click a monster for your charge, or right-click to cancel. R:5', libtcod.light_cyan)
    monster = target_monster(5)
    if monster is None: return 'cancelled'

    while player.distance_to(monster) >= 2:
        player.clear()
        player.move_towards(monster.x, monster.y)
        render_all()
        libtcod.console_flush()

    message(player.name + ' clashes into ' + monster.name + '!')
    player.fighter.strength += 4
    player.fighter.attack(monster)
    player.fighter.strength -= 4 #remove the bonus strength
    libtcod.console_flush()

def cleave():
    message('Left-click a monster to attack, or right click to cancel. R:2', libtcod.light_cyan)
    monster = target_monster(2)
    if monster is None: return 'cancelled'
    message('Left-click another monster to recieve your cleave! ... or right click to cancel.', libtcod.light_cyan)
    monster2 = target_monster(2)
    if monster2 is None or monster2 is monster: return 'cancelled'

    message(player.name + ' cleaves ' + monster.name + ' and ' + monster2.name + '!', libtcod.dark_red)
    player.fighter.attack(monster)
    monster2.fighter.take_damage(player.fighter.strength / 2)
    message(monster2.name + ' takes ' + str(player.fighter.strength / 2) + ' cleave damage!', libtcod.dark_red)


def whirlwind():
    message(player.name + ' spins around flailing his weapon about like a mad man!', libtcod.dark_red)
    for obj in objects:  #HIT EVERYONE
        if obj.distance(player.x, player.y) <= 2 and obj.fighter and not obj.fighter.player:
            message('The ' + obj.name + ' gets hit for ' + str(15) + ' damage.', libtcod.dark_red)
            obj.fighter.take_damage(15)

def devastate():
    pass

def rend():
    message('Left click a target to rend, or right click to cancel. R:2', libtcod.light_cyan)
    monster = target_monster(2)
    if monster is None: return 'cancelled'
    effect = StatusEffect(function=bleed, t = 0, run_time = 3)
    monster.fighter.add_status_effect(effect)

def bleed(bleedee):
    message(bleedee.owner.name + ' bleeds for 5 damage!', libtcod.dark_red)
    bleedee.take_damage(5)
    
#***************************Specials***********************************
def flaming(attcker, defender): #attacker isn't used in this code, but it could be later!!!
    if rutil.roll(100) > 50:
        effect = StatusEffect(function=burn, t = 0, run_time = 3)
        defender.fighter.add_status_effect(effect)
        player.actor.modify_rating(.5) #PEOPLE LOVE TO WATCH 'EM BURN!
    else: pass

def instadeath(attacker, defender): #lololololoolololololololololol
    chance = rutil.roll(100)
    if chance >= 100:
        player.actor.modify_rating(100)
        message(defender.name + " explodes into a a thousand pieces spraying blood and gore everywhere!", libtcod.magenta)
        defender.fighter.take_damage(defender.fighter.max_hp)
    elif chance <= 2:
        player.actor.modify_rating(100)
        message(attacker.owner.name + " screams in horror as the weapon sucks his soul from his body!", libtcod.magenta)
        attacker.take_damage(attacker.max_hp)

def explode(attacker, defender): #so many trolley magic items... at least this one could be cool with a bow
    x, y = defender.x, defender.y

    for obj in objects:  #damage every fighter in range, including the player
        if obj.distance(x, y) <= 3 and obj.fighter:
            message(obj.name + ' is caught in the explosion for ' + str(5) + ' hit points!', libtcod.orange)
            obj.fighter.take_damage(5)


#***************************TRAPS**************************************
def stone_fall():
    chance = rutil.roll(100)
    if chance > 100 - player.fighter.agi * 2:
        message('A stone falls from the ceiling, and you just barely evade it!', libtcod.yellow)
    else:
        message('A stone falls from the celing! It deals 10 damage to you!', libtcod.red)
        player.fighter.take_damage(10)

#*************************PATHFINDING***********************************
def astar_func(xFrom , yFrom , xTo , yTo , userData):
    if not is_blocked(xTo, yTo):
        return 1.0
    else:
        return 0.0
def new_path():
    return libtcod.path_new_using_function(MAP_WIDTH, MAP_HEIGHT , astar_func)

def destroy_path(path):
    path_delete(path)


#******************************Intialization****************************

libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Otherworld Rogue', False)
libtcod.sys_set_fps(LIMIT_FPS)
con = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)

mouse = libtcod.Mouse()
key = libtcod.Key()


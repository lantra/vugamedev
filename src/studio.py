"""The classes for setting up the studio."""
import libtcodpy as libtcod
import rogueutil as rutil
import math
import textwrap
import shelve
import locale
import roguet
import time


TAXES = .015

SCREEN_WIDTH = 80 #constant for screen width
SCREEN_HEIGHT = 50 #constant for screen height

MAIN_WIDTH = 80 #constant for the map width
MAIN_HEIGHT = 43 #constant for the map height

PANEL_HEIGHT = 7 # constant for teh panel, same as in roguelike portion
PANEL_Y = 43

class Object:
    def __init__(self, name, x, y, char, color, building_component=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.building_component = building_component

    def draw(self):
        libtcod.console_set_default_foreground(s_con, self.color)
        libtcod.console_put_char(s_con, self.x, self.y, self.char, libtcod.BKGND_NONE)

class Studio:
    def __init__ (self):
        self.name = "Test"
        self.money = 0.0
        self.base_worth = 0.0
        self.marketing_value = 0.0
        self.day = 1
        self.base_month = 1
        self.base_year = 3031

        self.actors = []
        self.buildings = []
        self.dead_actors = {}

        for i in range(5):
            actor = Actor()
            self.actors.append(actor)

        building_c = Building(100000.00)
        building = Object('Central Studio', 35, 35, 'S', libtcod.gold, building_c)
        self.buildings.append(building)
        objects.append(building)
        self.dead_actors['Cain'] = 1890131.30

        locale.setlocale( locale.LC_ALL, '' )#too lazy

    @property
    def worth(self):
        w = self.base_worth
        for building in self.buildings:
            w += building.building_component.value

        w += self.money/4

        return w

    def buy(self, x):
        if x > self.money:
            return "cancel"

        else:
            self.money -= x
            return 'succsess!'

    def make_money(self, x):
        self.money += x - (x * TAXES)

    def advance_day(self, x):
        self.day += 1


class Actor:
    def __init__ (self):
        fighter_component = roguet.Fighter(hp=100, fatigue=100, agi=10, dex=12, strength=10, death_function=roguet.player_death, player=True)
        actor_component = roguet.Actor()
        self.name = rutil.otherworld_names()
        self.actor = roguet.Object(0, 0, '@', self.name, libtcod.white, blocks=True, fighter=fighter_component, actor=actor_component)
        self.actor.level = 1


class Building:
    def __init__ (self, value, effect=None):
        self.value = value
        self.effect = None

    def buy_building(self):
        pass

    def use_effect(self):
        pass

def new_studio():
    global objects, studio

    objects = []
    studio = Studio()


def play_studio():
    global s_game_state, s_key, s_mouse


    s_player_action = None
    s_game_state = 'studio'

    s_mouse = libtcod.Mouse()
    s_key = libtcod.Key()
    while not libtcod.console_is_window_closed():
        #render the screen
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,s_key,s_mouse)
        s_render_all()

        s_player_action = s_handle_keys()
        if s_player_action == 'exit':
            break

        if not studio.actors:
            rutil.msgbox('You are out of actors and have lost the game...!', 24, s_con)


def s_handle_keys():
    global s_mouse, s_key



    if s_key.vk == libtcod.KEY_ENTER and s_key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

    elif s_key.vk == libtcod.KEY_BACKSPACE:
        return 'exit'  #exit game

    if s_game_state == 'studio':

        key_char = chr(s_key.c)

        if key_char == 'b': # see things u can build... not that it does anything
            choice = rutil.menu("Building Menu: (Place Holder Only)", ['New Studio: $300,000.00'], 50, s_con)


        if key_char == 'm': # see missions
            choice = rutil.menu("Pick a Mission: ", ['Endless'], 50, s_con)

            if choice == 0:
                time.sleep(.1)
                actor_options = [] #make a list to store the names of the actors to be selected
                for actor in studio.actors:
                    actor_options.append(actor.name)
                choice2 = rutil.menu("Pick an Actor: ", actor_options, 24, s_con)

                actor = studio.actors.pop(choice2)
                roguet.new_mission_studio(actor)
                roguet.play_rogue()
                studio.make_money(roguet.money)
                studio.dead_actors[actor.name] = roguet.money

        if key_char == 'g':
            string = ""
            for key in studio.dead_actors:
                string += "\n" + key + " : " + locale.currency(studio.dead_actors[key], grouping=True)

            rutil.msgbox("Graveyard:" + string, 50, s_con)


        if key_char == 'h': #hire a new actor
            choice = rutil.menu("Hire a new Actor? : ", ['Yes (Cost: $10,000)', 'No'], 24, s_con)

            if choice == 0:
                if studio.buy(10000.00) != 'cancel':
                    new_actor = Actor()
                    studio.actors.append(new_actor)

        if key_char == 'a': # see actors
            string = "Active Actors"
            for actor in studio.actors:
                string += "\n" + actor.name
            rutil.msgbox(string, 50, s_con)

def build_cords():
    global s_key, s_mouse

    while True:
        #render the screen. this erases the menu
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,key,mouse)
        s_render_all()
        (x, y) = (s_mouse.cx, s_mouse.cy)

        if s_mouse.rbutton_pressed or s_key.vk == libtcod.KEY_ESCAPE:
            return (None, None)  #cancel if the player right-clicked or pressed Escape

        "accept the target if..."
        if s_mouse.lbutton_pressed and x < SCREEN_WIDTH and y < SCREEN_HEIGHT - PANEL_HEIGHT:
            for object in objects:
                if x == object.x and y == object.y:
                    return 'canceled'
            return (x, y)


def s_render_all():

    libtcod.console_flush()

    #blit the contents of "con" to the root console
    libtcod.console_blit(s_con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

    for object in objects:
        object.draw()


    #prepare to render the GUI panel
    libtcod.console_set_default_background(s_panel, libtcod.black)
    libtcod.console_clear(s_panel)
    libtcod.console_set_default_foreground(s_con, libtcod.white)


    libtcod.console_hline(s_panel, 0, 0, 100, flag=libtcod.BKGND_NONE)
    libtcod.console_print_ex(s_panel, 0, 1, libtcod.BKGND_NONE, libtcod.LEFT, 'Money: ' + locale.currency(studio.money, grouping=True))
    libtcod.console_print_ex(s_panel, 0, 2, libtcod.BKGND_NONE, libtcod.LEFT, 'Worth: ' + locale.currency(studio.worth, grouping=True))
    libtcod.console_print_ex(s_panel, 0, 3, libtcod.BKGND_NONE, libtcod.LEFT, 'Controls: view (a)ctors, (b)uild, (m)issions, (h)ire new actors')
    libtcod.console_print_ex(s_panel, 0, 4, libtcod.BKGND_NONE, libtcod.LEFT, 'Year: ' + str(studio.base_year) + ' Month: ' + str(studio.base_month) + ' Day: ' + str(studio.day))



    #blit the contents of "panel" to the root console
    libtcod.console_blit(s_panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

#intialize this component
s_panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
s_con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT - PANEL_HEIGHT)

s_mouse = libtcod.Mouse()
s_key = libtcod.Key()

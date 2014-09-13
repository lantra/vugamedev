"""used to store functions that aren't using global varibles"""

import libtcodpy as libtcod
from pygame import mixer



def random_choice_index(chances):  #choose one option from list of chances, returning its index
    #the dice will land on some number between 1 and the sum of the chances
    dice = libtcod.random_get_int(0, 1, sum(chances))

    #go through all chances, keeping the sum so far
    running_sum = 0
    choice = 0
    for w in chances:
        running_sum += w

        #see if the dice landed in the part that corresponds to this choice
        if dice <= running_sum:
            return choice
        choice += 1

def random_choice(chances_dict):
    #choose one option from dictionary of chances, returning its key
    chances = chances_dict.values()
    strings = chances_dict.keys()

    return strings[random_choice_index(chances)]

def otherworld_names():
    libtcod.namegen_parse('names/jice_fantasy.cfg')
    choice = libtcod.random_get_int(0, 1, 2)

    if choice == 1:
        name = libtcod.namegen_generate_custom('Fantasy male','$s$m$e')

    if choice == 2:
        name = libtcod.namegen_generate_custom('Fantasy male','$s$e')

    libtcod.namegen_destroy()
    return name

def otherworld_boss_names():
    libtcod.namegen_parse('names/jice_celtic.cfg')
    choice = libtcod.random_get_int(0, 1, 2)

    if choice == 1:
        name = libtcod.namegen_generate_custom('Celtic male','$s$m$e_$p')

    if choice == 2:
        name = libtcod.namegen_generate_custom('Celtic male','$s$e_$p')

    libtcod.namegen_destroy()
    return name

def play_music(track):
    pass

def roll(die):
    roll = libtcod.random_get_int(0, 1, die)
    return roll

def menu(header, options, width, con):
    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = libtcod.console_get_height_rect(con, 0, 0, width, 50, header)
    if header == '':
        header_height = 0
    height = len(options) + header_height

    #create an off-screen console that represents the menu's window
    window = libtcod.console_new(width, height)

    #print the header, with auto-wrap
    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.black, libtcod.LEFT, header)

    #print all the options
    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = '(' + chr(letter_index) + ') ' + option_text
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
        y += 1
        letter_index += 1

    #blit the contents of "window" to the root console
    x = 80 / 2 - width/2
    y = 50 / 2 - height/2
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

def msgbox(text, width, con):
    menu(text, [], width, con)






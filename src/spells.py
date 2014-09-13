"""This document will contain all the spells in the game to avoid clutter"""
import libtcodpy as libtcod
import rogueutil as rutil


HEAL_AMMOUNT = 20 #the base heal ammount


   
def light_heal(player, curhp, max_hp, message = None):
    #heal the player
    if curhp == max_hp:
        message('You are already at full health.', libtcod.red)
        return 'cancelled'
 
    message('Your wounds start to feel better!', libtcod.light_violet)
    player.fighter.heal(HEAL_AMMOUNT * 20)





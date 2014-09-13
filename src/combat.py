import rogueutil as rutil
import libtcodpy as libtcod

def roll_to_hit(attacker, defender, messagefunction, player_actor):
    roll = rutil.roll(100)
    atck_bonus = fatigue_bonus(defender.fighter.fatigue, defender.fighter.max_fatigue)
    defender_bonus = fatigue_bonus(attacker.fatigue, attacker.max_fatigue)
    
    if roll == 100: #if the roll is 100, the attacker scores a devastating critical
        devastating_crit(attacker, defender, messagefunction)
        player_actor.modify_rating(10)
        return 'hit'

    elif roll >= 96 - attacker.stance_recklessness: #if the roll is > or = 96, the attacker scores a regular critical
        critical_hit(attacker, defender, messagefunction)
        player_actor.modify_rating(5)
        return 'hit'

    elif roll <= 1 + attacker.stance_recklessness: 
        attacker.fatigue_damage(10)
        messagefunction(attacker.owner.name + ' misses ' + defender.name + "horribly!", libtcod.yellow)
        player_actor.modify_rating(3)
        return 'miss'

    elif roll >= 50 - ((attacker.dex + atck_bonus + attacker.stance_aggresiveness) - (defender.fighter.agi + defender_bonus + defender.fighter.stance_evasiveness)):
    #if the attackers dexterity skill and if his target is tried (see fatigue_bonus) is larger than the defender's agility
    #and the bonus if the attacker is tired.
        damage(attacker, defender, messagefunction)
        return 'hit'

    else:
        attacker.fatigue_damage(2)
        messagefunction(attacker.owner.name + ' misses ' + defender.name + "!", libtcod.yellow)
        return 'miss'


def roll_to_rhit(attacker, defender, messagefunction, player_actor):
    roll = rutil.roll(100)
    atck_bonus = fatigue_bonus(defender.fighter.fatigue, defender.fighter.max_fatigue)
    defender_bonus = fatigue_bonus(attacker.fatigue, attacker.max_fatigue)
    
    if roll == 100: #if the roll is 100, the attacker scores a devastating critical
        devastating_crit(attacker, defender, messagefunction)
        player_actor.modify_rating(10)
        return 'hit'

    elif roll >= 96 - attacker.stance_recklessness: #if the roll is > or = 96, the attacker scores a regular critical
        critical_hit(attacker, defender, messagefunction)
        player_actor.modify_rating(5)
        return 'hit'

    elif roll <= 1 + attacker.stance_recklessness: 
        messagefunction(attacker.owner.name + ' misses ' + defender.name + "horribly!", libtcod.yellow)
        player_actor.modify_rating(3)
        return 'miss'

    elif roll >= 50 - ((attacker.dex + atck_bonus + attacker.stance_aggresiveness) - (defender.fighter.agi + defender_bonus + defender.fighter.stance_evasiveness)):
    #if the attackers dexterity skill and if his target is tried (see fatigue_bonus) is larger than the defender's agility
    #and the bonus if the attacker is tired.
        damage(attacker, defender, messagefunction)
        return 'hit'

    else:
        messagefunction(attacker.owner.name + ' misses ' + defender.name + "!", libtcod.yellow)
        return 'miss'

def fatigue_bonus(fatigue, max_fatigue):
    if fatigue < max_fatigue / 5:
        bonus = 3
        return bonus # if fatigue is less than 20% of the max, you are modertly tired

    elif fatigue < max_fatigue / 10:
        bonus = 5
        return bonus #if fatigue is less than 10% of the max, you are very tired 

    elif fatigue == 0:
        bonus = 10
        return bonus #if fatigue is 0 you are extremly tired therefore extremly vunerable

    else:
        bonus = 0
        return bonus


def devastating_crit(attacker, defender, messagefunction):
    #finding a chinx in the armor and DEVESTATING THEM (cutting open an artery or something)
    max_wep = attacker.wep_damage 
    damage = (max_wep + attacker.strength) * 2 + attacker.stance_power
    messagefunction(attacker.owner.name + ' devastates ' + defender.name + ' for ' + str(damage) + "!", libtcod.red) 
    defender.fighter.take_damage(damage)


def critical_hit(attacker, defender, messagefunction):
    #finding a chinx in the armor
    max_wep = attacker.wep_damage 
    damage = (max_wep + attacker.strength) + attacker.stance_power
    messagefunction(attacker.owner.name + ' critically hits ' + defender.name + ' for ' + str(damage) + "!", libtcod.red)
    defender.fighter.take_damage(damage)


def damage(attacker, defender, messagefunction):
    max_wep = attacker.wep_damage 
    damage = rutil.roll(max_wep) + (attacker.strength/4) + attacker.stance_power
    #check defender fatigue for ac vulerabilties
    if defender.fighter.fatigue == 0:
        def_ac = defender.fighter.ac / 2
    
    else:    
       def_ac = defender.fighter.ac
   
    damage = (rutil.roll(max_wep) + attacker.strength) - defender.fighter.ac

    if damage <= 0:
        damage = 2 + attacker.stance_power
        if defender.fighter.fatigue > damage:
            defender.fighter.fatigue_damage(damage)
            messagefunction(attacker.owner.name + ' blow glances off of ' + defender.name + ' for ' + str(damage) + ' fatigue damage!', libtcod.yellow)
        else:
            defender.fighter.take_damage(damage)
            messagefunction(attacker.owner.name + ' blow breaks through the defences of ' + defender.name + ' for ' + str(damage) + ' damage!', libtcod.yellow)            

    elif damage >= defender.fighter.fatigue:
        messagefunction(attacker.owner.name + ' hits ' + defender.name + ' for ' + str(damage) + "!", libtcod.yellow)
        damage -= defender.fighter.fatigue
        defender.fighter.fatigue = 0
        defender.fighter.take_damage(damage)


    else:
        defender.fighter.fatigue_damage(damage)
        messagefunction(attacker.owner.name + ' hits ' + defender.name + ' for ' + str(damage) + "!", libtcod.yellow)
        

 

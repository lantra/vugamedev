import libtcodpy as libtcod
import studio
import rogueutil as rutil


def main_menu():
    img = libtcod.image_load('menu_background.png')

    while not libtcod.console_is_window_closed():
        #show the background image, at twice the regular console resolution
        libtcod.image_blit_2x(img, 0, 0, 0)

        #show the game's title, and some credits!
        libtcod.console_set_default_foreground(0, libtcod.light_yellow)
        libtcod.console_print_ex(0, studio.roguet.SCREEN_WIDTH/2, studio.roguet.SCREEN_HEIGHT/2-4, libtcod.BKGND_NONE, libtcod.CENTER,
            'OTHERWORLD')
        libtcod.console_print_ex(0, studio.roguet.SCREEN_WIDTH/2, studio.roguet.SCREEN_HEIGHT-2, libtcod.BKGND_NONE, libtcod.CENTER,
            'By Lantra')


        #play music
        rutil.play_music('music/track1.mp3')

        #show options and wait for the player's choice
        choice = studio.roguet.menu('', ['Quick Game', 'Continue last Quick Game', 'Studio Mode Test', 'Quit'], 30)

        if choice == 0:  #new game
            studio.roguet.new_mission()
            studio.roguet.play_rogue()
        if choice == 1:  #load last game
            try:
                studio.roguet.load_game()
            except:
                rutil.msgbox('\n No saved game to load.\n', 24)
                continue
            studio.roguet.play_rogue()

        if choice == 2:
            studio.new_studio()
            studio.play_studio()

        elif choice == 3:  #quit
            break

main_menu()


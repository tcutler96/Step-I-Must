from scripts.assets import Assets
from scripts.utilities import Utilities
from scripts.display import Display
from scripts.shaders import Shaders
from scripts.audio import Audio
from scripts.events import Events
from scripts.transition import Transition
from scripts.text_handler import TextHandler
from scripts.menu import Menu
from game_states.splash import Splash
from game_states.main_menu import MainMenu
from game_states.game import Game
from game_states.level_editor import LevelEditor
import pygame as pg
import sys
import os


# add glow effect to hud layer
# add animation to 'other' images such as cell marker
# look into loop hero noise transition shader...
# reset asset animation counter when we return to main menu?
# neaten the cursor sprite up a bit
# rework scrollbar images to better fit the theme, antialias the edges?
# starting the game in debug mode does not set steps correctly...
# middle clicking a wall in the level editor crashes the game...
# if we draw text one letter at a time (with a short delay), centred on a position, might make a cool way of displaying speech text...
# rescale map elements and have them fade in and out when map opened and closed...
# add level with numerical code written with barriers that tells the secret to beating the level...
# add secret where opening a fully explored map on a particular level reveals a secret, the map tiles point towards something...
# add secret with a hint on a sign that says 'fill in the gap on the map in the first level' or something a bit more cryptic, which requires the player to go back to the first level in the first world,
# and move such that they are in the empty gap on the map when it is overlayed onto the level, this triggers a portal to level (-1, 0) for a secret (maybe add cheeses to world 1?)...
# add a portal nexts to the sign that gives the original hint that takes us to level (-1, 1)...
# add room that starts very pixelated (very hard to tell what anything is) but get clearer/ less pixelated as the player moves towards some secret spot in the level...
# add effect the end of the first game, as the player moves forward, the level gets more and more pixelated until they are standing on the teleporter to take them to the second game...
# have collectable text move upwards on the screen and dont limit player movement...
# spawning ontop of a collectable (seting respawn while in debug mode and so not collecting collectable) breaks the level loading, steps arent set properly...
# loading game in debug mode crashes when you try to take a step...
# clicking window x does not close window while mid transition...
# draw sign text as pixelated until it can be decoded?
# separate level into distinct display layers that can be controlled individually (level, player, text?)
# restarting level or quitting game while map is switching breaks it...
# in the game, always draw things to the screen whether the map or menu is open, so that can see them when the level is blurred...
# have game blur when the map opens take ~30 frames/ 0.5 seconds
# add main menu title sprite, remove title from menu data and then just draw sprite from main menu or integrate into menu class...
# add sprite entry instead of title to draw a sprite to the screen instead of drawing text...
# make text element shadows move left to right on a 1 second cycle...
# add audio to cutscenes, make cutscenes more interactive...
# level editor, placing certain cells spam the sound effect (walls, dead player on flag)...
# old levels dont have a lock parameter, not sure if this is a problem...
# fade mouse in and out...
# grey shader isnt applied if we are dead sliding over ice, think thats because we only activate shader when we have no steps, not no players...
# add multiple save files, just need to have multiple data jsons that we can switch between...
# pressing play instead goes to a select save menu, which displays progression percentage in menu button...
# change game input detection so that we can either use 'wasd' or the arrow keys, or just allow both at the same time...


class Main:
    def __init__(self):
        # pg.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pg.init()
        self.fps = 60
        self.true_fps = self.fps
        self.low_fps = False
        self.clock = pg.time.Clock()
        self.runtime_frames = 0
        self.runtime_seconds = 0
        self.sprite_size = 16
        self.assets_path = os.path.join(os.path.abspath(os.curdir), 'assets')
        self.assets = Assets(main=self)
        self.utilities = Utilities(main=self)
        self.display = Display(main=self)
        self.shaders = Shaders(main=self)
        self.audio = Audio(main=self)
        self.events = Events(main=self)
        self.transition = Transition(main=self)
        self.text_handler = TextHandler(main=self)
        self.menu_state = 'title_screen'
        self.menu_states = {menu_name: Menu(main=self, menu_name=menu_name, menu_data=menu_data) for menu_name, menu_data in self.assets.settings['menus'].items()}
        self.game_state = 'splash'
        self.game_states = {'splash': Splash(main=self), 'main_menu': MainMenu(main=self), 'game': Game(main=self), 'level_editor': LevelEditor(main=self)}
        self.game_states[self.game_state].start_up()
        self.debug = False
        self.testing = True
        self.draw_gol = False
        self.clear_gol = False
        self.conway = 0

    def change_game_state(self, game_state):
        if game_state != self.game_state:
            if game_state == 'quit':
                self.quit()
            elif game_state in self.game_states:
                previous_game_state = self.game_state
                self.game_state = game_state
                self.game_states[game_state].start_up(previous_game_state=previous_game_state)

    def change_menu_state(self, menu_state=None):
        if menu_state != self.menu_state:
            if menu_state is None or menu_state in self.menu_states:
                self.menu_state = menu_state
                if self.menu_state in self.menu_states:
                    self.menu_states[self.menu_state].start_up()

    def update_choose_level_menu(self):
        self.assets.update_choose_level_menu()
        self.menu_states['choose_level'] = Menu(main=self, menu_name='choose_level', menu_data=self.assets.settings['menus']['choose_level'])

    def run(self):
        while True:
            self.update()
            self.draw()
            self.clock.tick(self.fps)

    def update_game_of_life(self):
        if self.shaders.background_effect == 'gol':
            self.draw_gol = self.display.cursor.cursor and self.events.check_key(key='mouse_3', action='held') and not self.transition.transitioning
            self.clear_gol = self.events.check_key(key='escape') and self.game_state != 'game'
            if self.conway:
                self.conway -= 1
            if self.events.check_key(key='conway', action='last_pressed'):
                self.conway = self.fps * 2

    def update(self):
        self.true_fps = self.clock.get_fps()
        if self.true_fps:
            self.runtime_frames += 1
            self.runtime_seconds = self.runtime_seconds + 1 / self.true_fps
            self.low_fps = False
            if self.true_fps < 0.5 * self.fps:
                self.low_fps = True
        self.events.update()
        mouse_position = self.events.mouse_display_position
        if self.testing:
            if self.events.check_key(key='w', modifier='ctrl'):
                self.quit()
            if self.events.check_key(key='b', modifier='ctrl'):
                self.debug = not self.debug
        self.text_handler.update(mouse_position=mouse_position)
        if self.menu_state:
            self.menu_states[self.menu_state].update(mouse_position=mouse_position)
        self.assets.update()
        self.game_states[self.game_state].update(mouse_position=mouse_position)
        self.update_game_of_life()
        self.audio.update()
        self.display.update()
        self.transition.update()
        self.shaders.update(mouse_position=mouse_position)

    def draw_game_of_life(self):
        if self.shaders.background_effect == 'gol':
            if self.clear_gol:
                self.shaders.clear_gol()
            if self.draw_gol:
                pg.draw.circle(surface=self.display.displays['background'], color=self.assets.colours['cream'], center=self.events.mouse_display_position, radius=8, width=1, draw_bottom_left=True)
                pg.draw.circle(surface=self.display.displays['background'], color=self.assets.colours['cream'], center=self.events.mouse_display_position, radius=12, width=1, draw_top_left=True)
                pg.draw.circle(surface=self.display.displays['background'], color=self.assets.colours['cream'], center=self.events.mouse_display_position, radius=16, width=1, draw_top_right=True)
                pg.draw.circle(surface=self.display.displays['background'], color=self.assets.colours['cream'], center=self.events.mouse_display_position, radius=20, width=1, draw_bottom_right=True)
            if self.conway:
                self.text_handler.activate_text(text_group='main', text_id='conway')

    def draw(self):
        if self.debug:
            self.text_handler.activate_text(text_group='main', text_id='debug')
        self.game_states[self.game_state].draw(displays=self.display.displays)
        if self.menu_state:
            self.menu_states[self.menu_state].draw(displays=self.display.displays)
        self.text_handler.draw(displays=self.display.displays)
        self.draw_game_of_life()
        self.display.draw()
        self.transition.draw(displays=self.display.displays)
        self.shaders.draw(displays=self.display.displays)
        pg.display.flip()

    def quit(self):
        self.shaders.quit()
        pg.mixer.quit()
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    if sys.version_info[0:3] != (3, 13, 5):
        raise Exception('Python version 3.13.5 required')
    Main().run()

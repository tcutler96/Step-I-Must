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
import cProfile
import asyncio
import sys
import os


class Main:
    def __init__(self):
        pg.init()
        self.game_name = 'Step I Must'
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
                if previous_game_state == 'main_menu' and self.game_state == 'game' and 'New Game' not in self.menu_states['title_screen'].menu:
                    self.update_menu(menu='title_screen')
                self.game_states[game_state].start_up(previous_game_state=previous_game_state)

    def change_menu_state(self, menu_state=None):
        if menu_state != self.menu_state:
            if menu_state is None or menu_state in self.menu_states:
                self.menu_state = menu_state
                if self.menu_state in self.menu_states:
                    self.menu_states[self.menu_state].start_up()

    def update_menu(self, menu=None):
        if menu in self.menu_states:
            self.assets.update_menu(menu=menu)
            self.menu_states[menu] = Menu(main=self, menu_name=menu, menu_data=self.assets.settings['menus'][menu])

    def main(self):
        while True:
            self.update()
            self.draw()
            self.clock.tick(self.fps)

    # async def main(self):
    #     while True:
    #         self.update()
    #         self.draw()
    #         self.clock.tick(self.fps)
    #         await asyncio.sleep(0)

    def update_game_of_life(self):
        if self.shaders.background_effect == 'gol':
            self.draw_gol = self.display.cursor.cursor and self.events.check_key(key='mouse_3', action='held') and not self.transition.active
            self.clear_gol = self.events.check_key(key='escape') and self.game_state != 'game'
            if self.conway:
                self.conway -= 1
            if self.events.check_key(key='conway', action='last_pressed'):
                self.conway = self.fps * 2

    def update(self):
        self.true_fps = self.clock.get_fps()
        if self.true_fps:
            self.runtime_frames += 1
            self.runtime_seconds += 1 / self.true_fps
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
    # cProfile.run('Main().main()', sort='tottime')
    # asyncio.run(Main().main())
    Main().main()

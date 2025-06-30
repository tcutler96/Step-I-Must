from scripts.assets import Assets
from scripts.utilities import Utilities
from scripts.display import Display
from scripts.shaders import Shaders
from scripts.audio import Audio
from scripts.events import Events
from scripts.transition import Transition
from scripts.text_handler import TextHandler
from scripts.menu import Menu
from game_states.main_menu import MainMenu
from game_states.game import Game
from game_states.level_editor import LevelEditor
import pygame as pg
import sys
import json
import os


# add glow effect to hud layer
# add animation to 'other' images such as cell marker
# look into loop hero noise transition shader...
# dont need to resize sprites when loaded in assets if we set default sprite size to 16...
# reset asset animation counter when we return to main menu?
# neaten the cursor sprite up a bit
# rework scrollbar images to better fit the theme, antialias the edges?
# starting the game in debug mode does not set steps correctly...
# level editor toggle grid could be made thinner maybe...
# shader background is a little bit fuzzy...
# middle clicking a wall in the level editor crashes the game...
# if we draw text one letter at a time (with a short delay), centred on a position, might make a cool way of displaying speech text...
# programatically draw display layers in shader so we dont have to manually add them each time...
# rescale map elements and have them fade in and out when map opened and closed...
# add level with numerical code written with barriers that tells the secret to beating the level...
# add secret where opening a fully explored map on a particular level reveals a secret, the map tiles point towards something...
# add small amount of randomness to pitch of sound effects when they are played...
# need to loop over each level and fix the walls after we changed the name of the tiles...
# just need to replace old names with new names (ie 'up down' -> 'top bottom')...
# have collectable text move upwards on the screen and dont limit player movement...
# spawning ontop of a collectable (seting respawn while in debug mode and so not collecting collectable) breaks the level loading, steps arent set properly...
# loading game in debug mode crashes when you try to take a step...


class Main:
    def __init__(self):
        pg.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
        pg.init()
        self.fps = 60
        self.true_fps = self.fps
        self.clock = pg.time.Clock()
        self.runtime_frames = 0
        self.runtime_seconds = 0
        self.sprite_size = 16
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
        self.game_state = 'main_menu'
        self.game_states = {'main_menu': MainMenu(main=self), 'game': Game(main=self), 'level_editor': LevelEditor(main=self)}
        self.game_states[self.game_state].start_up()
        self.debug = False
        # self.update_levels()


    def update_levels(self):
        for level_name, level_data in self.assets.levels.items():
            collectables = level_data['collectables'] | {'cheeses': []}
            level_data['collectables'] = collectables
            with open(os.path.join('assets/levels', f'{level_name}.json'), 'w') as file_data:
                json.dump(obj=level_data, fp=file_data, indent=2)

    def change_game_state(self, game_state):
        if game_state != self.game_state:
            if game_state == 'quit':
                self.quit()
            elif game_state in self.game_states:
                previous_game_state = self.game_state
                self.game_state = game_state
                self.game_states[game_state].start_up(previous_game_state=previous_game_state)

    def change_menu_state(self, menu_state):
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

    def update(self):
        self.true_fps = self.clock.get_fps()
        if self.true_fps:
            self.runtime_frames += 1
            self.runtime_seconds = self.runtime_seconds + 1 / self.true_fps
        self.events.update()
        mouse_position = self.events.mouse_display_position if self.events.mouse_active else (999, 999)
        if self.events.check_key(key='w', modifier='ctrl'):
            self.quit()
        if self.events.check_key(key='b', modifier='ctrl'):
            self.debug = not self.debug
        if self.menu_state:
            self.menu_states[self.menu_state].update(mouse_position=mouse_position)
        elif self.game_state in ['game', 'level_editor']:
            self.assets.update()
        self.game_states[self.game_state].update(mouse_position=mouse_position)
        self.text_handler.update(mouse_position=mouse_position)
        self.audio.update()
        self.display.update()
        self.transition.update()
        self.shaders.update(mouse_position=mouse_position)
        if self.events.check_key(key='enter'):
            self.shaders.apply_shader = not self.shaders.apply_shader

    def draw(self):
        if self.debug:
            self.text_handler.activate_text(text_group='main', text_id='debug')
        self.game_states[self.game_state].draw(displays=self.display.displays)
        if self.menu_state:
            self.menu_states[self.menu_state].draw(displays=self.display.displays)
        self.text_handler.draw(displays=self.display.displays)
        self.display.draw()
        self.transition.draw(displays=self.display.displays)
        self.shaders.draw(displays=self.display.displays)
        pg.display.flip()

    def quit(self):
        self.assets.quit()
        self.shaders.quit()
        pg.mixer.quit()
        pg.quit()
        sys.exit()


if __name__ == '__main__':
    Main().run()

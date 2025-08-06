import pygame as pg


class MainMenu:
    def __init__(self, main):
        self.main = main

    def start_up(self, previous_game_state=None):
        self.main.audio.play_music(music_theme='edgy demo')
        self.main.change_menu_state(menu_state='title_screen')


    def update(self, mouse_position):
        self.main.display.set_cursor(cursor='arrow')
        if self.main.menu_state == 'title_screen':
            if self.main.events.check_key(key='space'):  # temporary for testing
                self.main.menu_states['game_paused'].menu['Main Menu'].button_type = 'game_state'
                self.main.menu_states['game_paused'].menu['Main Menu'].button_response = 'main_menu'
                self.main.change_game_state(game_state='game')

    def draw(self, displays):
        pass
        # displays['menu'].blit(source=self.main.assets.images['other']['title'], dest=(50, 50))

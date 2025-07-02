import pygame as pg


class MainMenu:
    def __init__(self, main):
        self.main = main
        self.draw_circle = False
        self.conway = False
        self.clear_background = False

    def start_up(self, previous_game_state=None):
        self.main.change_menu_state(menu_state='title_screen')
        self.main.audio.play_music(music_theme='main_menu', fade=self.main.transition.length)


    def update(self, mouse_position):
        self.main.display.set_cursor(cursor='arrow')
        if self.main.menu_state == 'title_screen':
            self.draw_circle = self.main.events.check_key(key='mouse_3', action='held')
            if self.conway:
                self.conway -= 1
            elif self.main.events.check_key(key='conway', action='last_pressed'):
                self.conway = self.main.fps
            self.clear_background  = self.main.events.check_key(key='escape')
            if self.main.events.check_key(key='space'):
                self.main.menu_states['game_paused'].menu['Quit'].button_type = 'game_state'
                self.main.menu_states['game_paused'].menu['Quit'].button_response = 'main_menu'
                self.main.change_game_state(game_state='game')

    def draw(self, displays):
        if self.clear_background:
            displays['background'].fill(color=self.main.assets.colours['purple'])
        if self.draw_circle:
            pg.draw.circle(surface=displays['background'], color=self.main.assets.colours['cream'], center=self.main.events.mouse_display_position, radius=24, width=1)
        if self.conway:  # move circles around screen
            pg.draw.circle(surface=displays['background'], color=self.main.assets.colours['cream'], center=(100, 45), radius=24, width=1)
            pg.draw.circle(surface=displays['background'], color=self.main.assets.colours['cream'], center=(self.main.display.width - 100, 45), radius=24, width=1)
        if self.main.events.check_key('c'):
            pg.draw.circle(surface=displays['background'], color=self.main.assets.colours['cream'], center=self.main.display.centre, radius=1, width=1)

import pygame as pg
import math


class Transition:
    def __init__(self, main):
        self.main = main
        self.surface = pg.Surface(size=self.main.display.size, flags=pg.SRCALPHA)
        self.surface_2 = pg.Surface(size=self.main.display.size)
        self.active = False
        self.fade_in = False
        self.style = 'fade'
        self.centre = (0, 0)
        self.max_distance = 0
        self.current = 0
        self.step = 0
        self.length = 0
        self.length = 0
        self.scale = 0
        self.response = None
        self.queue = None
        self.start_transition(fade_in=True, length=2)
        # add another transition style that is a black square moves from one side of the screen to the other relative to player movement, triggered whenever we exit/ enter a new level...

    def start_transition(self, fade_in=False, style='fade', centre=(0, 0), length=1, response=None, queue=None):
        # if active to quit game state then overide current transition...
        # need to take current transition state/ display and fade it to black...
        if not self.active:
            self.active = True
            self.style = style
            if centre == 'player':
                self.centre = self.main.game_states['game'].level.grid_to_display(position=self.main.game_states['game'].level.current_respawn[0][0],
                                                                                             centre=True) if self.main.game_states['game'].level.current_respawn else self.main.display.centre
            else:
                self.centre = centre
            self.max_distance = (max(self.centre[0], self.main.display.width - self.centre[0]), max(self.centre[1], self.main.display.height - self.centre[1]))
            self.max_distance = math.sqrt(self.max_distance[0] ** 2 + self.max_distance[1] ** 2)
            self.length = length * self.main.fps
            self.fade_in = fade_in
            if fade_in:
                self.current = 0
                self.step = 1
                self.scale = 0
            else:
                self.current = self.length
                self.step = -1
                self.scale = 1
            self.response = response
            if self.response and self.response[0] == 'game_state' and self.main.assets.music_themes[self.main.game_state] != self.main.assets.music_themes[self.response[1]]:
                self.main.audio.stop_music(fade=length)
            self.queue = queue

    def update(self):
        if self.active:
            self.main.display.set_cursor(cursor=None)
            self.current += self.step
            self.scale = (self.current / self.length) ** 4
            if self.current in [0, self.length]:
                self.active = False
                if self.response:
                    if self.response[0] == 'game_state':
                        self.main.change_game_state(game_state=self.response[1])
                    if self.response[0] == 'menu_state':
                        self.main.change_menu_state(menu_state=self.response[1])
                    elif self.response[0] == 'level':
                        self.main.menu_state = None
                        self.main.game_states[self.main.game_state].load_level(name=self.response[1], load_respawn=self.response[2], bump_player=self.response[3])
                    self.response = None
                if self.queue:
                    self.start_transition(*self.queue)
                    self.queue = None

    def draw(self, displays):
        if self.active:
            if self.style == 'fade':
                self.surface.fill(self.main.assets.colours['dark_purple'])
                self.surface.set_alpha(275 - 275 * self.scale)
                displays['transition'].blit(source=self.surface, dest=(0, 0))
            elif self.style == 'circle':
                self.surface.fill(self.main.assets.colours['purple'])
                self.surface.set_alpha(255 - 255 * self.scale)
                displays['transition'].blit(source=self.surface, dest=(0, 0))
                self.surface_2.fill(self.main.assets.colours['dark_purple'])
                pg.draw.circle(surface=self.surface_2, color=(255, 255, 255), center=self.centre, radius=self.max_distance * self.scale)
                self.surface_2.set_colorkey((255, 255, 255))
                displays['transition'].blit(source=self.surface_2, dest=(0, 0))

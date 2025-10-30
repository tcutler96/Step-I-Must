import pygame as pg
import math


class Transition:
    def __init__(self, main):
        self.main = main
        self.num_surfaces = 2
        self.surfaces = [pg.Surface(size=self.main.display.size, flags=pg.SRCALPHA) for _ in range(self.num_surfaces)]
        self.active = False
        self.fade_in = False
        self.style = 'fade'
        self.style_data = None
        self.circle_distance = 0
        self.current = 0
        self.step = 0
        self.length = 0
        self.scale = 0
        self.response = None
        self.queue = None
        self.start_transition(fade_in=True, length=2)

    def start_transition(self, fade_in=False, style='fade', style_data=None, length=1, response=None, queue=None):
        # if active to quit game state then overide current transition...
        # need to take current transition state/ display and fade it to black...
        if not self.active:
            self.active = True
            self.style = style
            if self.style == 'circle':
                if style_data == 'player':
                    self.style_data = [self.main.game_states['game'].level.grid_to_display(position=self.main.game_states['game'].level.current_respawn[0][0],
                                                                                          centre=True) if self.main.game_states['game'].level.current_respawn else self.main.display.centre]
                else:
                    self.style_data = style_data if isinstance(style_data, list) else [style_data]
                self.circle_distance = []
                for data in self.style_data:
                    circle_distance = (max(data[0], self.main.display.width - data[0]), max(data[1], self.main.display.height - data[1]))
                    circle_distance = math.sqrt(circle_distance[0] ** 2 + circle_distance[1] ** 2)
                    self.circle_distance.append(circle_distance)
            else:
                self.style_data = style_data
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
            if self.response and self.response[0] == 'game_state':
                self.main.audio.stop_music(game_state=self.response[1], fade=length)
                if self.response[1] == 'quit':
                    self.main.audio.play_sound(name='quit')
            self.queue = queue

    def update(self):
        if self.active:
            self.main.display.set_cursor(cursor=None)
            self.current += self.step
            self.scale = (self.current / self.length) ** 5
            # if self.current <= 0 or self.current >= self.length:
            if self.current in [0, self.length]:
                self.active = False
                if self.response:
                    if self.response[0] == 'game_state':
                        self.main.change_game_state(game_state=self.response[1])
                    elif self.response[0] == 'menu_state':
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
                self.surfaces[0].fill(self.main.assets.colours['dark_purple'])
                self.surfaces[0].set_alpha(255 - 255 * self.scale)
                displays['transition'].blit(source=self.surfaces[0], dest=(0, 0))
            elif self.style == 'circle':
                self.surfaces[0].fill(self.main.assets.colours['purple'])
                self.surfaces[0].set_alpha(255 - 255 * self.scale)
                displays['transition'].blit(source=self.surfaces[0], dest=(0, 0))
                self.surfaces[1].fill(self.main.assets.colours['dark_purple'])
                for count, (centre, circle_distance) in enumerate(zip(self.style_data, self.circle_distance)):
                    pg.draw.circle(surface=self.surfaces[1], color=(255, 255, 255), center=centre, radius=circle_distance * self.scale)
                self.surfaces[1].set_colorkey((255, 255, 255))
                displays['transition'].blit(source=self.surfaces[1], dest=(0, 0))
            elif self.style == 'square':
                self.surfaces[0].fill(self.main.assets.colours['purple'])
                self.surfaces[0].set_alpha(255 - 255 * self.scale)
                displays['transition'].blit(source=self.surfaces[0], dest=(0, 0))
                self.surfaces[1].fill(self.main.assets.colours['dark_purple'])
                displays['transition'].blit(source=self.surfaces[1], dest=(-self.style_data[0] * self.main.display.width * self.scale,
                                                                         -self.style_data[1] * self.main.display.width * self.scale))

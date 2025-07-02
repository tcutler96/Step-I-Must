from scripts.cursor import Cursor
import pygame as pg


class Display:
    def __init__(self, main):
        self.main = main
        self.screen_size = self.screen_width, self.screen_height = (pg.display.Info().current_w, pg.display.Info().current_h)
        self.screen_centre = self.screen_half_width, self.screen_half_height = self.screen_width // 2, self.screen_height // 2
        self.size = self.width, self.height = (480, 320)
        self.centre = self.half_width, self.half_height = self.width // 2, self.height // 2
        self.scale_factor = self.main.assets.settings['video']['resolution']
        self.window_size = self.window_width, self.window_height = (self.size[0] * self.scale_factor, self.size[1] * self.scale_factor)
        self.window_centre = self.window_half_width, self.window_half_height = self.window_width // 2, self.window_height // 2
        self.display_layers = ['background', 'level', 'steps', 'map', 'level_editor', 'menu', 'ui', 'transition']
        self.displays = self.load_displays()
        self.window = pg.display.set_mode(size=self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.main.assets.post_load()
        pg.display.set_caption('Slime Stepper')
        pg.display.set_icon(self.main.assets.images['other']['game_icon'])
        self.cursor = Cursor(main=self.main)
        self.rect = pg.Rect((0, 0), self.size)

    def load_displays(self):
        displays = {}
        for display_layer in self.display_layers:
            displays[display_layer] = pg.Surface(size=self.size, flags=pg.SRCALPHA)
        return displays

    def set_cursor(self, cursor=None):
        self.cursor.set_cursors.append(cursor)

    def change_resolution(self, scale_factor):
        self.scale_factor = scale_factor
        self.window_size = self.window_width, self.window_height = (self.size[0] * self.scale_factor, self.size[1] * self.scale_factor)
        self.window_centre = self.window_half_width, self.window_half_height = self.window_width // 2, self.window_height // 2
        self.window = pg.display.set_mode(size=self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)
        pg.display.set_window_position((self.screen_half_width - self.window_half_width, self.screen_half_height - self.window_half_height))
        self.main.shaders.change_resolution()

    def update(self):
        for display_layer, display_surface in self.displays.items():
            if display_layer == 'background':
                display_surface.fill(color=self.main.assets.colours['purple'])
            else:
                display_surface.fill(color=(0, 0, 0, 0))
        pg.display.set_caption('Slime Stepper' + (f' - running at {round(self.main.true_fps)} fps for {round(self.main.runtime_seconds, 2)}s' if self.main.debug else ''))
        if self.main.game_state in ['game', 'level_editor']:
            pg.display.set_icon(self.main.utilities.get_sprite(name='player', state='idle', animated=True))
        self.cursor.update()

    def draw(self):
        self.cursor.draw(displays=self.displays)

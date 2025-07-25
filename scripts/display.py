from scripts.cursor import Cursor
import pygame as pg
import platform


class Display:
    def __init__(self, main):
        self.main = main
        self.screen_size = self.screen_width, self.screen_height = pg.display.get_desktop_sizes()[0]
        self.screen_centre = self.screen_half_width, self.screen_half_height = self.screen_width // 2, self.screen_height // 2
        self.size = self.width, self.height = (480, 320)
        self.aspect_ratio = (1, self.size[0] / self.size[1])
        self.centre = self.half_width, self.half_height = self.width // 2, self.height // 2
        self.scale_factor = self.main.assets.settings['video']['resolution']
        self.window_size = self.window_width, self.window_height = (self.size[0] * self.scale_factor, self.size[1] * self.scale_factor)
        self.window_centre = self.window_half_width, self.window_half_height = self.window_width // 2, self.window_height // 2
        self.display_layers = ['background', 'level', 'player', 'level_text', 'map', 'level_editor', 'menu', 'ui', 'transition']
        self.displays = self.load_displays()
        if platform.system() == 'Darwin':
            pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
            pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
            pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
            pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)
        self.window = pg.display.set_mode(size=self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)
        self.main.assets.post_load()
        pg.display.set_caption(self.main.game_name)
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

    def check_new_resolution(self, scale_factor):
        new_window_size = (self.size[0] * scale_factor, self.size[1] * scale_factor)
        if new_window_size[0] <= self.screen_size[0] and new_window_size[1] <= self.screen_size[1]:
            return True

    def change_resolution(self, scale_factor):
        new_window_size = (self.size[0] * scale_factor, self.size[1] * scale_factor)
        if new_window_size[0] > self.screen_size[0] or new_window_size[1] > self.screen_size[1]:
            return True
        else:
            self.scale_factor = scale_factor
            self.window_size = self.window_width, self.window_height = new_window_size
            self.window_centre = self.window_half_width, self.window_half_height = self.window_width // 2, self.window_height // 2
            self.window = pg.display.set_mode(size=self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF)
            pg.display.set_window_position((self.screen_half_width - self.window_half_width, self.screen_half_height - self.window_half_height))
            self.main.shaders.change_resolution()

    def update(self):
        for display_layer, display_surface in self.displays.items():
            if display_layer == 'background':
                if self.main.assets.settings['video']['background'] == 'gol':
                    display_surface.fill(color=self.main.assets.colours['purple'])
                    # if self.main.events.check_key(key='b', action='held'):
                    #     display_surface.blit(source=self.main.assets.images['other']['test'], dest=(0, 0))
                elif self.main.assets.settings['video']['background'] == 'space':
                    display_surface.blit(source=self.main.assets.images['other']['space4'], dest=(0, 0))
            else:
                display_surface.fill(color=(0, 0, 0, 0))
        pg.display.set_caption(self.main.game_name + (f' - running at {round(self.main.true_fps)} fps for {round(self.main.runtime_seconds, 2)}s' if self.main.debug else ''))
        pg.display.set_icon(self.main.utilities.get_sprite(name='player', state='idle', animated=True))
        self.cursor.update()

    def draw(self):
        self.cursor.draw(displays=self.displays)

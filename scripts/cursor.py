import pygame as pg


class Cursor:
    def __init__(self, main):
        self.main = main
        self.cursor_type = self.main.assets.settings['video']['cursor_type']
        self.show_cursor = True
        self.cursor = 'default'
        self.cursors = self.load_cursors()
        self.set_cursors = []
        self.cursor_offsets = {'arrow': 0, 'hand': 2}

    def load_cursors(self):
        cursors = {'system': {'arrow': pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW), 'hand': pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND)}, 'sprite': {'default': {}, 'held': {}}}
        for cursor in ['arrow', 'hand']:
            surface = self.main.assets.images['cursor'][cursor + '_cursor2'].copy()
            cursors['sprite']['default'][cursor] = surface
            cursors['sprite']['held'][cursor] = pg.transform.scale(surface=surface, size=(surface.get_size()[0] * 0.9, surface.get_size()[1] * 0.9))
        return cursors

    def update(self):
        if None in self.set_cursors:
            self.cursor = None
            self.show_cursor = False
            pg.mouse.set_visible(False)
        else:
            if self.cursor_type == 'sprite':
                pg.mouse.set_visible(False)
                if 'hand' in self.set_cursors:
                    self.cursor = 'hand'
                    self.show_cursor = True
                elif 'arrow' in self.set_cursors:
                    self.cursor = 'arrow'
                    self.show_cursor = True
            elif self.cursor_type == 'system':
                pg.mouse.set_visible(True)
                if 'hand' in self.set_cursors:
                    self.cursor = 'hand'
                    pg.mouse.set_cursor(self.cursors['system']['hand'])
                elif 'arrow' in self.set_cursors:
                    self.cursor = 'arrow'
                    pg.mouse.set_cursor(self.cursors['system']['arrow'])
        self.set_cursors = []

    def draw(self, displays):
        if self.main.events.mouse_active and self.show_cursor and self.cursor_type == 'sprite':
            displays['ui'].blit(source=self.cursors['sprite']['held' if self.main.events.check_key(key='mouse_1', action='held') else 'default'][self.cursor],
                                dest=(self.main.events.mouse_display_position[0] - self.cursor_offsets[self.cursor], self.main.events.mouse_display_position[1]))

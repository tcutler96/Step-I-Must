import pygame as pg


class MapCell:
    def __init__(self, main, level_name, sprite, blit_position, cell_size, discovered, player, teleporter, collectables):
        self.main = main
        self.level_name = level_name
        self.sprite = sprite
        self.blit_position = blit_position
        self.cell_size = cell_size
        self.rect = None
        self.discovered = discovered
        self.player = player
        self.teleporter = teleporter
        self.collectables = collectables
        self.hovered = False
        self.was_hovered = False
        self.main.text_handler.add_text(text_group='map', text_id=self.level_name, text=self.level_name, position='top_right', alignment=('r', 'c'), display_layer='map')

    def update_rect(self, offset):
        self.rect = pg.Rect((self.blit_position[0] + offset[0], self.blit_position[1] + offset[1]), (self.cell_size, self.cell_size))

    def update(self, mouse_position, offset, interpolating, alpha):
        self.was_hovered = self.hovered
        self.hovered = False
        if interpolating:
            self.update_rect(offset=offset)
        elif alpha==255 and (self.discovered or self.main.debug) and mouse_position  and self.rect.collidepoint(mouse_position):
            self.hovered = True
            if self.teleporter or self.main.debug:
                if not self.was_hovered:
                    self.main.audio.play_sound(name='map_highlight_teleporter')
                self.main.display.set_cursor(cursor='hand')
                if self.main.events.check_key(key='mouse_1'):
                    self.main.audio.play_sound(name='teleport', overlap=True)
                    return self.rect.center
            elif not self.was_hovered:
                self.main.audio.play_sound(name='map_highlight')

    def draw_cell(self, displays, sprite, offset, alpha=None):
        if alpha:
            sprite.set_alpha(alpha)
        displays['map'].blit(source=sprite, dest=(self.blit_position[0] + offset[0], self.blit_position[1] + offset[1]))

    def draw(self, displays, icons, offset, alpha):
        if self.rect.colliderect(self.main.display.rect):
            if self.discovered or self.main.debug:
                if self.main.assets.settings['video']['map_colour'] != 'disabled':
                    pg.draw.rect(surface=displays['map'], color=self.main.utilities.get_colour(colour=self.main.assets.settings['video']['map_colour'], alpha=alpha), rect=self.rect)
                if self.hovered and alpha == 255:
                    self.main.text_handler.activate_text(text_group='map', text_id=self.level_name)
                    pg.draw.rect(surface=displays['map'], color=self.main.utilities.get_colour(colour='cream', alpha=alpha), rect=self.rect)
                self.draw_cell(displays=displays, sprite=self.sprite, offset=offset, alpha=alpha)
                if self.teleporter:
                    self.draw_cell(displays=displays, sprite=icons['teleporter']['sprite'], offset=offset)
                if self.player:
                    self.draw_cell(displays=displays, sprite=icons['player']['sprite'], offset=offset)
            for collectable_type, collectables in self.collectables.items():
                if collectables:
                    if self.main.debug:
                        self.draw_cell(displays=displays, sprite=icons[collectable_type]['sprite'], offset=offset)
                    elif collectable_type in ['silver keys', 'silver gems'] and self.main.assets.data['game']['part_one']:
                        self.draw_cell(displays=displays, sprite=icons[collectable_type]['sprite'], offset=offset)
                    elif collectable_type in ['gold keys', 'gold gems'] and self.main.assets.data['game']['part_two']:
                        self.draw_cell(displays=displays, sprite=icons[collectable_type]['sprite'], offset=offset)
                    elif collectable_type == 'cheeses' and self.main.utilities.check_collectable(collectable_type='cheese', count=False):
                        self.draw_cell(displays=displays, sprite=icons[collectable_type]['sprite'], offset=offset)

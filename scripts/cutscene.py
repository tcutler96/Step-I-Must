import pygame as pg

class Cutscene:
    def __init__(self, main):
        self.main = main
        self.active_cutscene = False
        self.timer = 0
        self.cutscene_data = {'part_one': {'type': 'level', 'triggered': self.main.assets.data['game']['part_one'], 'trigger': '(0, 0)', 'length': 9, 'position': (301, 61)},
                              'part_two': {'type': 'level', 'triggered': self.main.assets.data['game']['part_two'], 'trigger': '(-1, -5)', 'length': 9, 'position': (157, 205)},
                              'collectable': {'type': 'collectable', 'triggered': False, 'trigger': 'collectable', 'length': 3, 'position': None}}
        # move text element shadow sway and mouse options to the utilities draw text function?
        # cutscenes are triggered the firdt time the player enters a certain level, can add them for all the starting levels?
        # change intro cutscene, have black bars come from the top and bottom to simulate movie resolution, then have big player sprite appear with some text to introduce the setting and goal...
        # first room just shows the player how to move
        # second room shows player how to pause/ open game menu
        # third room shows player how to open the map, dont do it automatically, let them do it...
        # fourth room shows player how to undo/ redo
        self.rect_max_offset = 96
        self.top_rect = pg.Rect(0, -self.rect_max_offset, self.main.display.width, self.rect_max_offset)
        self.bottom_rect = pg.Rect(0, self.main.display.height, self.main.display.width, self.rect_max_offset)
        self.rect_offset = 0
        self.test_text = 'dialogue test with text appearing one character at a time...'
        self.text_index = 0

    def reset(self):
        self.cutscene_data['part_one']['triggered'] = self.main.assets.data['game']['part_one']
        self.cutscene_data['part_two']['triggered'] = self.main.assets.data['game']['part_two']

    def start(self, collectable_type, position):
        if collectable_type in self.main.assets.data['game']['collectables']:
            cutscene_data = self.cutscene_data['collectable']
            self.active_cutscene = 'collectable'
            self.timer = cutscene_data['length'] * self.main.fps
            cutscene_data['position'] = position
            self.main.text_handler.activate_text(text_group='collectables', text_id=collectable_type, duration=3)

    def update(self, level):
        if self.main.events.check_key('c', 'held'):
            self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player'], effect='blur', effect_data={'length': 1})
            if self.rect_offset < self.rect_max_offset:
                self.rect_offset += 2
                self.top_rect.y = -self.rect_max_offset + self.rect_offset
                self.bottom_rect.y = self.main.display.height - self.rect_offset
            else:
                if self.text_index < len(self.test_text):
                    text_index = self.text_index
                    self.text_index += 0.15
                    if int(text_index) != int(self.text_index):
                        self.main.audio.play_sound(name='dialogue')
        else:
            if self.rect_offset:
                self.rect_offset -= 2
                self.top_rect.y = -self.rect_max_offset + self.rect_offset
                self.bottom_rect.y = self.main.display.height - self.rect_offset
                self.text_index = 0

        if self.active_cutscene:
            self.timer -= 1
            if self.timer == 0:
                if self.active_cutscene == 'collectable':
                    self.main.shaders.apply_effect(display_layer=['level_main', 'level_player'], effect=None)
                self.active_cutscene = None
            if self.active_cutscene == 'part_one':
                if self.timer == 420:
                    return 'open_map'
                elif self.timer == 300:
                    return 'show_collectables_one'
                elif self.timer == 1:
                    return 'close_map'
            elif self.active_cutscene == 'part_two':
                if self.timer == 420:
                    return 'open_map'
                elif self.timer == 300:
                    return 'show_collectables_two'
                elif self.timer == 1:
                    return 'close_map'
            elif self.active_cutscene == 'collectable':
                # apply additional effect to player...
                self.main.shaders.apply_effect(display_layer='level_main', effect='shockwave', effect_data={'x': self.cutscene_data['collectable']['position'][0],
                                                                                                              'y': self.cutscene_data['collectable']['position'][1], 'length': 2})
        else:
            for name, data in self.cutscene_data.items():
                if data['type'] == 'level' and not data['triggered']:
                    if level.name == data['trigger']:
                        self.main.audio.play_sound(name='cutscene')
                        self.active_cutscene = name
                        self.timer = data['length'] * self.main.fps
                        data['triggered'] = True
                    if self.active_cutscene == 'part_one':
                        return 'map_target_one'
                    elif self.active_cutscene == 'part_two':
                        return 'map_target_two'

    def draw(self, displays):
        if self.rect_offset:
            pg.draw.rect(surface=displays['level_ui'], color=self.main.assets.colours['dark_purple'], rect=self.top_rect)
            pg.draw.rect(surface=displays['level_ui'], color=self.main.assets.colours['dark_purple'], rect=self.bottom_rect)
            if self.rect_offset == self.rect_max_offset:
                self.main.utilities.draw_text(text=self.test_text[:int(self.text_index)], surface=displays['level_ui'], position=self.main.display.centre, alignment=('c', 'c'),
                                              colour='light_green', bg_colour=None, shadow_colour='dark_purple', outline_colour='dark_purple', outline_size=1, size=16)

        if self.active_cutscene in ['part_one', 'part_two']:  # can add interesting sprite/ particles around player
            displays['level'].blit(source=self.main.assets.images['toolbar']['marker'], dest=self.cutscene_data[self.active_cutscene]['position'])
        elif self.active_cutscene == 'collectable': # collectable spirals around player while shrinking
            pass

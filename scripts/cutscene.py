import pygame as pg

class Cutscene:
    def __init__(self, main):
        self.main = main
        self.active_cutscene = False
        self.timer = 0
        self.cutscene_data2 = self.main.assets.data['cutscenes']
        print(self.cutscene_data2)
        self.cutscene_data = {'part_one': {'type': 'level', 'triggered': self.main.assets.data['game']['part_one'], 'trigger': '(0, 0)', 'length': 9, 'position': (301, 61)},
                              'part_two': {'type': 'level', 'triggered': self.main.assets.data['game']['part_two'], 'trigger': '(-1, -5)', 'length': 9, 'position': (157, 205)},
                              'collectable': {'type': 'collectable', 'triggered': False, 'trigger': 'collectable', 'length': 3, 'position': None}}
        # move text element shadow sway and mouse options to the utilities draw text function?
        # add rainbow colour effect to player and have collectable swirl around player...
        # cutscenes are triggered the first time the player enters a certain level, can add them for all the starting levels?
        # change intro cutscene, have black bars come from the top and bottom to simulate movie resolution, then have big player sprite appear with some text to introduce the setting and goal...
        # first room just shows the player how to move
        # second room shows player how to pause/ open game menu
        # third room shows player how to open the map, dont do it automatically, let them do it...
        # fourth room shows player how to undo/ redo
        self.rect_max_offset = 96
        self.rect_speed = 2
        self.top_rect = pg.Rect(0, -self.rect_max_offset, self.main.display.width, self.rect_max_offset)
        self.bottom_rect = pg.Rect(0, self.main.display.height, self.main.display.width, self.rect_max_offset)
        self.rect_offset = 0
        self.sprite = None
        self.sprite_position = (self.main.display.half_width, self.rect_max_offset + (self.main.display.half_height - self.rect_max_offset - self.main.sprite_size) // 2)
        self.test_text = 'dialogue test with text appearing one character at a time... now even longer!'
        self.text_index = 0
        self.text_speed = 0.1
        # put cutscene data/ dialogue into data file
        # 'Where and what is this strange place I find myself in?', 'I am but a slime in this strange and wonderful place'
        # 'And why is there a step counter in the corner?', 'I'm just a slime with no legs to take steps', 'Though I have no legs, I must be wary of each and every step I take'
        # 'Guess the only think to do is press forward'
        # allow for multiple text lines in cutscene dialogue, automatically move next line down, similar to sign text...

        # cutscene data: {(level): repeatable: True/ False}

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
            if self.rect_offset < self.rect_max_offset:  # stage 1, bars come in from top and bottom
                self.rect_offset += self.rect_speed
                self.top_rect.y = -self.rect_max_offset + self.rect_offset
                self.bottom_rect.y = self.main.display.height - self.rect_offset
                # we could make another player sprite that is used here in the cutscenes (ie player_thinking)...
                self.sprite = self.main.utilities.get_sprite(name='player', state='idle')
                self.sprite.set_alpha(255 * self.rect_offset / self.rect_max_offset)
                self.text_index = 0
            else:
                if self.text_index < len(self.test_text):  # stage 2, dialogue appears on screen
                    text_index = self.text_index
                    if self.main.events.check_key(key='space'):  # skip over current text line...
                        self.text_index = len(self.test_text)
                    else:
                        self.text_index += self.text_speed
                    if int(text_index) != int(self.text_index):
                        self.main.audio.play_sound(name='dialogue')
                        text = self.test_text[:int(self.text_index)]
                        self.main.text_handler.add_text(text_group='cutscene', text_id=text, text=text, position='centre', display_layer='level_ui',
                                                        size=16, max_width=self.main.display.width - 16, alpha_up=255, alpha_down=25.5)
        else:
            if self.rect_offset:
                self.rect_offset -= self.rect_speed
                self.top_rect.y = -self.rect_max_offset + self.rect_offset
                self.bottom_rect.y = self.main.display.height - self.rect_offset
                self.sprite = self.main.utilities.get_sprite(name='player', state='idle')
                self.sprite.set_alpha(255 * self.rect_offset / self.rect_max_offset)

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
                self.main.shaders.apply_effect(display_layer='level_player', effect='invert', effect_data={'length': 2})
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
            displays['level_ui'].blit(source=self.sprite, dest=(self.sprite_position[0], self.sprite_position[1] - self.main.text_handler.text_bounce * 3))
            if self.rect_offset == self.rect_max_offset:
                self.main.text_handler.activate_text(text_group='cutscene', text_id=self.test_text[:int(self.text_index)])

        if self.active_cutscene in ['part_one', 'part_two']:  # can add interesting sprite/ particles around player
            displays['level'].blit(source=self.main.assets.images['toolbar']['marker'], dest=self.cutscene_data[self.active_cutscene]['position'])
        elif self.active_cutscene == 'collectable': # collectable spirals around player while shrinking
            pass

import pygame as pg

class Cutscene:
    def __init__(self, main):
        self.main = main
        self.active_cutscene = False
        self.timer = 0
        self.cutscene_data_temp = self.main.assets.data['cutscenes']
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
        self.active = False
        self.stage = 0
        self.stage_fade = 1  # each stage fades in, in 1 second
        self.rect_max_offset = 96  # set length of each cutscene stage, to have all elements fade in and out together...
        self.rect_speed = 2
        self.bars = [pg.Rect(0, -self.rect_max_offset, self.main.display.width, self.rect_max_offset),
                     pg.Rect(0, self.main.display.height, self.main.display.width, self.rect_max_offset)]
        self.rect_offset = 0
        self.sprite = None
        self.sprite_position = (self.main.display.half_width - self.main.sprite_size // 2, self.rect_max_offset + (self.main.display.half_height - self.rect_max_offset - self.main.sprite_size) // 2)
        self.test_text = [["Where am I?", "Why am I?", "I'm just... a slime."], ["But I can think.", "I can move.", "That's not normal, is it?"],
                          ["[the slime looks around at the surroundings]", "This place is strange.", "It's all squares and steps and rules."],
                          ["I feel like I'm supposed to do something.", "But no one told me what.", "Or maybe I forgot..."], ["Every step I take...", "It's like it means something.", "But what?"],
                          ["What happens if I run out of steps?", "Do I stop...", "Do I stop?"], ["Move forward, reach the goal, don't waste steps.", "I guess that's all I've got.", "Step by step."],
                          ["Maybe I'll find out why I'm here.", "Or maybe I won't...", "Either way, I'll keep going."]]
        # self.test_text = ["Where am I?", "Why am I?", "I'm just... a slime."]
        # self.test_text = ["But I can think.", "I can move.", "That's not normal, is it?"]
        # self.test_text = ["[the slime looks around at the surroundings]", "This place is strange.", "It's all squares and steps and rules."]
        # self.test_text = ["I feel like I'm supposed to do something.", "But no one told me what.", "Or maybe I forgot..."]
        # self.test_text = ["Every step I take...", "It's like it means something.", "But what?"]
        # self.test_text = ["What happens if I run out of steps?", "Do I stop...", "Do I stop?"]
        # self.test_text = ["Move forward, reach the goal, don't waste steps.", "I guess that's all I've got.", "Step by step."]
        # self.test_text = ["Maybe I'll find out why I'm here.", "Or maybe I won't...", "Either way, I'll keep going."]
        self.text_position = (self.main.display.half_width, self.main.display.half_height - 8)
        self.text_index = 0
        self.line_index = 0
        self.character_index = 0
        self.line_pause = 0
        self.text_speed = 1
        self.show_button = False
        self.button = self.main.assets.images['other']['button_5']
        self.button_alpha = 0
        self.button_position = (self.main.display.half_width - self.button.get_width() // 2, self.main.display.height - self.rect_max_offset - self.button.get_height() * 1.5)
        self.main.text_handler.add_text(text_group='cutscene', text_id='space', text='space', size=10, alpha_up=8.5, alpha_down=8.5, bounce=-3,
                                        position=(self.main.display.half_width, self.main.display.height - self.rect_max_offset - self.button.get_height()), shadow_colour=None, display_layer='level_ui')
        # put cutscene data/ dialogue into data file
        # have dialogue be quite exstitential...
        # 'Where and what is this strange place I find myself in?', 'I am but a slime in this strange and wonderful place'
        # 'And why is there a step counter in the corner?', 'I'm just a slime with no legs to take steps', 'Though I have no legs, I must be wary of each and every step I take'
        # 'Guess the only think to do is press forward'
        # allow for multiple text lines in cutscene dialogue, automatically move next line down, similar to sign text...
        # or maybe just show one line at a time, but pause at the end of each line to give the player time to read it...
        # when we finish showing the last line of text, show press 'space' button to exit cutscene...

        # cutscene data: {(level): repeatable: True/ False}
        # add slight delay between lines
        # and add a pause at the end of each line section, waiting for the player to press 'space'

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

    def update_bars(self):
        self.bars[0].y = -self.rect_max_offset + self.rect_offset
        self.bars[1].y = self.main.display.height - self.rect_offset

    def update(self, level):
        if self.main.events.check_key('c'):
            if not self.stage:
                self.stage = 1
                self.rect_offset = 0
                self.text_index = 0
                self.line_index = 0
                self.character_index = 0
                self.button.set_alpha(0)
        if self.stage:
            self.sprite = self.main.utilities.get_sprite(name='player', state='thinking', alpha=255 * self.rect_offset / self.rect_max_offset)
        if self.stage in [1, 2, 3]:
            self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player'], effect='blur', effect_data={'length': 1})
        if self.stage == 1:  # stage 1, bars come in from top and bottom
            self.rect_offset += self.rect_speed
            self.update_bars()
            if self.rect_offset >= self.rect_max_offset:
                self.stage = 2
        elif self.stage == 2 and not self.line_pause: # stage 2, dialogue appears on screen
            character_index = self.character_index
            if self.main.events.check_key(key='space'):  # skip over current text line...
                self.character_index = len(self.test_text[self.text_index][self.line_index])
            else:
                self.character_index += self.text_speed
            if self.character_index > 0 and int(character_index) != int(self.character_index):
                self.main.audio.play_sound(name='dialogue')
                text = self.test_text[self.text_index][self.line_index][:int(self.character_index)]
                self.main.text_handler.add_text(text_group='cutscene', text_id=text, text=text, position=(self.text_position[0], self.text_position[1] + 16 * self.line_index), display_layer='level_ui',
                                                size=14, max_width=self.main.display.width - 32, alpha_up=255, alpha_down=25.5, style='itallic')
            if self.character_index >= len(self.test_text[self.text_index][self.line_index]):  # end of line
                if self.line_index == len(self.test_text[self.text_index]) - 1:
                    # start timer here, only progress when timer has finished...
                    self.line_pause = 60
                    if self.text_index == len(self.test_text) - 1:
                        self.stage = 3
                    else:
                        print('new section')
                        self.text_index += 1
                        self.line_index = 0
                        self.character_index = -60
                else:
                    print('new line')
                    self.line_index += 1
                    self.character_index = -60
        elif self.stage == 3:  # stage 3, all dialogue has appeared, awaiting user input
            if self.button_alpha < 255:
                self.button_alpha += 8.5
                self.button.set_alpha(self.button_alpha)
            if self.main.events.check_key(key='space'):
                if self.text_index == len(self.test_text) - 1:
                    self.stage = 4
        elif self.stage == 4:  # stage 4, final stage, everything fades away/ out
            self.rect_offset -= self.rect_speed
            self.update_bars()
            if self.button_alpha > 0:
                self.button_alpha -= 8.5
                self.button.set_alpha(self.button_alpha)
            if self.rect_offset <= 0:
                self.stage = 0
        self.active = bool(self.stage)

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
        if self.stage:
            for bar in self.bars:
                pg.draw.rect(surface=displays['level_ui'], color=self.main.assets.colours['dark_purple'], rect=bar)
            displays['level_ui'].blit(source=self.sprite, dest=(self.sprite_position[0], self.sprite_position[1] + self.main.text_handler.text_bounce * -3))
            if self.stage in [2, 3]:
                for line_index in range(self.line_index + 1):
                    character_index = int(self.character_index) if line_index == self.line_index else len(self.test_text[self.text_index][line_index])
                    self.main.text_handler.activate_text(text_group='cutscene', text_id=self.test_text[self.text_index][line_index][:character_index])
            if self.stage == 3:
                self.main.text_handler.activate_text(text_group='cutscene', text_id='space')
            if self.stage in [3, 4]:
                displays['level_ui'].blit(source=self.button, dest=(self.button_position[0], self.button_position[1] + self.main.text_handler.text_bounce * -3))

        if self.active_cutscene in ['part_one', 'part_two']:  # can add interesting sprite/ particles around player
            displays['level'].blit(source=self.main.assets.images['toolbar']['marker'], dest=self.cutscene_data[self.active_cutscene]['position'])
        elif self.active_cutscene == 'collectable': # collectable spirals around player while shrinking
            pass

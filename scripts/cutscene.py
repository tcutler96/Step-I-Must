import pygame as pg
from math import sin, cos

class Cutscene:
    def __init__(self, main):
        self.main = main
        self.cutscene_speed = self.main.assets.settings['gameplay']['cutscene_speed']
        self.active = False
        self.cutscene_type = None
        self.alpha_step = 8.5
        self.show_bars = False
        self.bars_offset = 0
        self.bars_max_offset = 96
        self.bars_speed = self.bars_max_offset / (((1 - self.cutscene_speed) * 1 + self.cutscene_speed * 0.5) * self.main.fps)
        self.bars = [pg.Rect(0, -self.bars_max_offset, self.main.display.width, self.bars_max_offset),
                     pg.Rect(0, self.main.display.height, self.main.display.width, self.bars_max_offset)]
        self.sprite = None
        self.sprite_position = (self.main.display.half_width - self.main.sprite_size // 2, self.bars_max_offset + (self.main.display.half_height - self.bars_max_offset - self.main.sprite_size) // 2)
        self.show_text = False
        self.text_id = None
        self.text = None
        self.text_position = (self.main.display.half_width, self.main.display.half_height - 8)
        self.page_index = 0
        self.line_index = 0
        self.character_index = 0
        self.text_speed = (1 - self.cutscene_speed) * 0.5 + self.cutscene_speed * 1
        self.line_pause = (1 - self.cutscene_speed) * 1 + self.cutscene_speed * 0.25
        self.line_timer = 0
        self.show_button = False
        self.button = self.main.assets.images['other']['button_5']
        self.button_position = (self.main.display.half_width - self.button.get_width() // 2, self.main.display.height - self.bars_max_offset - self.button.get_height() * 1.5)
        self.button_alpha = 0
        self.collectable_pause = 2
        self.collectable_timer = 0
        self.collectable_type = None
        self.collectable_position = None
        self.collectable_sprite = None
        self.collectable_sprite_position = None
        self.end_response = None
        self.end_trigger = False
        
        # intro and movement (0, 0), menu (0, 1), map (0, 2), undo/ redo (-1, 2), collectables (-1, 2)?*, locks/ paths (-2, 2), teleporter (-2, 2)?*, ice (-2, 3),
        # conveyors (-2, 1), blue flags (-4, 2), spikes (-5, 3), player spawner (-6, 2), reviving dead players (-4, 0), statues (-6, 0), splitters (-5, -2)
        # add cutscenes for: collectables, teleporters, moving flags/ respawning at original position, final stretch of first game,
        # intro to second game ('i though we were done, but it seems we are only just beginning', 'i can always return to the first place by toggling the map...')
        self.cutscene_data = {'collectables': {'silver keys': [["A silver key, a hopeful chime.", "Yet all it give is more lost time.", "For I am slime, and step I must."],
                                                               ["Each opened lock, a question grows.", "How deep this endless puzzle goes.", "For I am slime, and step I must."]],
                                               'silver gems': [["A silver gem, once left behind.", "Now claimed by me, no longer blind.", "For I am slime, and step I must."],
                                                               ["It sat right there, just out of reach.", "Waiting till the game could teach.", "For I am slime, and step I must."]],
                                               'gold keys': [["A golden key, my fingers tight.", "Yet holding it gives no delight.", "For I am slime, and step I must."],
                                                             ["Each one I find just leads to more.", "Like some unending, thankless chore.", "For I am slime, and step I must."]],
                                               'gold gems': [["A golden gem, so far and bright.", "It hid beyond my skill and sight.", "For I am slime, and step I must."],
                                                             ["Now I return with tricks in hand.", "To claim the prize, to understand.", "For I am slime, and step I must."]],
                                               'cheeses': [["A holey cheese, forbidden prize.", "Hidden where the shadow lies.", "For I am slime, and step I must."],
                                                           ["Through the cracks, I see between.", "To catch a glimpse of endless dream.", "For I am slime, and step I must."]]},
                              'levels': {'(0, 0)': [["I woke up lost, alone, and green.", "No name, no clue, no in-between.", "For I am slime, and step I must."],
                                                    ["The walls don't blink, the rules won't bend.", "I doubt the start, I fear the end.", "For I am slime, and step I must."],
                                                    ["I press a key, the world reacts.", "But steps are few, and truth subtracts.", "For I am slime, and step I must."],
                                                    ["What happens when I've stepped my last?", "Do I dissolve into the past?", "For I am slime, and step I must."],
                                                    ["I know not how, nor why I'm here.", "But onwards now, that much is clear.", "For I am slime, and step I must."],
                                                    ["No turning back, no time to lag.", "My only hope, the next safe flag.", "For I am slime, and step I must."]],
                                         '(0, 1)': [["This world is strange, too much to keep.", "I want to stop, to think, to sleep.", "For I am slime, and step I must."],
                                                    ["If things feel wrong or far too tough.", "I can always pause, sure enough.", "For I am slime, and step I must."]],
                                         '(0, 2)': [["I twist through rooms that loop and bend.", "I'm not quite sure where they all end.", "For I am slime, and step I must."],
                                                    ["I peer at the map to look around.", "To see what paths have yet been found.", "For I am slime, and step I must."]],
                                         '(-1, 2)': [["I took a step I did not mean.", "And now my goal cannot be seen.", "For I am slime, and step I must."],
                                                     ["But my steps are not set in stone.", "Undo or redo, the way is shown.", "For I am slime, and step I must."]],
                                         '(-2, 2)': [["A locked way ahead, shut not wide.", "The paths diverge, I must decide.", "For I am slime, and step I must."],
                                                     ["Each one will teach, each one will test.", "Whatever comes, I'll give my best.", "For I am slime, and step I must."]],
                                         '(-2, 3)': [["I step, then slide, I cannot brake.", "I bounce off walls like some mistake.", "For I am slime, and step I must."],
                                                     ["I look ahead, no chance to turn.", "Just frozen paths that I must learn.", "For I am slime, and step I must."]],
                                         '(-2, 1)': [["The ground now moves without my say.", "It shoves me one more step each way.", "For I am slime, and step I must."],
                                                     ["I try to stop, but can't resist.", "A subtle nudge, I get the gist.", "For I am slime, and step I must."]],
                                         '(-4, 2)': [["It looks the same, but something's wrong.", "This flag won't hold me for very long.", "For I am slime, and step I must."],
                                                     ["It waves with hope, but gives me none.", "A lying cloth, and now I'm undone.", "For I am slime, and step I must."]],
                                         '(-5, 3)': [["These things look sharp, I should beware.", "They stab and slice without a care.", "For I am slime, and step I must."],
                                                     ["Danger waits with every tread.", "I'll lose my life, my body bled.", "For I am slime, and step I must."]],
                                         '(-6, 2)': [["Another me, seeming the same.", "A crude reflection within the game.", "For I am slime, and step I must."],
                                                     ["We share one will, but not one past.", "Who came first, and who was last?", "For I am slime, and step I must."]],
                                         '(-4, 0)': [["One gives their life, the cost is steep.", "So another may rise from endless sleep.", "For I am slime, and step I must."],
                                                     ["A fallen soul begins to stir.", "Brought back to life in a soft blur.", "For I am slime, and step I must."]],
                                         '(-6, 0)': [["The statue's gaze is cold and wide.", "Looked at straight, there's no place to hide.", "For I am slime, and step I must."],
                                                     ["But turn away and slip on past.", "Their stony grip won't hold me fast.", "For I am slime, and step I must."]],
                                         '(-5, -2)': [["A single step, then comes the tear.", "Another me, now stands there.", "For I am slime, and step I must."],
                                                      ["Though of two bodies, our minds the same.", "Working together with one shared aim.", "For I am slime, and step I must."]]}}

    def start_cutscene(self, cutscene_type=None, cutscene_data=None):
        if not self.active:
            if cutscene_type == 'level':
                if ('level_name' in cutscene_data and cutscene_data['level_name'] in self.cutscene_data['levels'] and
                        (cutscene_data['level_name'] not in self.main.assets.data['game']['discovered_levels'] or 'force' in cutscene_data and cutscene_data['force'])):
                    self.active = True
                    self.show_bars = True
            elif cutscene_type == 'collectable':
                if 'collectable_type' in cutscene_data and cutscene_data['collectable_type'] in self.main.assets.data['game']['collectables'] and 'collectable_position' in cutscene_data:
                    self.active = True
                    self.collectable_timer = self.collectable_pause * self.main.fps
                    self.collectable_type = cutscene_data['collectable_type'][:-1]
                    self.collectable_position = cutscene_data['collectable_position']
                    self.main.audio.play_sound(name='collectable')  # temmporary for testing
            if self.active:
                self.cutscene_type = cutscene_type
                self.bars_offset = 0
                self.text_id = cutscene_data['level_name' if cutscene_type == 'level' else 'collectable_type']
                self.text = self.cutscene_data[f'{cutscene_type}s'][cutscene_data['level_name' if cutscene_type == 'level' else 'collectable_type']]
                self.main.text_handler.add_text(text_group='cutscene', text_id='space', text='space', size=10, alpha_up=self.alpha_step, alpha_down=self.alpha_step, bounce=-3, shadow_colour=None,
                                                position=(self.main.display.half_width, self.main.display.height - self.bars_max_offset - self.button.get_height()), display_layer='ui')
                if 'end_response' in cutscene_data:
                    self.end_response = cutscene_data['end_response']

    def update_bars_positions(self):
        self.bars[0].y = -self.bars_max_offset + self.bars_offset
        self.bars[1].y = self.main.display.height - self.bars_offset

    def update_bars(self):
        if self.show_bars:
            self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player', 'level_ui'], effect='pixelate', effect_data={'length': 1})
            if not self.bars_offset:
                self.main.audio.play_sound(name='cutscene_start')
            if self.bars_offset < self.bars_max_offset:
                if self.main.events.check_key(key='space', remove=True):
                    self.main.audio.play_sound(name='cutscene_skip', overlap=True)
                    self.bars_offset = self.bars_max_offset
                else:
                    self.bars_offset = min(self.bars_offset + self.bars_speed, self.bars_max_offset)
                self.update_bars_positions()
                if self.bars_offset == self.bars_max_offset:
                    self.show_text = True
                    self.page_index = 0
                    self.line_index = 0
                    self.character_index = 0
        elif self.bars_offset:
            if self.main.events.check_key(key='space'):
                self.main.audio.play_sound(name='cutscene_skip', overlap=True)
                self.bars_offset = 0
            else:
                self.bars_offset = max(self.bars_offset - self.bars_speed, 0)
            self.update_bars_positions()
            if self.bars_offset == 0:
                self.active = False
                self.cutscene_type = None
                self.button_alpha = 0
                self.main.text_handler.remove_text_group(text_group='cutscene')
                if self.end_response:
                    self.end_trigger = True

    def update_text(self):
        if self.show_text:
            if self.line_timer:
                if self.main.events.check_key(key='space'):
                    self.main.audio.play_sound(name='cutscene_skip', overlap=True)
                    self.line_timer = 0
                else:
                    self.line_timer -= 1
            elif self.character_index < len(self.text[self.page_index][self.line_index]):
                if not self.character_index:
                    self.main.audio.play_sound(name='cutscene_dialogue', overlap=True)
                character_index = self.character_index
                if self.main.events.check_key(key='space', remove=True):
                    self.main.audio.play_sound(name='cutscene_skip', overlap=True)
                    self.character_index = len(self.text[self.page_index][self.line_index])
                    self.line_timer = 1
                else:
                    self.character_index = min(self.character_index + self.text_speed, len(self.text[self.page_index][self.line_index]))
                if int(character_index) != int(self.character_index):
                    text_id = f'{self.text_id}_{self.page_index}_{self.line_index}_{int(self.character_index)}'
                    text = self.text[self.page_index][self.line_index][:int(self.character_index)]
                    self.main.text_handler.add_text(text_group='cutscene', text_id=text_id, text=text, position=(self.text_position[0], self.text_position[1] + 16 * self.line_index),
                                                    display_layer='ui', size=14, max_width=self.main.display.width - 32, alpha_up=255, alpha_down=self.alpha_step, style='itallic')
                    if self.character_index == len(self.text[self.page_index][self.line_index]):  # end of line
                        if self.line_timer:
                            self.line_timer = 0
                        else:
                            self.line_timer = self.line_pause * self.main.fps
                        if self.line_index == len(self.text[self.page_index]) - 1:
                            self.show_button = True
                            self.button_alpha = 0
                            self.button.set_alpha(self.button_alpha)
                        else:
                            self.line_index += 1
                            self.character_index = 0

    def update_button(self):
        if self.show_button:
            if not self.line_timer and self.button_alpha < 255:
                self.button_alpha += self.alpha_step
                self.button.set_alpha(self.button_alpha)
            if self.main.events.check_key(key='space'):
                self.main.audio.play_sound(name='cutscene_skip', overlap=True)
                self.show_button = False
                if self.page_index == len(self.text) - 1:
                    self.main.audio.play_sound(name='cutscene_end')
                    self.show_bars = False
                    self.show_text = False
                else:
                    self.page_index += 1
                    self.line_index = 0
                    self.character_index = 0
        elif self.button_alpha:
            self.button_alpha -= self.alpha_step
            self.button.set_alpha(self.button_alpha)
            if self.button_alpha == 0:
                self.show_button = False

    def get_sprite_alpha(self):
        return 255 * self.bars_offset / self.bars_max_offset

    def stop_cutscene(self):
        self.active = False
        self.show_bars = False
        self.bars_offset = 0
        self.update_bars_positions()
        self.sprite = None
        self.collectable_timer = 0
        self.collectable_sprite = None
        self.show_text = False
        self.show_button = False
        self.button_alpha = 0
        self.button.set_alpha(self.button_alpha)

    def update(self):
        if self.active:
            if self.main.debug and self.main.events.check_key(key='escape'):
                self.stop_cutscene()
            else:
                self.sprite = self.main.utilities.get_sprite(name='player', state='thinking', alpha=self.get_sprite_alpha())
                if self.cutscene_type == 'collectable':
                    if self.collectable_timer:
                        self.main.shaders.apply_effect(display_layer='level_main', effect='shockwave', effect_data={'length': self.collectable_pause, 'x': self.collectable_position[0], 'y': self.collectable_position[1]})
                        self.collectable_timer -= 1
                        if not self.collectable_timer:
                            self.main.shaders.apply_effect(display_layer='level_main', effect=None)
                            self.show_bars = True
                    else:
                        self.collectable_sprite = self.main.utilities.get_sprite(name='collectable', state=self.collectable_type, alpha=self.get_sprite_alpha())
                        self.collectable_sprite_position = (self.main.display.half_width - self.main.sprite_size // 2 + 32 * cos(2 * self.main.runtime_seconds),
                                                            self.bars_max_offset + (self.main.display.half_height - self.bars_max_offset - self.main.sprite_size) // 2 + 16 * sin(2 * self.main.runtime_seconds))
                self.update_bars()
                self.update_text()
                self.update_button()
        return self.active  # do we really need to return this?

    def draw(self, displays):
        if self.active and not self.collectable_timer:
            for bar in self.bars:
                pg.draw.rect(surface=displays['ui'], color=self.main.assets.colours['dark_purple'], rect=bar)
            if self.sprite:
                displays['ui'].blit(source=self.sprite, dest=(self.sprite_position[0], self.sprite_position[1] + self.main.utilities.get_text_bounce(bounce=-3)))
            if self.collectable_sprite:
                displays['ui'].blit(source=self.collectable_sprite, dest=(self.collectable_sprite_position[0], self.collectable_sprite_position[1] + self.main.utilities.get_text_bounce(bounce=-3)))
            if self.show_text:
                for line_index in range(self.line_index + 1):
                    text_id = f'{self.text_id}_{self.page_index}_{line_index}_{int(self.character_index) if line_index == self.line_index else len(self.text[self.page_index][line_index])}'
                    self.main.text_handler.activate_text(text_group='cutscene', text_id=text_id)
            if self.button_alpha:
                displays['ui'].blit(source=self.button, dest=(self.button_position[0], self.button_position[1] + self.main.utilities.get_text_bounce(bounce=-3)))
            if self.show_button and not self.line_timer:
                self.main.text_handler.activate_text(text_group='cutscene', text_id='space')

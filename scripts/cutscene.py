import pygame as pg
from math import sin, cos

class Cutscene:
    def __init__(self, main):
        self.main = main
        self.display_layer = 'level_map'
        self.cutscene_speed = self.main.assets.settings['game']['cutscene_speed']
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
        self.button = self.main.utilities.get_image(group='other', name='button_5')
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

        self.cutscene_data = {'collectables': {'silver keys': [["A silver key, a hopeful chime.", "Yet all it give is more lost time."],
                                                               ["Each opened lock, a question grows.", "How deep this endless puzzle goes."]],
                                               'silver gems': [["A silver gem, once left behind.", "Now claimed by me, no longer blind."],
                                                               ["It sat right there, just out of reach.", "Waiting till the game could teach."]],
                                               'gold keys': [["A golden key, my fingers tight.", "Yet holding it gives no delight."],
                                                             ["Each one I find just leads to more.", "Like some unending, thankless chore."]],
                                               'gold gems': [["A golden gem, so far and bright.", "It hid beyond my skill and sight."],
                                                             ["Now I return with tricks in hand.", "To claim the prize, to understand."]],
                                               'cheeses': [["A holey cheese, forbidden prize.", "Hidden where the shadow lies."],
                                                           ["Through the cracks, I see between.", "To catch a glimpse of endless dream."]]},
                              'levels': {'(0, 0)': [["I woke up lost, alone, and green.", "No name, no clue, no in-between."],
                                                    ["The walls don't blink, the rules won't bend.", "I doubt the start, I fear the end."],
                                                    ["I press a key, the world reacts.", "But steps are few, and truth subtracts."],
                                                    ["What happens when I've stepped my last?", "Do I dissolve into the past?"],
                                                    ["I know not how, nor why I'm here.", "But onwards now, that much is clear."],
                                                    ["No turning back, no time to lag.", "My only hope, the next safe flag."]],
                                         '(0, 1)': [["This world is strange, too much to keep.", "I want to stop, to think, to sleep."],
                                                    ["If things feel wrong or far too tough.", "I can always pause, sure enough."]],
                                         '(0, 2)': [["I twist through rooms that loop and bend.", "I'm not quite sure where they all end."],
                                                    ["I peer at the map to look around.", "To see what paths have yet been found."]],
                                         '(-1, 2)': [["A tempting key, not far from here.", "Perhaps it holds a path unclear."],
                                                     ["A shining gem, off to the side.", "Is it needed, or just pride?"],
                                                     ["I took a step I did not mean.", "And now my goal cannot be seen."],
                                                     ["But my steps are not set in stone.", "Undo or redo, the way is shown."]],
                                         '(-2, 2)': [["A locked way ahead, shut not wide.", "The paths diverge, I must decide."],
                                                     ["Each one will teach, each one will test.", "Whatever comes, I'll give my best."],
                                                     ["No matter where my journey bends.", "This place remains, it never ends."],
                                                     ["Though strange the road and far I roam.", "Some force will always pull me home."]],
                                         '(-2, 3)': [["I step, then slide, I cannot brake.", "I bounce off walls like some mistake."],
                                                     ["I look ahead, no chance to turn.", "Just frozen paths that I must learn."]],
                                         '(-2, 1)': [["The ground now moves without my say.", "It shoves me one more step each way."],
                                                     ["I try to stop, but can't resist.", "A subtle nudge, I get the gist."]],
                                         '(-4, 2)': [["It looks the same, but something's wrong.", "This flag won't hold me for very long."],
                                                     ["It waves with hope, but gives me none.", "A lying cloth, and now I'm undone."]],
                                         '(-5, 3)': [["These things look sharp, I should beware.", "They stab and slice without a care."],
                                                     ["Danger waits with every tread.", "I'll lose my life, my body bled."]],
                                         '(-6, 2)': [["Another me, seeming the same.", "A crude reflection within the game."],
                                                     ["We share one will, but not one past.", "Who came first, and who was last?"]],
                                         '(-4, 0)': [["One gives their life, the cost is steep.", "So another may rise from endless sleep."],
                                                     ["A fallen soul begins to stir.", "Brought back to life in a soft blur."]],
                                         '(-6, 0)': [["The statue's gaze is cold and wide.", "Looked at straight, there's no place to hide."],
                                                     ["But turn away and slip on past.", "Their stony grip won't hold me fast."]],
                                         '(-5, -2)': [["A single step, then comes the tear.", "Another me, now stands there."],
                                                      ["Though of two bodies, our minds the same.", "Working together with one shared aim."]],
                                         '(-4, -2)': [["The air feels still, the walls grown wide.", "As though they've nothing left to hide."]],
                                         '(-3, -2)': [["A path well worn by none before.", "Now pulls me on to something more."]],
                                         '(-2, -2)': [["The way ahead allows no turns.", "A truth awaits I fear to learn."]],
                                         '(-1, -2)': [["Is this the end, or just a door?", "Beyond which waits what came before."]],
                                         '(-1, -5)': [["The portal shivers, and whispers low.", "I've stepped through veils I do not know."],
                                                      ["I see it now, the fog has cleared.", "This is no end, as I had feared."],
                                                      ["Each step I've taken has led to this.", "The start of an endless abyss."],
                                                      ["All up to now, naught but a test.", "I hope I'm ready, no time to rest."],
                                                      ["If there are things still left undone.", "To that first world, I can always run."],
                                                      ["My trusty map, faithful and true.", "Now shows to me, both old and new."]]}}
        self.update_cutscene_text()

    def update_cutscene_text(self):
        for cutscene_data in self.cutscene_data.values():
            for cutscene_text in cutscene_data.values():
                for page in cutscene_text:
                    page.append("For I am slime, and step I must.")

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
            if self.active:
                self.cutscene_type = cutscene_type
                self.bars_offset = 0
                self.text_id = cutscene_data['level_name' if cutscene_type == 'level' else 'collectable_type']
                self.text = self.cutscene_data[f'{cutscene_type}s'][cutscene_data['level_name' if cutscene_type == 'level' else 'collectable_type']]
                self.main.text_handler.add_text(text_group='cutscene', text_id='space', text='space', size=10, alpha_up=self.alpha_step, alpha_down=self.alpha_step, bounce=-3, shadow_colour=None,
                                                position=(self.main.display.half_width, self.main.display.height - self.bars_max_offset - self.button.get_height()), display_layer=self.display_layer)
                if 'end_response' in cutscene_data:
                    self.end_response = cutscene_data['end_response']

    def update_bars_positions(self):
        self.bars[0].y = -self.bars_max_offset + self.bars_offset
        self.bars[1].y = self.main.display.height - self.bars_offset

    def update_bars(self, skip):
        if self.show_bars:
            self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player', 'level_ui'], effect='pixelate', effect_data={'length': 1})
            if not self.bars_offset:
                self.main.audio.play_sound(name='cutscene_start')
            if self.bars_offset < self.bars_max_offset:
                if skip:
                    self.main.audio.play_sound(name='cutscene_skip')
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
            if skip:
                self.main.audio.play_sound(name='cutscene_skip')
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

    def update_text(self, skip):
        if self.show_text:
            if self.line_timer:
                if skip:
                    self.main.audio.play_sound(name='cutscene_skip')
                    self.line_timer = 0
                else:
                    self.line_timer -= 1
            elif self.character_index < len(self.text[self.page_index][self.line_index]):
                if not self.character_index:
                    self.main.audio.play_sound(name='cutscene_dialogue')
                character_index = self.character_index
                if skip:
                    self.main.audio.play_sound(name='cutscene_skip')
                    self.character_index = len(self.text[self.page_index][self.line_index])
                    self.line_timer = 1
                else:
                    self.character_index = min(self.character_index + self.text_speed, len(self.text[self.page_index][self.line_index]))
                if int(character_index) != int(self.character_index):
                    text_id = f'{self.text_id}_{self.page_index}_{self.line_index}_{int(self.character_index)}'
                    text = self.text[self.page_index][self.line_index][:int(self.character_index)]
                    self.main.text_handler.add_text(text_group='cutscene', text_id=text_id, text=text, position=(self.text_position[0], self.text_position[1] + 16 * self.line_index),
                                                    display_layer=self.display_layer, size=14, max_width=self.main.display.width - 32, alpha_up=255, alpha_down=self.alpha_step, style='itallic')
                    if self.character_index == len(self.text[self.page_index][self.line_index]):
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

    def update_button(self, skip):
        if self.show_button:
            if not self.line_timer and self.button_alpha < 255:
                self.button_alpha += self.alpha_step
                self.button.set_alpha(self.button_alpha)
            if skip:
                self.main.audio.play_sound(name='cutscene_skip')
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
                # pass in skip variable here instead of checking for space everywhere...
                skip = self.main.events.check_key(key='space', remove=True)
                self.update_bars(skip=skip)
                self.update_text(skip=skip)
                self.update_button(skip=skip)
        return self.active  # do we really need to return this?

    def draw(self, displays):
        if self.active and not self.collectable_timer:
            for bar in self.bars:
                pg.draw.rect(surface=displays[self.display_layer], color=self.main.assets.colours['dark_purple'], rect=bar)
            if self.sprite:
                displays[self.display_layer].blit(source=self.sprite, dest=(self.sprite_position[0], self.sprite_position[1] + self.main.utilities.get_text_bounce(bounce=-3)))
            if self.collectable_sprite:
                displays[self.display_layer].blit(source=self.collectable_sprite, dest=(self.collectable_sprite_position[0], self.collectable_sprite_position[1] + self.main.utilities.get_text_bounce(bounce=-3)))
            if self.show_text:
                for line_index in range(self.line_index + 1):
                    text_id = f'{self.text_id}_{self.page_index}_{line_index}_{int(self.character_index) if line_index == self.line_index else len(self.text[self.page_index][line_index])}'
                    self.main.text_handler.activate_text(text_group='cutscene', text_id=text_id)
            if self.button_alpha:
                displays[self.display_layer].blit(source=self.button, dest=(self.button_position[0], self.button_position[1] + self.main.utilities.get_text_bounce(bounce=-3)))
            if self.show_button and not self.line_timer:
                self.main.text_handler.activate_text(text_group='cutscene', text_id='space')

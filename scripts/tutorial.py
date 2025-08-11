

class Tutorial:
    def __init__(self, main):
        self.main = main
        self.display_layer = 'level_main'
        self.level_name = self.main.assets.data['game']['level']
        self.keys_counter = self.main.fps * 3
        self.tutorials = self.load_tutorials(tutorials_data={'(0, 0)': {'action': [{'text': 'move', 'position': (12, 8)}], 'keys': [{'text': ['w', '^'], 'position': (12, 6)}, {'text': ['a', '<'], 'position': (11, 7)},
                                                                                                                                    {'text': ['s', 'v'], 'position': (12, 7)}, {'text': ['d', '>'], 'position': (13, 7)}]},
                                                             '(0, 1)': {'action': [{'text': 'menu', 'position': (3, 11)}], 'keys': [{'text': ['esc', 'p'], 'position': (3, 10)}]},
                                                             '(0, 2)': {'action': [{'text': 'map', 'position': (12, 12)}], 'keys': [{'text': ['tab', 'm'], 'position': (12, 11)}]},
                                                             '(-1, 2)': {'action': [{'text': 'undo', 'position': (3, 4)}, {'text': 'redo', 'position': (12, 4)}], 'keys': [{'text': ['z', '4'], 'position': (3, 3)},
                                                                                                                                                                           {'text': ['y', '6'], 'position': (12, 3)}]},
                                                             '(-1, -5)': {'action': [{'text': 'toggle map', 'position': (11, 13)}], 'keys': [{'text': ['space'], 'position': (11, 12)}]}})

    def get_position(self, position, element_type=None):
        return ((104 if element_type == 'button_5' else 108 if element_type == 'button_3' else 112) + (position[0] + (0.5 if element_type=='text' else 0)) * self.main.sprite_size,
                (31 if element_type=='text' else 32) + (position[1] + (0.5 if element_type=='text' else 0)) * self.main.sprite_size)

    def load_tutorials(self, tutorials_data):
        for level_name, tutorial_data in tutorials_data.items():
            for action_data in tutorial_data['action']:
                self.main.text_handler.add_text(text_group='tutorial', text_id=f'{level_name}_{action_data['text']}', text=action_data['text'], size=18, alpha_up=8.5, alpha_down=8.5, bounce=3,
                                                position=self.get_position(position=action_data['position'], element_type='text'), shadow_colour=None, display_layer=self.display_layer)
            tutorial_data['sprites'] = []
            tutorial_data['active_keys'] = 0
            tutorial_data['keys_count'] = len(tutorial_data['keys'][0]['text'])
            tutorial_data['keys_counter'] = self.keys_counter
            for key_data in tutorial_data['keys']:
                max_length = 0
                for key_text in key_data['text']:
                    max_length = max(max_length, len(key_text))
                    self.main.text_handler.add_text(text_group='tutorial', text_id=f'{level_name}_{key_text}', text=key_text, size=10, alpha_up=8.5, alpha_down=8.5, bounce=3,
                                                    position=self.get_position(position=key_data['position'], element_type='text'), shadow_colour=None, display_layer=self.display_layer)
                sprite_type = f'button_{max_length}'
                tutorial_data['sprites'].append({'type': sprite_type, 'position': self.get_position(position=key_data['position'], element_type=sprite_type)})
        return tutorials_data

    def transition_level(self, level_name):
        self.level_name = level_name
        if self.level_name in self.tutorials:
            tutorial_data = self.tutorials[self.level_name]
            if tutorial_data['keys_count'] > 1:
                tutorial_data['active_keys'] = 0
                tutorial_data['keys_counter'] = self.keys_counter

    def update_level(self, level_name):
        if level_name != self.level_name:
            self.transition_level(level_name=level_name)

    def update(self):
        if self.level_name in self.tutorials:
            tutorial_data = self.tutorials[self.level_name]
            if tutorial_data['keys_count'] > 1:
                tutorial_data['keys_counter'] -= 1
                if not tutorial_data['keys_counter']:
                    tutorial_data['keys_counter'] = self.keys_counter
                    tutorial_data['active_keys'] = (tutorial_data['active_keys'] + 1) % tutorial_data['keys_count']

    def draw(self, displays):
        if self.level_name in self.tutorials:
            tutorial_data = self.tutorials[self.level_name]
            for action in tutorial_data['action']:
                self.main.text_handler.activate_text(text_group='tutorial', text_id=f'{self.level_name}_{action['text']}')
            for key in tutorial_data['keys']:
                self.main.text_handler.activate_text(text_group='tutorial', text_id=f'{self.level_name}_{key['text'][tutorial_data['active_keys']]}')
            for sprite in tutorial_data['sprites']:
                displays[self.display_layer].blit(source=self.main.assets.images['other'][sprite['type']], dest=(sprite['position'][0], sprite['position'][1] + self.main.utilities.get_text_bounce(bounce=3)))

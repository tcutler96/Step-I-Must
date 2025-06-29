import pygame as pg


class Toolbar:
    def __init__(self, main):
        self.main = main
        self.text_position = (288, 16)
        self.text_size = 20
        self.max_width = 174
        self.cell_marker_offset = (-3, -3)
        self.element_choices = {'objects': {'no object': ['no object'], 'player': ['idle', 'dead'], 'permanent flag': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
                                            'temporary flag': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 'rock': ['rock'], 'statue': ['statue'],
                                            'collectable': ['silver key', 'silver gem', 'gold key', 'gold gem', 'cheese']},
                                'tiles': {'no tile': ['no tile'], 'wall': ['centre'], 'ice': ['ice'], 'conveyor': ['up', 'right', 'down', 'left'], 'spike': ['spike'],
                                          'player spawner': ['player spawner'], 'splitter': ['vertical', 'horizontal'], 'barrier': ['vertical', 'horizontal'],
                                          'teleporter': ['reciever', 'sender', 'portal'], 'lock': ['lock'], 'sign': ['sign'], 'star reseter': ['star reseter']}}
        self.button_choices = {'top': {'Reset Level': 'reset', 'Toggle Grid': 'grid', 'Play Level': 'play'}, 'right': {'Save Level': 'save', 'Load Level': 'load', 'Quit to Main Menu': 'quit'}}
        self.toolbar = self.get_toolbar()
        self.hovered_element = [None, None]
        self.selected_object = ['no object', 0]
        self.selected_tile = ['no tile', 0]

    def get_toolbar(self):
        toolbar = {'background_rects': [pg.Rect(4, 4, 24 * (len(self.element_choices['objects']) + 1), 24), pg.Rect(4, 4, 24, 24 * (len(self.element_choices['tiles']) + 1)),
                                        pg.Rect(self.main.display.width - 4, 4, -24 * (len(self.button_choices['top']) + 1), 24),
                                        pg.Rect(self.main.display.width - 4, 4, -24, 24 * (len(self.button_choices['top']) + 1))]}
        buttons = {}
        for button_type in self.button_choices:
            for button_count, button_name in enumerate(self.button_choices[button_type]):
                button_position = (self.main.display.width - 24 - (24 * (button_count + 1) if button_type == 'top' else 0), 8 + (24 * (button_count + 1) if button_type == 'right' else 0))
                buttons[button_name] = {'position': button_position, 'sprite': self.main.assets.images['toolbar'][self.button_choices[button_type][button_name]],
                                        'rect': pg.Rect(button_position[0] - 4, button_position[1] - 4, 24, 24)}
                self.main.text_handler.add_text(text_group='toolbar', text_id=button_name, text=button_name, position=self.text_position, alignment=('c', 'c'), size=self.text_size, max_width=self.max_width)
        toolbar['buttons'] = buttons
        elements = {}
        for element_type in self.element_choices:
            for name_count, element_name in enumerate(self.element_choices[element_type]):
                if element_name == 'no object':
                    element_data = {'position': [(32, 8)], 'rects': [pg.Rect(28, 4, 24, 24)], 'states': ['no object'], 'num_choices': 1, 'element_type': 'object'}
                    self.main.text_handler.add_text(text_group='toolbar', text_id='no object' + 'no object', text='no object', position=self.text_position, alignment=('c', 'c'), size=self.text_size, max_width=self.max_width)
                elif element_name == 'no tile':
                    element_data = {'position': [(8, 32)], 'rects': [pg.Rect(4, 28, 24, 24)], 'states': ['no tile'], 'num_choices': 1, 'element_type': 'tile'}
                    self.main.text_handler.add_text(text_group='toolbar', text_id='no tile' + 'no tile', text='no tile', position=self.text_position, alignment=('c', 'c'), size=self.text_size, max_width=self.max_width)
                else:
                    element_data = {'position': [], 'rects': [], 'states': []}
                    for state_count, element_state in enumerate(self.element_choices[element_type][element_name]):
                        sprite_position = (8 + (24 * (name_count + 1) if element_type == 'objects' else 0) + (24 * state_count if element_type == 'tiles' else 0),
                                           8 + (24 * (name_count + 1) if element_type == 'tiles' else 0) + (24 * state_count if element_type == 'objects' else 0))
                        element_data['position'].append(sprite_position)
                        element_data['rects'].append(pg.Rect(sprite_position[0] - 4, sprite_position[1] - 4, 24, 24))
                        element_data['states'].append(element_state)
                        self.main.text_handler.add_text(text_group='toolbar', text_id=element_name + element_state, text=element_name + (' - ' + element_state if element_state != element_name else ''),
                                                        position=self.text_position, alignment=('c', 'c'), size=self.text_size, max_width=self.max_width)
                    element_data['num_choices'] = len(element_data['position'])
                    element_data['element_type'] = element_type[:-1]
                    if element_data['num_choices'] > 1:
                        element_data['hover_rect'] = pg.Rect(element_data['rects'][0][0], element_data['rects'][0][1], 24 * element_data['num_choices'] if element_data['element_type'] == 'tile' else 24,
                                                             24 * element_data['num_choices'] if element_data['element_type'] == 'object' else 24)
                elements[element_name] = element_data
        toolbar['elements'] = elements
        return toolbar

    def set_toolbar(self, elements):
        self.selected_object = ['no object', 0]
        self.selected_tile = ['no tile', 0]
        if elements['object']:
            self.selected_object = [elements['object']['name'], self.element_choices['objects'][elements['object']['name']].index(elements['object']['state'])]
        elif elements['player']:
            self.selected_object = [elements['player']['name'], self.element_choices['objects'][elements['player']['name']].index(elements['player']['state'])]
        if elements['tile']:
            self.selected_tile = [elements['tile']['name'], self.element_choices['tiles'][elements['tile']['name']].index(elements['tile']['state'])]
        elif elements['vertical_barrier']:
            self.selected_tile = [elements['vertical_barrier']['name'], self.element_choices['tiles'][elements['vertical_barrier']['name']].index(elements['vertical_barrier']['state'])]
        elif elements['horizontal_barrier']:
            self.selected_tile = [elements['horizontal_barrier']['name'], self.element_choices['tiles'][elements['horizontal_barrier']['name']].index(elements['horizontal_barrier']['state'])]


    def update(self, mouse_position):
        hovered_element = self.hovered_element
        selected_elememt = None
        self.hovered_element = [None, None]
        for button_name, button_data in self.toolbar['buttons'].items():
            if button_data['rect'].collidepoint(mouse_position):
                self.main.display.set_cursor(cursor='hand')
                self.hovered_element = button_name
                if self.main.events.check_key(key='mouse_1'):
                    selected_elememt = ['button', button_name]
        if not selected_elememt:
            for element_name, element_data in self.toolbar['elements'].items():
                for count, rect in enumerate(element_data['rects']):
                    if count and element_name != hovered_element[0]:
                        break
                    if rect.collidepoint(mouse_position):
                        self.hovered_element = [element_name, count]
                        self.main.display.set_cursor(cursor='hand')
                        if self.main.events.check_key(key='mouse_1'):
                            if element_data['element_type'] == 'object':
                                if [element_name, count] != self.selected_object:
                                    self.selected_object = [element_name, count]
                                    selected_elememt = [element_data['element_type'], self.selected_object[0], self.element_choices['objects'][self.selected_object[0]][self.selected_object[1]]]
                            elif element_data['element_type'] == 'tile':
                                if [element_name, count] != self.selected_tile:
                                    self.selected_tile = [element_name, count]
                                    selected_elememt = [element_data['element_type'], self.selected_tile[0], self.element_choices['tiles'][self.selected_tile[0]][self.selected_tile[1]]]
        return selected_elememt

    def draw(self, displays):
        for background_rect in self.toolbar['background_rects']:
            pg.draw.rect(surface=displays['level_editor'], color=self.main.assets.colours['dark_purple'], rect=background_rect, border_radius=5)
        for button_name, button_data in self.toolbar['buttons'].items():
            displays['level_editor'].blit(source=button_data['sprite'], dest=button_data['position'])
            if button_name == self.hovered_element:
                self.main.text_handler.activate_text(text_group='toolbar', text_id=button_name)
                displays['level_editor'].blit(source=self.main.assets.images['toolbar']['marker'], dest=(button_data['position'][0] + self.cell_marker_offset[0], button_data['position'][1]  + self.cell_marker_offset[1]))
        for element_name, element_data in self.toolbar['elements'].items():
            if element_name == self.hovered_element[0] and element_data['num_choices'] > 1:
                self.main.text_handler.activate_text(text_group='toolbar', text_id=element_name + element_data['states'][self.hovered_element[1]])
                pg.draw.rect(surface=displays['level_editor'], color=self.main.assets.colours['cream'], rect=element_data['hover_rect'], border_radius=5)
            if element_name != self.hovered_element[0] and element_name == (self.selected_object[0] if element_data['element_type'] == 'object' else self.selected_tile[0]):
                pg.draw.rect(surface=displays['level_editor'], color=self.main.assets.colours['bright_green'], rect=pg.Rect(element_data['position'][0][0] - 2, element_data['position'][0][1] - 2, 20, 20), border_radius=3)
                if element_name == 'player' and element_data['states'][self.selected_object[1]] == 'idle':
                    sprite = self.main.utilities.get_sprite(name='player respawn')
                    sprite.blit(source=self.main.utilities.get_sprite(name='player', state='idle'), dest=(0, 0))
                else:
                    sprite = self.main.utilities.get_sprite(name=element_name, state=element_data['states'][self.selected_object[1] if element_data['element_type'] == 'object' else self.selected_tile[1]])
                displays['level_editor'].blit(source=sprite, dest=element_data['position'][0])
            else:
                for count, (position, state) in enumerate(zip(element_data['position'] if element_name == self.hovered_element[0] else [element_data['position'][0]],
                                            element_data['states'] if element_name == self.hovered_element[0] else [element_data['states'][0]])):
                    if element_name == 'player' and state == 'idle':
                        sprite = self.main.utilities.get_sprite(name='player respawn')
                        sprite.blit(source=self.main.utilities.get_sprite(name='player', state='idle'), dest=(0, 0))
                    else:
                        sprite = self.main.utilities.get_sprite(name=element_name, state=state)
                    if [element_name, count] == (self.selected_object if element_data['element_type'] == 'object' else self.selected_tile):
                        pg.draw.rect(surface=displays['level_editor'], color=self.main.assets.colours['bright_green'], rect=pg.Rect(position[0] - 2, position[1] - 2, 20, 20), border_radius=3)
                    displays['level_editor'].blit(source=sprite, dest=position)
                    if element_name == self.hovered_element[0] and count == self.hovered_element[1]:
                        displays['level_editor'].blit(source=self.main.assets.images['toolbar']['marker'], dest=(position[0] + self.cell_marker_offset[0], position[1] + self.cell_marker_offset[1]))
                        self.main.text_handler.activate_text(text_group='toolbar', text_id=element_name + element_data['states'][self.hovered_element[1]])

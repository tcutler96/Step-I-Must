from scripts.text_element import TextElement
from math import sin, cos


class TextHandler:
    def __init__(self, main):
        self.main = main
        self.text_bounce = 0  # menu/ level elements: 3, level ui: -3
        self.shadow_sway = 0
        self.sign_lines = {}
        self.text_elements = {}
        self.add_text(text_group='main', text_id='debug', text='debug mode', position='bottom', colour='purple', size=16)
        self.add_text(text_group='main', text_id='debug_required', text='debug mode required', position='top')
        self.add_text(text_group='main', text_id='backup_data', text='data backed up', position='top')
        self.add_text(text_group='main', text_id='backup_settings', text='settings backed up', position='top')
        self.add_text(text_group='main', text_id='clear_game_data', text='game data cleared', position='top')
        self.add_text(text_group='main', text_id='restore_data', text='data restored', position='top')
        self.add_text(text_group='main', text_id='restore_settings', text='settings restored', position='top')
        self.add_text(text_group='main', text_id='conway', text="conway's game of life", position='top', colour='cream', shadow_colour=None, outline_colour=None, display_layer='background')
        self.add_text(text_group='splash', text_id='tcgame', text='a tc game', position='centre', alpha_up=8.5, alpha_down=8.5, size=24, shadow_offset='mouse')
        self.add_text(text_group='splash', text_id='hoolio', text='with hoolio audio', position='centre', alpha_up=8.5, alpha_down=8.5, size=28, shadow_offset='mouse')
        self.add_text(text_group='splash', text_id='...', text='...', position='centre', alpha_up=8.5, alpha_down=8.5, colour='purple', size=28)
        self.add_text(text_group='level_editor', text_id='controls', text='Controls', position=(426, 232), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, style='underline', display_layer='level_map')
        self.add_text(text_group='level_editor', text_id='place', text='Place cell: LMB', position=(426, 248), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='level_editor', text_id='copy', text='Copy cell: MMB', position=(426, 264), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='level_editor', text_id='clear', text='Clear cell: RMB', position=(426, 280), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='level_editor', text_id='reset', text='level reset', position='bottom_right', bounce=-3, alignment=('r', 'c'))
        self.add_text(text_group='level_editor', text_id='saved', text='level saved', position='bottom_right', bounce=-3, alignment=('r', 'c'))
        self.add_text(text_group='game', text_id='reset', text='move to reset', position='centre', bounce=-3, display_layer='level_ui')
        self.add_text(text_group='game', text_id='warp', text=f"press 'e' to warp", position='top', bounce=-3, display_layer='level_main')
        self.add_text(text_group='game', text_id='set_warp', text=f"press 'e' to set warp", position='top', bounce=-3, display_layer='level_main')
        self.add_text(text_group='game', text_id='warp?', text=f"{{*<¡>*}} press 'e' to warp {{*<¡>*}}", position='top', bounce=-3, display_layer='level_main', style='itallic')
        self.add_text(text_group='map', text_id='collectables', text='Collectables', position=(424, 40), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, style='underline', display_layer='level_map')
        for steps in range(-9, 10):
            self.add_text(text_group='steps', text_id=steps, text=str(steps), position='top_left', bounce=-3, alignment=('l', 'c'), display_layer='level_main')
        self.add_sign_text()
        self.add_text(text_group='map', text_id='controls', text='Controls', position=(56, 40), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, style='underline', display_layer='level_map')
        self.add_text(text_group='map', text_id='move', text='Move: wasd | arrows', position=(56, 56), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='map', text_id='menu', text='Menu: escape | p', position=(56, 72), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='map', text_id='map', text='Map: tab | m', position=(56, 88), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='map', text_id='undo', text='Undo: z | 4', position=(56, 104), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='map', text_id='redo', text='Redo: c | 6', position=(56, 120), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.add_text(text_group='map', text_id='toggle_map', text='Toggle map: space', position=(56, 136), alpha_up=8.5, alpha_down=8.5, bounce=-3, alignment=('c', 'c'), size=14, max_width=104, display_layer='level_map')
        self.game_state_text_groups = {'game': ['tutorial', 'cutscene', 'game', 'map', 'steps', 'collectables', 'locks', 'signs', 'game_paused', 'options', 'video', 'shaders', 'audio', 'gameplay', 'developer', 'quit_game'],
                                       'level_editor': ['title_screen', 'level_editor', 'toolbar', 'choose_level'],
                                       'main_menu': ['title_screen', 'options', 'video', 'shaders', 'audio', 'gameplay', 'developer', 'quit_game', 'new_game', 'are_you_sure', 'choose_level'],
                                       'splash': ['splash']}

    def add_text(self, text_group, text_id, text, position, bounce=3, alpha_up=25.5, alpha_down=25.5, alignment=('c', 'c'), colour='light_green', bg_colour=None, shadow_colour='dark_purple', shadow_offset='sway',
                 outline_colour='dark_purple', outline_size=1, size=20, max_width=0, max_height=0, font='Alagard', style=None, display_layer='ui', menu_state=None, active=False, delay=0, duration=0,
                 interactable=False, hovered_colour='green', hovered_bg_colour=None, hovered_shadow_colour=None, hovered_shadow_offset=None, hovered_outline_colour='dark_purple', hovered_outline_size=2):
        if self.check_text_element(text_group=text_group, text_id=text_id):
            del self.text_elements[text_group][text_id]
        position = self.main.utilities.convert_position(position=position)
        colour, bg_colour, shadow_colour, hovered_colour, hovered_bg_colour, hovered_shadow_colour = (
            self.main.utilities.convert_colours(colours=[colour, bg_colour, shadow_colour, hovered_colour, hovered_bg_colour, hovered_shadow_colour]))
        surface = self.main.utilities.draw_text(text=text, colour=colour, bg_colour=bg_colour, shadow_colour=shadow_colour, outline_colour=outline_colour, outline_size=outline_size,
                                                size=size, max_width=max_width, max_height=max_height, font=font, style=style)
        alligned_position = self.main.utilities.align_position(size=surface[0].get_size() if isinstance(surface, tuple) else surface.get_size(), position=position, alignment=alignment)
        hovered_surface = self.main.utilities.draw_text(text=text, colour=hovered_colour, bg_colour=hovered_bg_colour, shadow_colour=hovered_shadow_colour, outline_colour=hovered_outline_colour,
                                                        outline_size=hovered_outline_size, size=size, max_width=max_width, max_height=max_height, font=font, style=style) if interactable else None
        # outline_difference = hovered_outline_size - outline_size
        # alligned_hovered_position = (alligned_position[0] - outline_difference, alligned_position[1] - outline_difference)
        if text_group not in self.text_elements:
            self.text_elements[text_group] = {}
        if display_layer not in self.main.display.display_layers:
            print(f"'{display_layer}' display layer not found for text {text_group}, {text_id}, {text}...")
            display_layer = 'ui'
        self.text_elements[text_group][text_id] = TextElement(main=self.main, text=text, surface=surface, position=alligned_position, bounce=bounce, alpha_up=alpha_up, alpha_down=alpha_down, shadow_offset=shadow_offset,
                                                              display_layer=display_layer, menu_state=menu_state, active=active, delay=delay * self.main.fps, duration=duration * self.main.fps,
                                                              interactable=interactable,  hovered_surface=hovered_surface, hovered_position=alligned_position, hovered_shadow_offset=hovered_shadow_offset)

    def add_sign_text(self):
        for sign_position, sign_text in self.main.assets.data['signs'].items():
            words = sign_text.split(' ')
            lines = [words[0]]
            for word in words[1:]:
                if len(lines[-1]) + len(word) < 30:
                    lines[-1] += (" " + word)
                else:
                    lines.append(word)
            cell_position = self.main.utilities.position_str_to_tuple(position=sign_position.split(' - ')[-1])
            text_position = (112 + (cell_position[0] + 0.5) * 16, 32 + (cell_position[1] + ((len(lines) + 0.5) if cell_position[1] < 8 else -0.5)) * 16)
            for offset, text in enumerate(reversed(lines)):
                self.add_text(text_group='signs', text_id=f'{sign_position}_{offset}', text=text, position=(text_position[0], text_position[1] - 16 * offset), size=12, bounce=3, display_layer='level_main')
                self.sign_lines[sign_position] = offset + 1

    def remove_text(self, text_group, text_id):
        if self.check_text_element(text_group=text_group, text_id=text_id):
            del self.text_elements[text_group][text_id]

    def remove_text_group(self, text_group):
        if text_group in self.text_elements:
            del self.text_elements[text_group]

    def check_text_element(self, text_group, text_id):
        return text_group in self.text_elements and text_id in self.text_elements[text_group]

    def activate_text(self, text_group, text_id, delay=0, duration=0, offset=(0, 0)):
        if self.check_text_element(text_group=text_group, text_id=text_id):
            self.text_elements[text_group][text_id].activate(delay=delay, duration=duration, offset=offset)

    def deactivate_text(self, text_group, text_id):
        if self.check_text_element(text_group=text_group, text_id=text_id):
            self.text_elements[text_group][text_id].deactivate()

    def deactivate_text_group(self, text_group):
        if text_group in self.text_elements:
            for text_id in self.text_elements[text_group]:
                self.text_elements[text_group][text_id].deactivate()

    def update(self, mouse_position):
        self.text_bounce = sin(2 * self.main.runtime_seconds)
        self.shadow_sway = (2 * sin(2 * self.main.runtime_seconds), cos(self.main.runtime_seconds))
        for text_group, text_ids in self.text_elements.items():
            for text_id, text_element in text_ids.items():
                text_element.update(mouse_position=mouse_position, bounce=self.text_bounce, sway=self.shadow_sway)

    def draw(self, displays):
        for text_group, text_ids in self.text_elements.items():
            if text_group in self.game_state_text_groups[self.main.game_state] or text_group == 'main':
                for text_id, text_element in text_ids.items():
                    text_element.draw(displays=displays)

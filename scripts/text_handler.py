from scripts.text_element import TextElement


class TextHandler:
    def __init__(self, main):
        self.main = main
        # add way to move text element shadow over time, have preset choices (ie sin sway)...
        # and way to move text elements so that they bounce up and down with the game cycle...
        self.text_elements = {}
        self.add_text(text_group='main', text_id='debug', text='debug mode', position='top', colour='purple', size=16)
        self.add_text(text_group='main', text_id='conway', text="conway's game of life", position='top', colour='cream', shadow_colour=None, outline_colour=None, display_layer='background')
        self.add_text(text_group='splash', text_id='tcgame', text='a tc game', position='centre', alpha_step=8.5, colour='purple', size=24)
        self.add_text(text_group='splash', text_id='hoolioes', text='with hoolioes audio', position='centre', alpha_step=8.5, colour='purple', size=24)
        self.add_text(text_group='splash', text_id='...', text='...', position='centre', alpha_step=8.5, colour='purple', size=24)
        self.add_text(text_group='level_editor', text_id='reset', text='level reset', position='bottom')
        self.add_text(text_group='level_editor', text_id='saved', text='level saved', position='bottom')
        self.add_text(text_group='game', text_id='reset', text='move to reset', position='centre', display_layer='level')
        self.add_text(text_group='game', text_id='warp', text=f"press 'e' to warp", position='top', display_layer='level')
        self.add_text(text_group='game', text_id='set_warp', text=f"press 'e' to set warp", position='top', display_layer='level')
        self.add_text(text_group='game', text_id='warp?', text=f"¡ ¿ ? !  press 'e' to warp  ! ? ¿ ¡", position='top', display_layer='level')
        self.add_text(text_group='map', text_id='toggle', text="toggle map: 'tab'", position='bottom_left', alpha_step=8.5, shadow_offset=(2, 2),
                      alignment=('l', 'c'), outline_size=0, size=14, interactable=True, hovered_outline_size=1, display_layer='map')
        self.add_text(text_group='map', text_id='switch', text="switch map: 'space'", position='bottom_right', alpha_step=8.5, shadow_offset=(2, 2),
                      alignment=('r', 'c'), outline_size=0, size=14, interactable=True, hovered_outline_size=1, display_layer='map')
        self.add_text(text_group='map', text_id='collectables', text='collectables', position=(424, 40), alpha_step=8.5, shadow_offset=(2, 2), alignment=('c', 'c'), outline_size=0, size=14, display_layer='map')
        self.add_text(text_group='map', text_id='tracker_1', text='World 1: 100%', position=(424, 252), alpha_step=8.5, shadow_offset=(2, 2), alignment=('c', 'c'), outline_size=0, size=14, display_layer='map')
        self.add_text(text_group='map', text_id='tracker_2', text='World 2: 32%', position=(424, 266), alpha_step=8.5, shadow_offset=(2, 2), alignment=('c', 'c'), outline_size=0, size=14, display_layer='map')
        self.add_text(text_group='map', text_id='tracker_3', text='Overall: 46%', position=(424, 280), alpha_step=8.5, shadow_offset=(2, 2), alignment=('c', 'c'), outline_size=0, size=14, display_layer='map')
        for steps in range(-9, 10):
            self.add_text(text_group='steps', text_id=steps, text=str(steps), position='top_left', alignment=('l', 'c'), display_layer='steps')
        for collectable in self.main.assets.data['game']['collectables']:
            self.add_text(text_group='collectables', text_id=collectable, text=f'{collectable[:-1]} collected!', position='bottom', outline_size=1, display_layer='level')
        self.add_text(text_group='signs', text_id='(-2, 2) - (6, 8)', text='this is a sign text test', position='centre', size=10, outline_size=1, display_layer='level')
        self.game_state_text_groups = {'game': ['game', 'map', 'steps', 'collectables', 'locks', 'signs', 'game_paused', 'options', 'video', 'audio', 'gameplay'],
                                       'level_editor': ['title_screen', 'level_editor', 'toolbar', 'choose_level'],
                                       'main_menu': ['title_screen', 'options', 'video', 'audio', 'gameplay', 'new_game', 'are_you_sure', 'choose_level'], 'splash': ['splash']}

    def check_text_element(self, text_group, text_id):
        return text_group in self.text_elements and text_id in self.text_elements[text_group]

    def add_text(self, text_group, text_id, text, position, alpha_step=25.5, alignment=('c', 'c'), colour='light_green', bg_colour=None, shadow_colour='dark_purple', shadow_offset=(4, 4),
                 outline_colour='dark_purple', outline_size=1, size=20, max_width=0, max_height=0, font='Alagard', style=None, display_layer='ui', menu_state=None, active=False, delay=0, duration=0,
                 interactable=False, hovered_colour='green', hovered_bg_colour=None, hovered_shadow_colour=None, hovered_shadow_offset=None, hovered_outline_colour='dark_purple', hovered_outline_size=2):
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
        self.text_elements[text_group][text_id] = TextElement(main=self.main, text=text, surface=surface, position=alligned_position, alpha_step=alpha_step, shadow_offset=shadow_offset,
                                                              display_layer=display_layer, menu_state=menu_state, active=active, delay=delay * self.main.fps, duration=duration * self.main.fps,
                                                              interactable=interactable,  hovered_surface=hovered_surface, hovered_position=alligned_position, hovered_shadow_offset=hovered_shadow_offset)

    def activate_text(self, text_group, text_id, delay=0, duration=0, offset=(0, 0)):
        if self.check_text_element(text_group=text_group, text_id=text_id):
            self.text_elements[text_group][text_id].activate(delay=delay, duration=duration, offset=offset)

    def deactivate_text(self, text_group, text_id):
        if self.check_text_element(text_group=text_group, text_id=text_id):
            self.text_elements[text_group][text_id].deactivate()

    def update(self, mouse_position):
        for text_group, text_ids in self.text_elements.items():
            for text_id, text_element in text_ids.items():
                text_element.update(mouse_position=mouse_position)

    def draw(self, displays):
        for text_group, text_ids in self.text_elements.items():
            if text_group in self.game_state_text_groups[self.main.game_state] or text_group == 'main':
                for text_id, text_element in text_ids.items():
                    text_element.draw(displays=displays)

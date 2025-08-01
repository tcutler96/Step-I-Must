

class MenuElement:
    def __init__(self, main, menu_name, name, position, element_data, data):
        self.main = main
        self.menu_name = menu_name
        self.name = name
        self.sprite = None
        self.sprite_position = None
        self.option_width = int(self.main.display.size[0] * 0.75)
        if isinstance(element_data, str):
            self.element_type = element_data
        else:
            self.element_type, self.button_type, self.button_response = element_data
        self.data = data
        if self.element_type == 'title':
            if self.name.endswith('.png'):
                self.sprite = self.main.assets.images['other'][self.name[:-4]]
                self.sprite_position = (position[0] - self.sprite.get_width() // 2, position[1] - self.sprite.get_height() // 2)
            else:
                self.main.text_handler.add_text(text_group=self.menu_name, text_id=self.name, text=self.name.upper(), position=position, alignment=('c', 'c'), shadow_offset='mouse',
                                                size=self.data['title_size'], font=self.data['title_font'], style=['underline'], display_layer='menu', menu_state=menu_name)
        elif self.element_type == 'button':
            interactable = self.button_type != 'option'
            self.main.text_handler.add_text(text_group=self.menu_name, text_id=self.name, text=self.name + (':' if self.button_type == 'option' else ''),
                                            position=(position[0] - (self.option_width // 2 if self.button_type == 'option' else 0), position[1]),
                                            alignment=('l', 'c') if self.button_type == 'option' else ('c', 'c'), size=self.data['button_size'], shadow_offset='mouse',
                                            font=self.data['button_font'], display_layer='menu', menu_state=menu_name, interactable=interactable)
            self.centre = self.main.text_handler.text_elements[self.menu_name][self.name].rect.center
            if self.button_type == 'option':
                self.option_centres = []
                for option in self.button_response:
                    self.main.text_handler.add_text(text_group=self.menu_name, text_id=self.name + option, text=option, position=(position[0] + self.option_width // 2, position[1]), alignment=('r', 'c'),
                                                    shadow_offset='mouse', size=self.data['button_size'], font=self.data['button_font'], display_layer='menu', menu_state=menu_name, interactable=True)
                    self.option_centres.append(self.main.text_handler.text_elements[self.menu_name][self.name + option].rect.center)
        self.offset = [0, 0]
        self.offset_step = 5
        self.offset_start = [-50, 0]

    def cycle_option(self, selected):
        if selected == 'left':
            self.button_response.append(self.button_response.pop(0))
            self.option_centres.append(self.option_centres.pop(0))
        elif selected == 'right':
            self.button_response.insert(0, self.button_response.pop())
            self.option_centres.insert(0, self.option_centres.pop())
            self.main.events.remove_key(key='mouse_3')

    def update(self, offset, scroll):
        if self.offset[0] < 0:
            self.offset[0] += self.offset_step
        if not self.sprite:
            self.main.text_handler.text_elements[self.menu_name][self.name].scroll = scroll
            if self.element_type == 'button' and self.button_type == 'option':
                self.main.text_handler.text_elements[self.menu_name][self.name + self.button_response[0]].scroll = scroll
            if offset == [0, 0] and self.offset == [0, 0] and not self.main.transition.transitioning:
                if self.element_type == 'button':
                    selected = self.main.text_handler.text_elements[self.menu_name][self.name + (self.button_response[0] if self.button_type == 'option' else '')].selected
                    if selected:
                        if self.button_type == 'option':
                            self.offset = self.offset_start.copy()
                            self.cycle_option(selected=selected)
                            return self.button_type, self.button_response, selected
                        elif selected == 'left':
                            return self.button_type, self.button_response, self.name
                    elif self.name in ['Back', 'Resume', 'No']:
                        if self.main.events.check_key(key=['mouse_3', 'escape']):
                            self.main.events.remove_key(key=['mouse_3', 'escape'])
                            return self.button_type, self.button_response
                        elif self.main.events.check_key(key='p') and self.menu_name == 'game_paused':
                            self.main.events.remove_key(key='p')
                            return self.button_type, self.button_response

    def draw(self, displays, offset):
        if self.sprite:
            displays['ui'].blit(source=self.sprite, dest=(self.sprite_position[0], self.sprite_position[1] + offset[1] + self.main.text_handler.text_bounce * 3))
        self.main.text_handler.activate_text(text_group=self.menu_name, text_id=self.name, offset=offset)
        if self.element_type == 'button' and self.button_type == 'option':
            self.main.text_handler.activate_text(text_group=self.menu_name, text_id=self.name + self.button_response[0], offset=[sum(x) for x in zip(offset, self.offset)])

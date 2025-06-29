from scripts.menu_element import MenuElement
from scripts.menu_scrollbar import MenuScrollbar
from math import ceil


class Menu:
    def __init__(self, main, menu_name, menu_data):
        self.main = main
        self.menu_name = menu_name
        self.data = {'title_font': 'Alagard', 'title_size': 50, 'button_font': 'Alagard', 'button_size': 24}
        self.menu_centre = (self.main.display.half_width, self.main.display.half_height - self.data['button_size'] // 2)
        self.max_rows = (self.main.display.height - self.menu_centre[1]) // self.data['button_size'] - 1
        self.choose_level_columns = 3
        self.column_positions = {1: {0: 0},
                                 2: {0: int(-self.main.display.half_width * 0.25), 1: int(self.main.display.half_width * 0.25)},
                                 3: {0: int(-self.main.display.half_width * 0.55), 1: 0, 2: int(self.main.display.half_width * 0.55)}}
        self.menu, self.max_scroll = self.get_menu(menu_data=menu_data)
        self.scrollbar = MenuScrollbar(main=self.main, max_scroll=self.max_scroll, scroll_step=self.data['button_size']) if self.max_scroll else None
        self.offset = [0, 0]
        self.offset_step = 5
        self.offset_start =[0, -50]
        self.scroll = 0
        self.scroll_step = self.data['button_size']

    def get_menu(self, menu_data):
        menu = {}
        columns, rows = 1, len(menu_data) - 1 - (1 if 'Back' in menu_data else 0)
        column, row = 0, 0
        max_scroll = 0
        for count, (element_name, element_data) in enumerate(menu_data.items()):
            if element_data == 'title':
                if element_name == 'Choose Level':
                    columns, rows = 3, ceil(rows / 3)
                if rows > self.max_rows:
                    max_scroll = (rows - self.max_rows) * self.data['button_size']
                position = (self.menu_centre[0], int(self.menu_centre[1] - self.data['title_size'] // 1.25))
            elif element_name == 'Back':
                position = (self.menu_centre[0], self.menu_centre[1] + self.data['button_size'] * rows)
            else:
                position = (self.menu_centre[0] + self.column_positions[columns][column], self.menu_centre[1] + self.data['button_size'] * row)
                column += 1
                if column == columns:
                    column = 0
                    row += 1
            menu[element_name] = MenuElement(main=self.main, menu_name=self.menu_name, name=element_name, position=position, element_data=element_data, data=self.data)
        return menu, max_scroll

    def start_up(self):
        self.offset = self.offset_start.copy()
        self.scroll = 0
        if self.scrollbar:
            self.scrollbar.start_up()

    def scroll_up(self):
        self.scroll = max(0, self.scroll - self.scroll_step)

    def scroll_down(self):
        self.scroll = min(self.max_scroll, self.scroll + self.scroll_step)

    def update(self, mouse_position):
        if self.scrollbar:
            response = self.scrollbar.update(scroll=self.scroll, offset=self.offset, mouse_position=mouse_position)
            if response == 'up':
                self.scroll_up()
            elif response == 'down':
                self.scroll_down()
        if self.offset[1] < 0:
            self.offset[1] += self.offset_step
        elif self.max_scroll:
            if self.main.events.check_key(key='mouse_4'):
                self.scroll_up()
            elif self.main.events.check_key(key='mouse_5'):
                self.scroll_down()
        for _, element in self.menu.items():
            selected_element = element.update(offset=self.offset, scroll=self.scroll)
            if selected_element and not self.main.transition.transitioning:
                self.main.audio.play_sound(name='click')  # need to make this more specific to each button type...
                if selected_element[0] == 'game_state':
                    if self.main.game_state == 'main_menu' and selected_element[1] == 'quit':
                        self.main.audio.quit()
                        self.main.transition.start(response=['game_state', 'quit'], queue=(True, 'fade', (0, 0), 1))
                    elif self.main.game_state == 'main_menu' and selected_element[1] == 'game':
                        if selected_element[2] == 'Yes':
                            self.main.assets.reset_game_data()
                        self.main.menu_states['game_paused'].menu['Quit'].button_type = 'game_state'
                        self.main.menu_states['game_paused'].menu['Quit'].button_response = 'main_menu'
                        self.main.transition.start(style='circle', centre=element.centre, response=['game_state', 'game'], queue=(True, 'circle', 'player', 1))
                    elif self.main.game_state == 'main_menu' and selected_element[1] == 'level_editor':
                        self.main.menu_states['choose_level'].menu['Back'].button_type = 'game_state'
                        self.main.menu_states['choose_level'].menu['Back'].button_response = 'main_menu'
                        self.main.change_game_state(game_state='level_editor')
                    elif self.main.game_state == 'game' and selected_element[1] == 'main_menu':
                        self.main.shaders.apply_shader = False
                        self.main.transition.start(response=['game_state', 'main_menu'], queue=(True, 'fade', (0, 0), 1))
                    elif self.main.game_state == 'game' and selected_element[1] == 'level_editor':
                        self.main.transition.start(response=['game_state', 'level_editor'], queue=(True, 'fade', (0, 0), 1))
                    else:
                        self.main.change_game_state(game_state=selected_element[1])
                elif selected_element[0] == 'menu_state':
                    if selected_element[1] == 'options':
                        if self.main.game_state == 'main_menu':
                            self.main.menu_states['options'].menu['Back'].button_type = 'menu_state'
                            self.main.menu_states['options'].menu['Back'].button_response = 'title_screen'
                        elif self.main.game_state == 'game':
                            self.main.menu_states['options'].menu['Back'].button_type = 'menu_state'
                            self.main.menu_states['options'].menu['Back'].button_response = 'game_paused'
                    self.main.change_menu_state(menu_state=selected_element[1])
                elif selected_element[0] == 'option':
                    self.main.assets.change_setting(group=self.menu_name, name=selected_element[2].lower().replace(' ', '_'), option=selected_element[1][0].lower().replace(' ', '_'))
                elif selected_element[0] == 'level':
                    if self.main.game_state == 'game' and selected_element[2] == 'Restart Level':
                        self.main.game_states['game'].map.show_map = False
                        self.main.transition.start(style='circle', centre=element.centre, response=['level', self.main.game_states['game'].level.name, 'original', None, None], queue=(True, 'circle', 'player', 1))
                    elif self.main.game_state == 'level_editor':
                        print(1)
                        self.main.transition.start(response=['level', selected_element[1], 'level', None, None], queue=(True, 'fade', (0, 0), 1))

    def draw(self, displays):
        pass
        if self.scrollbar:
            self.scrollbar.draw(displays=displays, scroll=self.scroll, offset=self.offset)
        for _, element in self.menu.items():
            element.draw(offset=self.offset)

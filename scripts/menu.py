from scripts.menu_element import MenuElement
from scripts.menu_scrollbar import MenuScrollbar
from math import ceil


class Menu:
    def __init__(self, main, menu_name, menu_data):
        self.main = main
        self.menu_name = menu_name
        self.data = {'title_font': 'Mleitod', 'title_size': 48, 'button_font': 'Alagard', 'button_size': 24}
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
        for element_name, element_data in menu_data.items():
            if element_data == 'title':
                if element_name == 'Choose Level':
                    columns, rows = 3, ceil(rows / 3)
                if rows > self.max_rows:
                    max_scroll = (rows - self.max_rows) * self.data['button_size']
                position = (self.menu_centre[0], int(self.menu_centre[1] - self.data['title_size'] // 1.25))
            elif element_name == 'Back':
                position = (self.menu_centre[0], self.menu_centre[1] + self.data['button_size'] * rows)
            else:
                if self.menu_name == 'title_screen' and element_name == 'New Game' and not self.main.assets.data['game']['level']:
                    continue
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
        if self.scroll > 0:
            self.main.audio.play_sound(name='menu_scroll', existing=None)
            self.scroll = max(0, self.scroll - self.scroll_step)

    def scroll_down(self):
        if self.scroll < self.max_scroll:
            self.main.audio.play_sound(name='menu_scroll', existing=None)
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
            if selected_element and not self.main.transition.active:
                self.main.audio.play_sound(name='menu_select')
                if selected_element[0] == 'game_state':
                    if self.main.game_state in ['main_menu', 'game'] and selected_element[1] == 'quit':
                        self.main.audio.quit()
                        self.main.transition.start_transition(response=['game_state', 'quit'], queue=(True, 'fade', (0, 0), 1))
                    elif self.main.game_state == 'main_menu' and selected_element[1] == 'game':
                        if not self.main.assets.data['game']['level'] or element.name == 'Yes':
                            self.main.assets.reset_game_data()
                            self.main.game_states['game'].cutscene.start_cutscene(cutscene_type='level', cutscene_data={'level_name': '(0, 0)', 'force': True})
                        self.main.menu_states['game_paused'].menu['Main Menu'].button_type = 'game_state'
                        self.main.menu_states['game_paused'].menu['Main Menu'].button_response = 'main_menu'
                        self.main.transition.start_transition(style='circle', style_data=element.centre, response=['game_state', 'game'], queue=(True, 'circle', 'player', 1))
                    elif self.main.game_state == 'main_menu' and selected_element[1] == 'level_editor':
                        self.main.menu_states['choose_level'].menu['Back'].button_type = 'game_state'
                        self.main.menu_states['choose_level'].menu['Back'].button_response = 'main_menu'
                        self.main.change_game_state(game_state='level_editor')
                    elif self.main.game_state == 'game' and selected_element[1] == 'main_menu':
                        self.main.transition.start_transition(response=['game_state', 'main_menu'], queue=(True, 'fade', (0, 0), 1))
                    elif self.main.game_state == 'game' and selected_element[1] == 'level_editor':
                        self.main.transition.start_transition(response=['game_state', 'level_editor'], queue=(True, 'fade', (0, 0), 1))
                    else:
                        self.main.change_game_state(game_state=selected_element[1])
                elif selected_element[0] == 'menu_state':
                    if selected_element[2] == 'Options':
                        self.main.menu_states['options'].menu['Back'].button_response = 'title_screen' if self.main.game_state == 'main_menu' else 'game_paused'
                    elif selected_element[2] == 'Quit Game':
                        self.main.menu_states['quit_game'].menu['No'].button_response = 'title_screen' if self.main.game_state == 'main_menu' else 'game_paused'
                    elif selected_element[2] == 'Back':
                        self.main.assets.save_settings()
                    if selected_element[1] == 'developer' and not self.main.debug:
                        self.main.text_handler.activate_text(text_group='main', text_id='debug_required', duration=2)
                    else:
                        self.main.change_menu_state(menu_state=selected_element[1])
                elif selected_element[0] == 'button':
                    if self.main.menu_state == 'developer' and not self.main.debug:
                        self.main.text_handler.activate_text(text_group='main', text_id='debug_required', duration=2)
                    else:
                        self.main.text_handler.deactivate_text_group(text_group='main')
                        self.main.text_handler.activate_text(text_group='main', text_id=selected_element[1], duration=2)
                        if selected_element[1] == 'backup_data':
                            self.main.utilities.backup_file(file_name='data')
                        elif selected_element[1] == 'backup_settings':
                            self.main.utilities.backup_file(file_name='settings')
                        elif selected_element[1] == 'clear_game_data':
                            self.main.assets.reset_game_data(clear=True)
                            self.main.update_menu(menu='title_screen')
                            self.main.change_game_state(game_state='main_menu')
                        elif selected_element[1] == 'restore_data':
                            self.main.utilities.restore_file(file_name='data')
                        elif selected_element[1] == 'restore_settings':
                            self.main.utilities.restore_file(file_name='settings')
                        elif selected_element[1] == 'resave_levels':
                            self.main.utilities.resave_levels()
                elif selected_element[0] == 'option':
                    response = self.main.assets.change_setting(group=self.menu_name, name=element.name, option=selected_element[1][0])
                    while response:
                        element.cycle_option(selected=selected_element[2])
                        response = self.main.assets.change_setting(group=self.menu_name, name=element.name, option=selected_element[1][0])
                elif selected_element[0] == 'level':
                    if self.main.game_state == 'game' and element.name == 'Restart Level':
                        self.main.transition.start_transition(style='circle', style_data=element.centre, response=['level', self.main.game_states['game'].level.name, 'original', None, None],
                                                              queue=(True, 'circle', 'player', 1))
                    elif self.main.game_state == 'level_editor':
                        self.main.transition.start_transition(response=['level', selected_element[1], 'level', None, None], queue=(True, 'fade', (0, 0), 1))

    def draw(self, displays):
        if self.scrollbar:
            self.scrollbar.draw(displays=displays, scroll=self.scroll, offset=self.offset)
        for _, element in self.menu.items():
            element.draw(displays=displays, offset=self.offset)



class Splash:
    def __init__(self, main):
        self.main = main
        self.timer = 0
        self.timers = {'timer': 0, 'text_id': None, 160: 'tcgame', 330: 'hoolio', 500: 'end'}

    def start_up(self, previous_game_state=None):
        self.main.audio.play_music(music_theme='edgy demo')
        self.main.change_menu_state()


    def update(self, mouse_position):
        self.timers['timer'] += 1
        if not self.main.transition.active:
            self.main.display.set_cursor(cursor='arrow')
            if self.timers['timer'] in self.timers:
                self.timers['text_id'] = self.timers[self.timers['timer']]
                if self.timers['text_id'] and self.timers['text_id'] != 'end':
                    self.main.audio.play_sound(name='splash')
            if self.main.events.check_key(key=['mouse_1', 'space']):
                self.timers['text_id'] = 'end'
            if self.timers['text_id'] == 'end':
                self.main.change_game_state(game_state='main_menu')

    def draw(self, displays):
        if self.timers['text_id']:
            self.main.text_handler.activate_text(text_group='splash', text_id=self.timers['text_id'])

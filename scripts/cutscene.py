

class Cutscene:
    def __init__(self, main):
        self.main = main
        self.active_cutscene = False
        self.timer = 0
        self.cutscene_data = {'part_one': {'type': 'level', 'triggered': self.main.assets.data['game']['part_one'], 'trigger': '(0, 0)', 'length': 9, 'position': (301, 61)},
                              'part_two': {'type': 'level', 'triggered': self.main.assets.data['game']['part_two'], 'trigger': '(-1, -5)', 'length': 9, 'position': (157, 205)},
                              'collectable': {'type': 'collectable', 'triggered': False, 'trigger': 'collectable', 'length': 3, 'position': None}}

    def reset(self):
        self.cutscene_data['part_one']['triggered'] = self.main.assets.data['game']['part_one']
        self.cutscene_data['part_two']['triggered'] = self.main.assets.data['game']['part_two']

    def start(self, collectable_type, position):
        if collectable_type in self.main.assets.data['game']['collectables']:
            cutscene_data = self.cutscene_data['collectable']
            self.active_cutscene = 'collectable'
            self.timer = cutscene_data['length'] * self.main.fps
            cutscene_data['position'] = position
            self.main.text_handler.activate_text(text_group='collectables', text_id=collectable_type, duration=3)

    def update(self, level):
        if self.active_cutscene:
            self.timer -= 1
            if self.timer == 0:
                if self.active_cutscene == 'collectable':
                    self.main.shaders.apply_effect(display_layer=['level', 'player'], effect=None)
                self.active_cutscene = None
            if self.active_cutscene == 'part_one':
                if self.timer == 420:
                    return 'open_map'
                elif self.timer == 300:
                    return 'show_collectables_one'
                elif self.timer == 1:
                    return 'close_map'
            elif self.active_cutscene == 'part_two':
                if self.timer == 240:
                    return 'open_map'
                elif self.timer == 120:
                    return 'show_collectables_two'
                elif self.timer == 1:
                    return 'close_map'
            elif self.active_cutscene == 'collectable':
                self.main.shaders.apply_effect(display_layer=['level', 'player'], effect='shockwave', effect_data={'x': self.cutscene_data['collectable']['position'][0],
                                                                                                                   'y': self.cutscene_data['collectable']['position'][1], 'length': 2})
        else:
            for name, data in self.cutscene_data.items():
                if data['type'] == 'level' and not data['triggered']:
                    if level.name == data['trigger']:
                        self.active_cutscene = name
                        self.timer = data['length'] * self.main.fps
                        data['triggered'] = True
                    if self.active_cutscene == 'part_one':
                        return 'map_target_one'
                    elif self.active_cutscene == 'part_two':
                        return 'map_target_two'

    def draw(self, displays):
        if self.active_cutscene in ['part_one', 'part_two']:  # can add interesting sprite/ particles around player
            displays['level'].blit(source=self.main.assets.images['toolbar']['marker'], dest=self.cutscene_data[self.active_cutscene]['position'])
        elif self.active_cutscene == 'collectable': # collectable spirals around player while shrinking
            pass

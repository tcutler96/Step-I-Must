from copy import deepcopy
import pygame.freetype
import pygame as pg
import json
import os


class Assets:
    def __init__(self, main):
        self.main = main
        self.assets_path = self.main.assets_path
        self.audio = self.load_audio()
        self.fonts = self.load_fonts()
        self.images = None
        self.levels = self.load_levels()
        self.shaders = self.load_shaders()
        self.data = self.load_data()
        self.settings = self.load_settings()
        self.update_menu(menu='choose_level')
        self.music_themes = {'splash': None, 'game': 'game', 'level_editor': 'main_menu', 'main_menu': 'main_menu', 'quit': None}
        self.colours = {'whiteish': (230, 230, 230),
                        'blackish': (25, 25, 25),
                        'white': (255, 255, 255),
                        'black': (0, 0, 0),
                        'r': (255, 0, 0),
                        'g': (0, 255, 0),
                        'b': (0, 0, 255),
                        'cream': (246, 242, 195),
                        'purple': (49, 41, 62),
                        'light_purple': (195, 199, 246),
                        'dark_purple': (22, 13, 19),
                        'green': (77, 102, 96),
                        'light_green': (142, 184, 158),
                        'bright_green': (127, 255, 127)}
        self.settings_changed = False
        self.option_to_setting = {'video': {'background': {'game_of_life': 'gol'}, 'button_prompt': {}, 'hrt_shader': {}, 'particles': {},
                                            'resolution': {'(448,_320)': 1, '(896,_640)': 2, '(1344,_960)': 3, '(1792,_1280)': 4}, 'screen_shake': {}, 'shaders': {}},
                                 'audio': {'master_volume': {'disabled': 0, '10%': 0.1, '20%': 0.2, '30%': 0.3, '40%': 0.4, '50%': 0.5, '60%': 0.6, '70%': 0.7, '80%': 0.8, '90%': 0.9, '100%': 1},
                                           'music_volume': {'disabled': 0, '10%': 0.1, '20%': 0.2, '30%': 0.3, '40%': 0.4, '50%': 0.5, '60%': 0.6, '70%': 0.7, '80%': 0.8, '90%': 0.9, '100%': 1},
                                           'sound_volume': {'disabled': 0, '10%': 0.1, '20%': 0.2, '30%': 0.3, '40%': 0.4, '50%': 0.5, '60%': 0.6, '70%': 0.7, '80%': 0.8, '90%': 0.9, '100%': 1}},
                                 'gameplay': {'cutscene_speed': {'slow': 0, 'fast': 1}, 'hold_to_move': {'disabled': -1, 'slow': 15, 'fast': 5},
                                              'hold_to_undo': {'disabled': -1, 'slow': 15, 'fast': 5}, 'movement_speed': {'slow': 0.125, 'fast': 0.25}}}

    def post_load(self):
        self.images = self.load_images()

    def list_directory(self, path):
        for f in os.listdir(path):
            if not f.startswith('.'):
                yield f

    def load_audio(self):
        path = os.path.join(self.assets_path, 'audio')
        audio = {}
        for folder in self.list_directory(path=path):
            if folder in ['music', 'sound']:
                folder_path = os.path.join(path, folder)
                folder_audio = {}
                for file in self.list_directory(path=folder_path):
                    folder_audio[file.split('.')[0]] = os.path.join(folder_path, file) if folder == 'music' else pg.mixer.Sound(file=os.path.join(folder_path, file))
                audio[folder] = folder_audio
        return audio

    def load_fonts(self):
        path = os.path.join(self.assets_path, 'fonts')
        fonts = {}
        for file in self.list_directory(path=path):
            if file.endswith('.ttf'):
                fonts[file.split('.')[0]] = pg.freetype.Font(file=os.path.join(path, file), size=0)
        return fonts

    def load_images(self):
        path = os.path.join(self.assets_path, 'images')
        images = {}
        for folder in self.list_directory(path=path):
            folder_path = os.path.join(path, folder)
            if os.path.isdir(folder_path):
                if folder in ['cursor', 'map', 'other', 'scrollbar', 'toolbar']:
                    folder_images = {}
                    for image in self.list_directory(path=folder_path):
                        folder_images[image.split('.')[0]] = self.main.utilities.load_image(path=os.path.join(folder_path, image))
                    images[folder] = folder_images
                elif folder == 'sprites':
                    sprites = {}
                    sprites_data = {}
                    for sprite_type in self.list_directory(path=folder_path):
                        sprite_type_path = os.path.join(folder_path, sprite_type)
                        for sprite_folder_name in self.list_directory(path=sprite_type_path):
                            sprite_name = sprite_folder_name.split('_')[-1]
                            sprite_name_path = os.path.join(sprite_type_path, sprite_folder_name)
                            if os.path.isdir(sprite_name_path):
                                sprite = {}
                                frame_data = {}
                                for sprite_file in self.list_directory(path=sprite_name_path):
                                    frames = []
                                    sprite_info = sprite_file[:-4].split(' - ')
                                    sprite_sheet = self.main.utilities.load_image(path=os.path.join(sprite_name_path, sprite_file))
                                    sprite_size = sprite_sheet.get_height()
                                    num_frames = sprite_sheet.get_width() // sprite_size
                                    if len(sprite_info) > 1:
                                        frames_counts = [int(frame_count) for frame_count in sprite_info[1].split(', ')]
                                        if len(frames_counts) != num_frames:
                                            frames_counts = frames_counts + [frames_counts[-1]] * (num_frames - len(frames_counts))
                                    else:
                                        frames_counts = None
                                    for frame in range(num_frames):
                                        frames.append(sprite_sheet.subsurface(pg.Rect((frame * sprite_size, 0), (sprite_size, sprite_size))))
                                    sprite_info = sprite_info[0].split('_')[-1]
                                    sprite[sprite_info] = frames
                                    frame_data[sprite_info] = {'frame_counts': frames_counts, 'num_frames': num_frames, 'frame_count': 0, 'frame_index': 0, 'loops': 0}
                                sprites[sprite_name] = sprite
                                sprites_data[sprite_name] = {'frame_data': frame_data, 'state_list': list(sprite), 'num_states': len(list(sprite)), 'sprite_type': sprite_type[:-1]}
                    images['sprites'] = sprites
                    images['sprites_data'] = sprites_data
                    images['sprite_list'] = list(sprites_data)
        return images

    def load_levels(self):
        path = os.path.join(self.assets_path, 'levels')
        levels = {}
        for file in self.list_directory(path=path):
            if file.endswith('.json'):
                with open(os.path.join(path, file), 'r') as file_data:
                    levels[file.split('.')[0]] = json.load(file_data)
        return levels

    def load_shaders(self):
        path = os.path.join(self.assets_path, 'shaders')
        shaders = {}
        for file in self.list_directory(path=path):
            if file.endswith('.glsl'):
                with open(os.path.join(path, file), 'r') as file_data:
                    shaders[file.split('.')[0]] = file_data.read()
        return shaders

    def load_data(self):
        path = os.path.join(self.assets_path, 'data.json')
        with open(path, 'r') as file_data:
            data = json.load(file_data)
        return data

    def load_settings(self):
        path = os.path.join(self.assets_path, 'settings.json')
        with open(path, 'r') as file_data:
            settings = json.load(file_data)
        return settings

    def change_setting(self, group, name, option):
        name = name.lower().replace(' ', '_')
        option = option.lower().replace(' ', '_')
        self.settings_changed = True
        if name in self.option_to_setting[group] and option in self.option_to_setting[group][name]:
            option = self.option_to_setting[group][name][option]
        elif option == 'enabled':
            option = True
        elif option == 'disabled':
            option = False
        self.settings[group][name] = option
        if group == 'video':
            if name == 'background':
                self.main.shaders.background_effect = option
            elif name == 'button_prompt':
                # self.main.game_states['game'].show_button_prompt = option
                pass
            elif name == 'cursor_type':
                self.main.display.cursor.cursor_type = option
            elif name == 'hrt_shader':
                # self.main.shaders.hrt_shader = option
                pass
            elif name == 'particles':  # reference main/ particle handler...
                pass
            elif name == 'resolution':
                return self.main.display.change_resolution(scale_factor=option)
            elif name == 'screen_shake':  # reference game class
                pass
            elif name == 'shaders':
                self.main.shaders.apply_shaders = option
        elif group == 'audio':
            self.main.audio.change_volume(audio_type=name)
        elif group == 'gameplay':
            if name == 'cutscene_speed':
                self.main.game_states['game'].cutscene.bars_speed = self.main.game_states['game'].cutscene.bars_max_offset / (((1 - option) * 1 + option * 0.5) * self.main.fps)
                self.main.game_states['game'].cutscene.text_speed = (1 - option) * 0.5 + option * 1
                self.main.game_states['game'].cutscene.line_pause = (1 - option) * 1 + option * 0.25
            elif name == 'hold_to_move':
                self.main.game_states['game'].move_delay = option
            elif name == 'hold_to_undo':
                self.main.game_states['game'].level.undo_redo_delay = option
                self.main.game_states['level_editor'].level.undo_redo_delay = option
            elif name == 'movement_speed':
                self.main.game_states['game'].movement_speed = option

    def save_data(self):
        with open(os.path.join(self.assets_path, 'data.json'), 'w') as file:
            json.dump(obj=self.data, fp=file, indent=2)

    def save_settings(self):
        if self.settings_changed:
            self.settings_changed = False
            settings = deepcopy(self.settings)
            del settings['menus']['choose_level']
            with open(os.path.join(self.assets_path, 'settings.json'), 'w') as file:
                json.dump(obj=settings, fp=file, indent=2)

    def reset_game_data(self, clear=False):
        self.data['game'] = {'level': '(0, 0)' if not clear else None, 'respawn': [[[12, 2]], [[12, 2]], [False]],
                             'collectables': {'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'cheeses': []}, 'discovered_levels': ['(0, 0)'], 'active_portals': []}
        self.save_data()

    def update_menu(self, menu=None):
        if menu == 'choose_level':
            self.settings['menus']['choose_level'] = {'Choose Level': 'title', 'empty': None, 'filled': None, 'saved': None}
            for level in list(self.levels.keys()):
                self.settings['menus']['choose_level'][level] = ['button', 'level', level]
            if not self.settings['menus']['choose_level']['saved']:
                del self.settings['menus']['choose_level']['saved']
            self.settings['menus']['choose_level']['Back'] = ['button', 'game_state', 'main_menu']

    def reset_sprite(self, name):
        for state, frame_data in self.main.assets.images['sprites_data'][name]['frame_data'].items():
            if state.endswith(' animated'):
                frame_data['frame_count'] = 0
                frame_data['frame_index'] = 0
                frame_data['loops'] = 0

    def update(self):
        for sprite_name, sprite_data in self.images['sprites_data'].items():
            for sprite_state, state_data in self.images['sprites_data'][sprite_name]['frame_data'].items():
                if sprite_state not in ['states', 'num_states', 'sprite_type']:
                    if state_data['num_frames'] > 1:
                        state_data['frame_count'] += 1
                        if state_data['frame_count'] >= state_data['frame_counts'][state_data['frame_index']]:
                            state_data['frame_count'] = 0
                            state_data['frame_index'] += 1
                            if state_data['frame_index'] >= state_data['num_frames']:
                                state_data['frame_index'] = 0
                                state_data['loops'] += 1

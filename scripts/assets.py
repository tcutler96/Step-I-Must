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
        self.option_to_setting = {'game': {'movement_speed': {'slow': 0.125, 'fast': 0.25}, 'hold_to_move': {'disabled': -1, 'slow': 15, 'fast': 5},
                                           'hold_to_undo': {'disabled': -1, 'slow': 15, 'fast': 5}, 'cutscene_speed': {'slow': 0, 'fast': 1}},
                                  'video': {'resolution': {'(448,_320)': 1, '(896,_640)': 2, '(1344,_960)': 3, '(1792,_1280)': 4}},
                                  'shaders': {'background': {'game_of_life': 'gol'}},
                                  'audio': {'master_volume': {'disabled': 0, '10%': 0.1, '20%': 0.2, '30%': 0.3, '40%': 0.4, '50%': 0.5, '60%': 0.6, '70%': 0.7, '80%': 0.8, '90%': 0.9, '100%': 1},
                                            'music_volume': {'disabled': 0, '10%': 0.1, '20%': 0.2, '30%': 0.3, '40%': 0.4, '50%': 0.5, '60%': 0.6, '70%': 0.7, '80%': 0.8, '90%': 0.9, '100%': 1},
                                            'sound_volume': {'disabled': 0, '10%': 0.1, '20%': 0.2, '30%': 0.3, '40%': 0.4, '50%': 0.5, '60%': 0.6, '70%': 0.7, '80%': 0.8, '90%': 0.9, '100%': 1}}}

    def post_load(self):
        self.images = self.load_images()

    def list_directory(self, path, folders=True, extensions='all'):
        directory = []
        if extensions is None:
            extensions = []
        elif extensions != 'all' and not isinstance(extensions, list):
            extensions = [extensions]
        for f in os.listdir(path):
            if not f.startswith('.'):
                p = os.path.join(path, f)
                if os.path.isdir(p):
                    if folders:
                        directory.append(f)
                else:
                    if extensions == 'all' or f.split('.')[-1] in extensions:
                        directory.append(f)
        return directory

    def load_audio(self):
        path = os.path.join(self.assets_path, 'audio')
        audio = {}
        for folder in self.list_directory(path=path, extensions=None):
            if folder in ['music', 'sound']:
                folder_path = os.path.join(path, folder)
                folder_audio = {}
                for file in self.list_directory(path=folder_path, folders=False, extensions=['wav', 'mp3']):
                    if folder == 'music':
                        music = pg.mixer.Sound(file=os.path.join(folder_path, file))
                        folder_audio[file.split('.')[0]] = {'path': os.path.join(folder_path, file), 'length': int(music.get_length() * 1000)}
                        del music
                    elif folder == 'sound':
                        folder_audio[file.split('.')[0]] = pg.mixer.Sound(file=os.path.join(folder_path, file))
                audio[folder] = folder_audio
        return audio

    def load_fonts(self):
        path = os.path.join(self.assets_path, 'fonts')
        fonts = {}
        for file in self.list_directory(path=path, folders=False, extensions='ttf'):
            fonts[file.split('.')[0]] = pg.freetype.Font(file=os.path.join(path, file), size=0)
        return fonts

    def load_image_data(self, folder_path, image_path, sprite):
        image_sheet = self.main.utilities.load_image(path=os.path.join(folder_path, image_path))
        image_info = image_path.split('.')[0].split(' _ ')[-1].split(' -- ')
        if sprite:
            image_size = (image_sheet.get_height(), image_sheet.get_height())
            num_frames = image_sheet.get_width() // image_size[1]
        elif len(image_info) > 1:
            num_frames = int(image_info[1])
            image_size = (image_sheet.get_width() // num_frames, image_sheet.get_height())
        else:
            image_size = None
            num_frames = 1
        image_info = image_info[0].split(' - ')
        if len(image_info) > 1:
            frame_counts = image_info[1]
        else:
            frame_counts = None
        image_name = image_info[0]
        if num_frames > 1:
            frames = []
            if frame_counts:
                frames_counts = [int(frame_count) for frame_count in frame_counts.split(', ')]
                if len(frames_counts) != num_frames:
                    frames_counts = frames_counts + [frames_counts[-1]] * (num_frames - len(frames_counts))
            else:
                frames_counts = [60] * num_frames
            for frame_num in range(num_frames):
                frames.append(image_sheet.subsurface(pg.Rect((frame_num * image_size[0], 0), image_size)))
            image_data = {'frames': frames, 'frame_counts': frames_counts, 'num_frames': num_frames, 'frame_count': 0, 'frame_index': 0, 'loops': 0}
        else:
            image_data = {'frames': [image_sheet]}
        return image_name, image_data

    def load_images(self):
        path = os.path.join(self.assets_path, 'images')
        images = {}
        for folder in self.list_directory(path=path, extensions=None):
            folder_path = os.path.join(path, folder)
            if folder == 'sprites':
                for sprite_type in self.list_directory(path=folder_path, extensions=None):
                    sprite_type_path = os.path.join(folder_path, sprite_type)
                    for sprite_name in self.list_directory(path=sprite_type_path, extensions=None):
                        sprite_name_path = os.path.join(sprite_type_path, sprite_name)
                        sprite_name = sprite_name.split(' _ ')[1]
                        folder_images = {}
                        for sprite_file in self.list_directory(path=sprite_name_path, folders=False, extensions=['png', 'jpg']):
                            image_name, image_data = self.load_image_data(folder_path=sprite_name_path, image_path=sprite_file, sprite=True)
                            folder_images[image_name] = image_data
                        images[sprite_name] = folder_images
            else:
                folder_images = {}
                for image in self.list_directory(path=folder_path, folders=False, extensions=['png', 'jpg']):
                    image_name, image_data = self.load_image_data(folder_path=folder_path, image_path=image, sprite=False)
                    folder_images[image_name] = image_data
                images[folder] = folder_images
        return images

    def load_levels(self):
        path = os.path.join(self.assets_path, 'levels')
        levels = {}
        for file in self.list_directory(path=path, folders=False, extensions='json'):
            with open(os.path.join(path, file), 'r') as file_data:
                levels[file.split('.')[0]] = json.load(file_data)
        return levels

    def load_shaders(self):
        path = os.path.join(self.assets_path, 'shaders')
        shaders = {}
        for file in self.list_directory(path=path, folders=False, extensions='glsl'):
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
        self.save_data()  # game (level, respawn, collectables, discovered_levels, active_portals)

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
        if group == 'game':
            if name == 'movement_speed':
                self.main.game_states['game'].movement_speed = option
            elif name == 'hold_to_move':
                self.main.game_states['game'].move_delay = option
            elif name == 'hold_to_undo':
                self.main.game_states['game'].level.undo_redo_delay = option
                self.main.game_states['level_editor'].level.undo_redo_delay = option
            elif name == 'cutscene_speed':
                self.main.game_states['game'].cutscene.bars_speed = self.main.game_states['game'].cutscene.bars_max_offset / (((1 - option) * 1 + option * 0.5) * self.main.fps)
                self.main.game_states['game'].cutscene.text_speed = (1 - option) * 0.5 + option * 1
                self.main.game_states['game'].cutscene.line_pause = (1 - option) * 1 + option * 0.25
            elif name == 'map_colour':
                self.main.game_states['game'].map.map_colour = option
        elif group == 'video':
            if name == 'resolution':
                return self.main.display.change_resolution(scale_factor=option)
            elif name == 'cursor_type':
                self.main.display.cursor.cursor_type = option
            elif name == 'particles':  # reference particle handler once added...
                pass
        elif group == 'shaders':
            self.main.audio.change_volume(audio_type=name)
            if name == 'all':
                self.main.shaders.apply_shaders = option
            elif name == 'background':
                self.main.shaders.background = option
            elif name == 'chromatic_ui':
                self.main.shaders.chromatic_ui = option
            elif name == 'crt':
                self.main.shaders.crt = option
            elif name == 'vignette':
                self.main.shaders.vignette = option
        elif group == 'audio':
            self.main.audio.change_volume(audio_type=name)

    def trigger_button(self, button):
        if button == 'reset_game_data':
            self.main.assets.reset_game_data(clear=True)
            self.main.update_menu(menu='title_screen')
            self.main.change_game_state(game_state='main_menu')
        elif button == 'update_levels':
            self.main.utilities.update_levels()
        elif button == 'resave_levels':
            self.main.utilities.resave_levels()
        elif button == 'backup_data':
            self.main.utilities.backup_file(file_name='data')
        elif button == 'backup_settings':
            self.main.utilities.backup_file(file_name='settings')
        elif button == 'restore_data':
            self.main.utilities.restore_file(file_name='data')
        elif button == 'restore_settings':
            self.main.utilities.restore_file(file_name='settings')

    def update_menu(self, menu=None):
        if menu == 'choose_level':
            self.settings['menus']['choose_level'] = {'Choose Level': 'title', 'empty': None, 'filled': None, 'saved': None}
            for level in list(self.levels.keys()):
                self.settings['menus']['choose_level'][level] = ['button', 'level', level]
            if not self.settings['menus']['choose_level']['saved']:
                del self.settings['menus']['choose_level']['saved']
            self.settings['menus']['choose_level']['Back'] = ['button', 'game_state', 'main_menu']

    def reset_sprite(self, name):
        # update this for new image dict
        for state, frame_data in self.main.assets.images['sprites_data'][name]['frame_data'].items():
            if state.endswith('_animated'):
                frame_data['frame_count'] = 0
                frame_data['frame_index'] = 0
                frame_data['loops'] = 0

    def update(self):
        for group_data in self.images.values():
            for image_data in group_data.values():
                if 'frame_counts' in image_data:
                    image_data['frame_count'] += 1
                    if image_data['frame_count'] >= image_data['frame_counts'][image_data['frame_index']]:
                        image_data['frame_count'] = 0
                        image_data['frame_index'] += 1
                        if image_data['frame_index'] >= image_data['num_frames']:
                            image_data['frame_index'] = 0
                            image_data['loops'] += 1

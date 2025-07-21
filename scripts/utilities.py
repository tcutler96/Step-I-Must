from copy import deepcopy
import pygame.freetype
import pygame as pg
import json
import os


class Utilities:
    def __init__(self, main):
        self.main = main
        self.assets_path = self.main.assets_path
        self.neighbour_offsets = [(-1, 0), (0, -1), (1, 0), (0, 1)]
        self.neighbour_auto_tile_map = {tuple(sorted([])): 'single', tuple(sorted([(0, -1)])): 'bottom end', tuple(sorted([(1, 0)])): 'left end', tuple(sorted([(0, 1)])): 'top end',
                                        tuple(sorted([(-1, 0)])): 'right end', tuple(sorted([(-1, 0), (1, 0)])): 'left right', tuple(sorted([(0, -1), (0, 1)])): 'top bottom',
                                        tuple(sorted([(1, 0), (0, 1)])): 'top left', tuple(sorted([(-1, 0), (1, 0), (0, 1)])): 'top', tuple(sorted([(-1, 0), (0, 1)])): 'top right',
                                        tuple(sorted([(0, -1), (0, 1), (-1, 0)])): 'right', tuple(sorted([(0, -1), (-1, 0)])): 'bottom right', tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 'bottom',
                                        tuple(sorted([(0, -1), (1, 0)])): 'bottom left', tuple(sorted([(0, -1), (1, 0), (0, 1)])): 'left', tuple(sorted([(-1, 0), (0, -1), (1, 0), (0, 1)])): 'centre'}
        self.corner_offsets = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        self.corner_auto_tile_map = {(-1, -1): 'tl', (1, -1): 'tr', (1, 1): 'br', (-1, 1): 'bl'}

    def s_to_ms(self, s):
        return int(s * 1000)

    def position_str_to_tuple(self, position):
        return tuple([int(number) for number in position.replace('(', '').replace(')', '').split(', ')])

    def level_and_position(self, level, position):
        return level + ' - ' + str(tuple(position))

    def get_opposite_movement(self, movement):
        return movement[0] * -1, movement[1] * -1

    def check_collectable(self, collectable_type, count=True):
        if collectable_type == 'all':
            collectable_type = list(self.main.assets.data['game']['collectables'])
        elif not isinstance(collectable_type, list):
            collectable_type = [collectable_type]
        collectable_count = 0
        for collectable in collectable_type:
            collectables = self.main.assets.data['game']['collectables'][collectable if collectable.endswith('s') else collectable + 's']
            if collectables:
                if count:
                    collectable_count += len(collectables)
                else:
                    return True
        return collectable_count

    def load_image(self, path):
        if path.endswith('.png') or path.endswith('jpg'):
            image = pg.image.load(path).convert()
            image.set_colorkey((0, 0, 0))
            return image

    def load_images(self, path):
        images = []
        for image_name in sorted(os.listdir(path=path)):
            images.append(self.load_image(path=path + '/' + image_name))
        return images

    def get_sprite(self, name, state=None, animated=True):
        if name in ['no object', 'no tile']:
            return self.main.assets.images['toolbar']['empty']
        if not state:
            state = name
        if name in self.main.assets.images['sprite_list'] and state in self.main.assets.images['sprites_data'][name]['state_list']:
            return self.main.assets.images['sprites'][name][state][self.main.assets.images['sprites_data'][name]['frame_data'][state]['frame_index'] if animated else 0].copy()

    def get_colour(self, colour, alpha=0):
        if colour in self.main.assets.colours:
            colour = self.main.assets.colours[colour]
        else:
            colour = self.main.assets.colours['white']
        if alpha:
            colour = (*colour, alpha)
        return colour

    def convert_colours(self, colours):
        converted_colours = []
        if not isinstance(colours, list):
            colours = list(colours)
        for colour in colours:
            if isinstance(colour, str):
                converted_colours.append(self.main.utilities.get_colour(colour=colour))
            else:
                converted_colours.append(colour)
        return converted_colours

    def convert_position(self, position):
        if isinstance(position, str):
            if position == 'top_left':
                position = (8, 16)
            elif position == 'top':
                position = (self.main.display.half_width, 16)
            elif position == 'top_right':
                position = (self.main.display.width - 8, 16)
            elif position == 'left':
                position = (8, self.main.display.half_height)
            elif position == 'centre':
                position = self.main.display.centre
            elif position == 'right':
                position = (self.main.display.width - 8, self.main.display.half_height)
            elif position == 'bottom_left':
                position = (8, self.main.display.height - 16)
            elif position == 'bottom':
                position = (self.main.display.half_width, self.main.display.height - 16)
            elif position == 'bottom_right':
                position = (self.main.display.width - 8, self.main.display.height - 16)
            else:
                position = (0, 0)
        return position

    def align_position(self, size, position, alignment):
        if alignment:
            if alignment[0] == 'c':
                position = (position[0] - size[0] // 2, position[1])
            elif alignment[0] == 'r':
                position = (position[0] - size[0], position[1])
            if alignment[1] == 'c':
                position = (position[0], position[1] - size[1] // 2)
            elif alignment[1] == 'b':
                position = (position[0], position[1] - size[1])
        return position

    def draw_text(self, text, surface=None, position=(0, 0), alignment=('c', 'c'), colour='light_green', bg_colour=None, shadow_colour='dark_purple', shadow_offset=(4, 2),
                  outline_colour='dark_purple', outline_size=1, size=16, max_width=0, max_height=0, font='Alagard', style=None):
        if outline_size > 0:
            outline_offsets = [[x - outline_size, y - outline_size] for x in range(outline_size * 2 + 1) for y in range(outline_size * 2 + 1)]
        else:
            outline_offsets = None
        position = self.convert_position(position=position)
        colour, bg_colour, shadow_colour, outline_colour = self.convert_colours(colours=[colour, bg_colour, shadow_colour, outline_colour])
        if font not in self.main.assets.fonts:
            self.main.assets.fonts[font] = pg.freetype.SysFont(name=font, size=0, bold=False, italic=False)
        font_object = self.main.assets.fonts[font]
        font_object.underline = False
        font_object.oblique = False
        font_object.strong = False
        font_object.antialiased = True
        if style:
            if not isinstance(style, list):
                style = [style]
            if 'underline' in style:
                font_object.underline = True
            if 'itallic' in style:
                font_object.oblique = True
            if 'bold' in style:
                font_object.strong = True
            if 'antia' in style:
                font_object.antialiased = False
        if max_width:
            while font_object.get_rect(text=text, size=size).width > max_width:
                size -= 1
        if max_height:
            while font_object.get_rect(text=text, size=size).height > max_height:
                size -= 1
        _, _, width, height = font_object.get_rect(text=text, size=size)
        position = self.align_position(size=(width, height), position=position, alignment=alignment)
        if surface:
            if shadow_colour and shadow_offset != (0, 0):
                font_object.render_to(surf=surface, dest=(position[0] + shadow_offset[0], position[1] + shadow_offset[1]), text=text, fgcolor=shadow_colour, bgcolor=bg_colour, size=size)
            if outline_size:
                for offset in outline_offsets:
                    font_object.render_to(surf=surface, dest=(position[0] + offset[0], position[1] + offset[1]), text=text, fgcolor=outline_colour, size=size)
            font_object.render_to(surf=surface, dest=position, text=text, fgcolor=colour, bgcolor=bg_colour if not shadow_colour else None, size=size)
            return pg.Rect(*position, width, height)
        else:
            if outline_size:
                surface = pg.Surface(size=(width + outline_size * 2, height + outline_size * 2), flags=pg.SRCALPHA)
                position = (outline_size, outline_size)
                for offset in outline_offsets:
                    font_object.render_to(surf=surface, dest=(position[0] + offset[0], position[1] + offset[1]), text=text, fgcolor=outline_colour, size=size)
                font_object.render_to(surf=surface, dest=position, text=text, fgcolor=colour, size=size)
            else:
                surface = font_object.render(text=text, fgcolor=colour, bgcolor=bg_colour if not shadow_colour else None, size=size)[0]
            if shadow_colour and shadow_offset != (0, 0):
                return surface, font_object.render(text=text, fgcolor=shadow_colour, size=size)[0]
            else:
                return surface

    def add_menu(self, name, title=None, buttons=None):
        # do we really need this?
        # name: menu name reference by other menus, title: string/ sprite, buttons: [{'name': 'Example', 'type': ['menu_state', 'game_state', 'level', 'option'], 'response': 'example'}]
        # make sure to manually update option_to_setting dict in assets class and game_state_text_groups in text_handler class
        menu_data = {}
        if title:
            menu_data[title] = 'title'
        if buttons:
            for button in buttons:
                if button['type'] in ['menu_state', 'game_state', 'level', 'option']:
                    menu_data[button['name']] = ['button', button['type'], button['response']]
        self.main.assets.settings['menus'][name] = menu_data
        self.main.assets.settings_changed = True
        self.main.assets.save_settings()

    def backup_file(self, file_name=None):  # call from develop options menu
        if file_name in ['data', 'settings']:
            if file_name == 'data':
                file_data = self.main.assets.data
            elif file_name == 'settings':
                file_data = deepcopy(self.main.assets.settings)
                del file_data['menus']['choose_level']
            with open(os.path.join(self.assets_path, f'{file_name}_backup.json'), 'w') as file:
                json.dump(obj=file_data, fp=file, indent=2)

    def restore_file(self, file_name=None):  # call from developer options menu, add additional check before doing (ie are you sure?)
        if file_name in ['data', 'settings']:
            path = os.path.join(self.assets_path, f'{file_name}_backup.json')
            with open(path, 'r') as file_data:
                with open(os.path.join(self.assets_path, f'{file_name}.json'), 'w') as file:
                    json.dump(obj=json.load(file_data), fp=file, indent=2)

    def update_levels(self):
        wall_state_updates = {'up down': 'top bottom', 'up end': 'top end', 'down end': 'bottom end'}
        for level_name, level_data in self.main.assets.levels.items():
            for cell in level_data['tilemap'].values():
                if cell['tile'] and cell['tile']['name'] == 'wall' and cell['tile']['state'] in wall_state_updates:
                    cell['tile']['state'] = wall_state_updates[cell['tile']['state']]
            collectables = level_data['collectables'] | {'cheeses': []}
            level_data['collectables'] = collectables
            with open(os.path.join('assets/levels', f'{level_name}.json'), 'w') as file_data:
                json.dump(obj=level_data, fp=file_data, indent=2)

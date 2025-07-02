from scripts.map_cell import MapCell


class Map:
    def __init__(self, main):
        self.main = main
        self.show_map = False
        self.show_text = True
        self.show_collectables = True
        self.cell_size = 16
        part_one_offset = (304.0, 128.0)
        part_two_offset = (240.0, 400.0)
        target = self.get_target(level=self.main.assets.data['game']['level'])
        self.offset_dict = {'1': part_one_offset, '2': part_two_offset, 'current': part_one_offset if target == '1' else part_two_offset, 'target': target,
                            'step': (abs(part_one_offset[0] - part_two_offset[0]) / (2 * self.cell_size), abs(part_one_offset[1] - part_two_offset[1]) / (2 * self.cell_size))}
        self.collectables = {'position': (384, 50), 'types': list(self.main.assets.data['game']['collectables'])}
        self.icons = {'alpha': {'alpha': 255, 'alpha_alt': 0, 'step': -4.25, 'timer': 120, 'delay': 120}, 'alpha_default': {'alpha': 255, 'alpha_alt': 0, 'step': -4.25, 'timer': 120, 'delay': 120},
                      'icons': {'player': {'name': 'player', 'state': 'idle', 'sprite': None}, 'teleporter': {'name': 'teleporter', 'state': 'reciever', 'sprite': None},
                                'silver keys': {'name': 'collectable', 'state': 'silver key', 'sprite': None}, 'silver gems': {'name': 'collectable', 'state': 'silver gem', 'sprite': None},
                                'gold keys': {'name': 'collectable', 'state': 'gold key', 'sprite': None}, 'gold gems': {'name': 'collectable', 'state': 'gold gem', 'sprite': None},
                                'cheeses': {'name': 'collectable', 'state': 'cheese', 'sprite': None}}}
        self.levels = self.load_levels()
        self.map = self.load_map()
        # apply gentle blur shader to game layer when map is open...
        # have map icons fade in and out...
        # reduce each level down to a 16x16 map tile representing it (ie green dot for a wall, empty/ dark purple dot for free space)

    def load_levels(self):
        levels = {}
        for level_name, level_data in self.main.assets.levels.items():
            if level_name.startswith('(') and level_name.endswith(')'):
                levels[level_name] = level_data
        return levels

    def load_map(self):
        map_cells = {}
        for level_name, level_data in self.levels.items():
            level_position = self.main.utilities.position_str_to_tuple(position=level_name)
            blit_position = (level_position[0] * self.cell_size, (level_position[1] - (4 if level_position[1] < -3 else 0)) * self.cell_size)
            if level_name in self.main.assets.data['map'] and self.main.assets.data['map'][level_name] in self.main.assets.images['map']:
                sprite = self.main.assets.images['map'][self.main.assets.data['map'][level_name]]
            else:
                neighbours = set()
                for neighbour in self.main.utilities.neighbour_offsets:
                    neighbour_position = str((level_position[0] + neighbour[0], level_position[1] + neighbour[1]))
                    if neighbour_position in self.levels:
                        neighbours.add(neighbour)
                variant = self.main.utilities.neighbour_auto_tile_map[tuple(sorted(neighbours))]
                self.main.assets.data['map'][level_name] = variant
                sprite = self.main.assets.images['map'][variant]
                print(f'{level_name} map data updated ({variant})...')
            teleporter = False
            for reciever in self.main.assets.data['teleporters']['recievers']:
                if level_name in reciever:
                    teleporter = True
            map_cells[level_name] = MapCell(main=self.main, level_name=level_name, sprite=sprite, blit_position=blit_position,
                                            cell_size=self.cell_size, offset=self.offset_dict['current'], discovered=level_name in self.main.assets.data['game']['discovered_levels'],
                                            player=level_name == self.main.assets.data['game']['level'], teleporter=teleporter,
                                            collectables={'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'cheeses': []})
        return map_cells

    def reset_map(self):
        self.show_map = False
        self.icons['alpha'] = self.icons['alpha_default'].copy()
        self.update_icons()
        for level_name, map_cell in self.map.items():
            map_cell.discovered = level_name in self.main.assets.data['game']['discovered_levels']
            map_cell.player = level_name == self.main.assets.data['game']['level']
        for level_name, level_data in self.levels.items():
            for collectable_type in self.collectables['types']:
                collectable = []
                if level_data['collectables'][collectable_type]:
                    for position in level_data['collectables'][collectable_type]:
                        if self.main.utilities.level_and_position(level=level_name, position=position) not in self.main.assets.data['game']['collectables'][collectable_type]:
                            collectable.append(tuple(position))
                self.map[level_name].collectables[collectable_type] = collectable

    def get_target(self, level):
        return '1' if self.main.utilities.position_str_to_tuple(position=level)[1] > -4 else '2'

    def set_target(self, target):
        if self.offset_dict['current'] != self.offset_dict[target]:
            self.offset_dict['target'] = target
            self.offset_dict['current'] = self.offset_dict[self.offset_dict['target']]
            for map_cell in self.map.values():
                map_cell.update_rect(self.offset_dict['current'])

    def transition_level(self, old_level, new_level):
        self.map[old_level].player = False
        self.map[new_level].player = True
        if not self.map[new_level].discovered:
            self.map[new_level].discovered = True
            self.main.assets.data['game']['discovered_levels'].append(new_level)

    def update_player(self, level_name):
        for map_cell in self.map.values():
            map_cell.player = False
            if map_cell.level_name == level_name:
                map_cell.player = True

    def update_collectables(self, collectable_type, level_name, position):
        if collectable_type in self.collectables['types']:
            if level_name != 'custom' and position in self.map[level_name].collectables[collectable_type]:
                self.map[level_name].collectables[collectable_type].remove(position)

    def update_icons(self):
        if self.icons['alpha']['timer']:
            self.icons['alpha']['timer'] -= 1
        else:
            self.icons['alpha']['alpha'] += self.icons['alpha']['step']
            self.icons['alpha']['alpha_alt'] -= self.icons['alpha']['step']
            if self.icons['alpha']['alpha'] == 0 or self.icons['alpha']['alpha'] == 255:
                self.icons['alpha']['step'] *= -1
                self.icons['alpha']['timer'] = self.icons['alpha']['delay']
        for icon in self.icons['icons'].values():
            sprite = self.main.utilities.get_sprite(name=icon['name'], state=icon['state'])
            sprite.set_alpha(self.icons['alpha']['alpha'] if icon['name'] in ['player', 'teleporter'] else self.icons['alpha']['alpha_alt'])
            icon['sprite'] = sprite

    def update(self, mouse_position, active_cutscene):
        if not active_cutscene and (self.main.text_handler.text_elements['map']['toggle'].selected or self.main.events.check_key(key='tab')):
            self.show_map = not self.show_map
            if not self.show_map:  # map turned off
                # set map cell alpha step to negative value...
                self.set_target(target=self.offset_dict['target'])
            else:  # map turned on
                # set map cell alpha step to positive value...
                self.icons['alpha'] = self.icons['alpha_default'].copy()
        if not active_cutscene and self.show_map and (self.main.text_handler.text_elements['map']['switch'].selected or self.main.events.check_key(key='space')):
            self.offset_dict['target'] = '1' if self.offset_dict['target'] == '2' else '2'
            mouse_position = None
        interpolating = False
        if self.offset_dict['current'] != self.offset_dict[self.offset_dict['target']]:
            if self.show_map:
                interpolating = True
                step = (self.offset_dict['step'][0] * (1 if self.offset_dict['current'][0] < self.offset_dict[self.offset_dict['target']][0] else -1),
                        self.offset_dict['step'][1] * (1 if self.offset_dict['current'][1] < self.offset_dict[self.offset_dict['target']][1] else -1))
                self.offset_dict['current'] = (self.offset_dict['current'][0] + step[0], self.offset_dict['current'][1] + step[1])
            else:
                self.offset_dict['current'] = self.offset_dict[self.offset_dict['target']]
        if self.show_map:
            self.main.shaders.apply_effect(dispay_layer='level', effect='pixel')
            self.update_icons()
            selected_level = None
            for level_name, map_cell in self.map.items():
                if map_cell.update(mouse_position=mouse_position, offset=self.offset_dict['current'], interpolating=interpolating):
                    selected_level = level_name
            if selected_level:
                self.set_target(target=self.get_target(level=selected_level))
                return selected_level

    def draw_collectables(self, displays):
        if self.show_collectables:
            self.main.text_handler.activate_text(text_group='map', text_id='collectables')
            for x, (collectable_type, collectable_count) in enumerate(self.main.assets.data['game']['collectables'].items()):
                collectable_count = len(collectable_count)
                for y in range(collectable_count):
                    sprite = self.main.utilities.get_sprite(name='collectable', state=collectable_type[:-1])
                    displays['map'].blit(source=sprite, dest=(self.collectables['position'][0] + x * self.main.sprite_size, self.collectables['position'][1] + y * self.main.sprite_size // 4))
                if collectable_count:
                    self.main.utilities.draw_text(text=str(collectable_count), surface=displays['map'], alignment=('c', 't'), shadow_offset=(2, 2), outline_size=0, size=14, max_width=self.main.sprite_size * 0.8,
                                                  position=(self.collectables['position'][0] + (x + 0.5) * self.main.sprite_size, self.collectables['position'][1] + (collectable_count + 3.5) * self.main.sprite_size // 4))

    def draw(self, displays):
        if self.show_map:
            for map_cell in self.map.values():
                map_cell.draw(displays=displays, icons=self.icons['icons'], offset=self.offset_dict['current'])
            self.draw_collectables(displays=displays)
            if self.show_text:
                self.main.text_handler.activate_text(text_group='map', text_id='toggle')
                if self.main.assets.data['game']['part_two']:
                    self.main.text_handler.activate_text(text_group='map', text_id='switch')

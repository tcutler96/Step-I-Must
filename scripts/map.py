from scripts.map_cell import MapCell


class Map:
    def __init__(self, main):
        self.main = main
        self.show_map = False
        self.show_text = True
        self.cell_size = self.main.sprite_size
        part_one_offset = (304.0, 128.0)
        part_two_offset = (240.0, 400.0)
        self.offset_dict = {1: part_one_offset, 2: part_two_offset, 'current': None, 'target': 1,
                            'step': (abs(part_one_offset[0] - part_two_offset[0]) / (2 * self.cell_size), abs(part_one_offset[1] - part_two_offset[1]) / (2 * self.cell_size))}
        self.collectables = {'base_position': (384, 50), 'y_overlap': 0.35, 'types': list(self.main.assets.data['game']['collectables']),
                             'max_counts': {collectable_type: 0 for collectable_type in list(self.main.assets.data['game']['collectables'])},
                             'sprites': {'fraction': self.main.assets.images['map']['fraction'].copy(), 'fraction_filled': self.main.assets.images['map']['fraction_filled'].copy(), 'medal': self.main.assets.images['map']['medal'].copy()} |
                                        {collectable_type[:-1]: None for collectable_type in list(self.main.assets.data['game']['collectables'])} |
                                        {f'{collectable_type[:-1]} empty': None for collectable_type in list(self.main.assets.data['game']['collectables'])}}
        self.part_data = {'part_one': {'collectable_types': ['silver keys', 'silver gems'], 'text': 'World 1: ', 'position': (424, 252)},
                          'part_two': {'collectable_types': ['gold keys', 'gold gems', 'cheeses'], 'text': 'World 2: ', 'position': (424, 266)},
                          'overall': {'collectable_types': ['silver keys', 'silver gems', 'gold keys', 'gold gems', 'cheeses'], 'text': 'Overall: ', 'position': (424, 280)}}
        self.alpha = 0
        self.alpha_step = 8.5
        self.icons = {'alpha': {'alpha': 255, 'alpha_alt': 0, 'step': -4.25, 'timer': 120, 'delay': 120}, 'alpha_default': {'alpha': 255, 'alpha_alt': 0, 'step': -4.25, 'timer': 120, 'delay': 120},
                      'icons': {'player': {'name': 'player', 'state': 'idle', 'sprite': None}, 'teleporter': {'name': 'teleporter', 'state': 'reciever', 'sprite': None},
                                'silver keys': {'name': 'collectable', 'state': 'silver key', 'sprite': None}, 'silver gems': {'name': 'collectable', 'state': 'silver gem', 'sprite': None},
                                'gold keys': {'name': 'collectable', 'state': 'gold key', 'sprite': None}, 'gold gems': {'name': 'collectable', 'state': 'gold gem', 'sprite': None},
                                'cheeses': {'name': 'collectable', 'state': 'cheese', 'sprite': None}}}
        self.levels = self.load_levels()
        self.map = self.load_map()

    def get_collectable_position(self, x, y):
        return self.collectables['base_position'][0] + x * self.main.sprite_size, self.collectables['base_position'][1] + y * self.main.sprite_size * self.collectables['y_overlap']

    def load_levels(self):
        levels = {}
        for level_name, level_data in self.main.assets.levels.items():
            if level_name.startswith('(') and level_name.endswith(')'):
                for collectable, amount in level_data['collectables'].items():
                    if amount:
                        self.collectables['max_counts'][collectable] += len(amount)
                levels[level_name] = level_data
        for x, collectable_type in enumerate(self.collectables['types']):
            self.update_collectable_count_text(collectable_type=collectable_type)
        return levels

    def load_map(self):
        map_cells = {}
        data_updated = False
        for level_name, level_data in self.levels.items():
            level_position = self.main.utilities.position_str_to_tuple(position=level_name)
            blit_position = ((level_position[0] - (3 if level_position == (4, 4) else 0)) * self.cell_size, (level_position[1] - (4 if level_position[1] < -3 else -1 if level_position == (4, 4) else 0)) * self.cell_size)
            if level_name in self.main.assets.data['map'] and self.main.assets.data['map'][level_name] in self.main.assets.images['map']:
                sprite = self.main.assets.images['map'][self.main.assets.data['map'][level_name]].copy()
            else:
                neighbours = set()
                for neighbour in self.main.utilities.neighbour_offsets:
                    neighbour_position = str((level_position[0] + neighbour[0], level_position[1] + neighbour[1]))
                    if neighbour_position in self.levels:
                        neighbours.add(neighbour)
                variant = self.main.utilities.neighbour_auto_tile_map[tuple(sorted(neighbours))]
                self.main.assets.data['map'][level_name] = variant
                data_updated = True
                sprite = self.main.assets.images['map'][variant].copy()
                print(f'{level_name} map data updated to {variant}...')
            teleporter = False
            for reciever in self.main.assets.data['teleporters']['recievers']:
                if level_name in reciever:
                    teleporter = True
            map_cells[level_name] = MapCell(main=self.main, level_name=level_name, sprite=sprite, blit_position=blit_position,
                                            cell_size=self.cell_size, discovered=level_name in self.main.assets.data['game']['discovered_levels'],
                                            player=level_name == self.main.assets.data['game']['level'], teleporter=teleporter,
                                            collectables={'silver keys': [], 'silver gems': [], 'gold keys': [], 'gold gems': [], 'cheeses': []})
        if data_updated:
            self.main.assets.save_data()
        return map_cells

    def reset_map(self):
        self.show_map = False
        self.icons['alpha'] = self.icons['alpha_default'].copy()
        self.update_icons()
        self.update_part_percents()
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
        return 1 if self.main.utilities.position_str_to_tuple(position=level)[1] > -4 else 2

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

    def update_collectable_count_text(self, collectable_type):
        count = len(self.main.assets.data['game']['collectables'][collectable_type])
        max_count = self.collectables['max_counts'][collectable_type]
        self.main.text_handler.add_text(text_group='map', text_id=f'{collectable_type}_current', text=str(count), alignment=('c', 'c'), bounce=0, shadow_offset=(4, 4),
                                        size=14, max_width=self.main.sprite_size * 0.75, display_layer='map', alpha_step=8.5, colour='purple' if count < max_count else 'light_green',
                                        position=self.get_collectable_position(x=self.collectables['types'].index(collectable_type) + 0.5, y=max_count + 3))
        self.main.text_handler.add_text(text_group='map', text_id=f'{collectable_type}_max', text=str(max_count), alignment=('c', 'c'), size=14, bounce=0, shadow_offset=(4, 4),
                                        max_width=self.main.sprite_size * 0.75, display_layer='map', alpha_step=8.5, colour='purple' if count < max_count else 'light_green',
                                        position=self.get_collectable_position(x=self.collectables['types'].index(collectable_type) + 0.5, y=max_count + (6.3 if count < max_count else 6.1)))

    def update_part_percents(self):
        max_counts = self.collectables['max_counts']
        for part in self.part_data:
            max_count = 0
            for collectable_type in self.part_data[part]['collectable_types']:
                max_count += max_counts[collectable_type]
            count = self.main.utilities.check_collectable(collectable_type=self.part_data[part]['collectable_types'])
            percent = round(100 * count / max_count, 2)
            self.main.assets.data['game'][f'{part}_percent'] = percent
            self.main.text_handler.add_text(text_group='map', text_id=f'{part}_percent', text=f'{self.part_data[part]['text']}{percent:g}%', position=self.part_data[part]['position'],
                                            alpha_step=8.5, alignment=('c', 'c'), size=14, bounce=False, max_width=112, display_layer='map')

    def update_collectables(self, collectable_type, level_name, position):
        if collectable_type in self.collectables['types'] and position in self.map[level_name].collectables[collectable_type]:
            self.map[level_name].collectables[collectable_type].remove(position)
            self.update_collectable_count_text(collectable_type=collectable_type)
            self.update_part_percents()

    def update_interpolation(self):
        interpolating = False
        if self.offset_dict['current'] != self.offset_dict[self.offset_dict['target']]:
            interpolating = True
            step = (self.offset_dict['step'][0] * (1 if self.offset_dict['current'][0] < self.offset_dict[self.offset_dict['target']][0] else -1),
                    self.offset_dict['step'][1] * (1 if self.offset_dict['current'][1] < self.offset_dict[self.offset_dict['target']][1] else -1))
            self.offset_dict['current'] = (self.offset_dict['current'][0] + step[0], self.offset_dict['current'][1] + step[1])
        return interpolating

    def update_icons(self):
        if self.show_map or self.alpha:
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
                sprite.set_alpha(min(self.icons['alpha']['alpha'], self.alpha) if icon['name'] in ['player', 'teleporter'] else min(self.icons['alpha']['alpha_alt'], self.alpha))
                icon['sprite'] = sprite

    def update_sprites(self):
        if self.show_map or self.alpha:
            for name, sprite in self.collectables['sprites'].items():
                if name in ['fraction', 'fraction_filled', 'medal']:
                    sprite.set_alpha(self.alpha)
                else:
                    sprite = self.main.utilities.get_sprite(name='collectable', state=name)
                    sprite.set_alpha(self.alpha)
                    self.collectables['sprites'][name] = sprite

    def update(self, mouse_position, active_cutscene):
        if not active_cutscene and not self.main.menu_state:
            if self.main.text_handler.text_elements['map']['toggle'].selected == 'left' or self.main.events.check_key(key='tab'):
                self.show_map = not self.show_map
                if not self.show_map:
                    self.main.audio.play_sound(name='map_close')
                else:
                    self.main.audio.play_sound(name='map_open')
                    self.alpha = 0
                    self.icons['alpha'] = self.icons['alpha_default'].copy()
                    self.set_target(target=self.get_target(level=self.main.assets.data['game']['level']))
            if self.show_map and (self.main.text_handler.text_elements['map']['switch'].selected == 'left' or self.main.events.check_key(key='space')):
                self.main.audio.play_sound(name='map_switch')
                self.offset_dict['target'] = 1 if self.offset_dict['target'] == 2 else 2
                mouse_position = None
        self.update_icons()
        self.update_sprites()
        if self.show_map:
            interpolating = self.update_interpolation()
            self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player', 'level_ui'], effect='blur', effect_data={'length': 0.5})
            if self.alpha < 255:
                self.alpha = min(self.alpha + self.alpha_step, 255)
            selected_level = [None, None]
            for level_name, map_cell in self.map.items():
                selected = map_cell.update(mouse_position=mouse_position, offset=self.offset_dict['current'], interpolating=interpolating, alpha=self.alpha)
                if selected:
                    selected_level = [level_name, selected]
            if selected_level[0]:
                return selected_level
        else:
            if self.alpha:
                self.alpha = max(self.alpha - self.alpha_step, 0)

    def draw_collectables(self, displays):  # store all collectable positions in dict as they never change...
        if self.show_map and (self.main.assets.data['game']['part_one'] or self.main.debug):
            self.main.text_handler.activate_text(text_group='map', text_id='collectables')
        for x, (collectable_type, collectable_count) in enumerate(self.main.assets.data['game']['collectables'].items()):
            collectable_count = len(collectable_count)
            if collectable_count or self.main.debug:
                max_count = self.collectables['max_counts'][collectable_type]
                for y in list(range(collectable_count, max_count)) + list(range(collectable_count)):
                    collectable_sprite = self.collectables['sprites'][collectable_type[:-1]] if y <= collectable_count - 1 else self.collectables['sprites'][collectable_type[:-1] + ' empty']
                    displays['level_map'].blit(source=collectable_sprite, dest=self.get_collectable_position(x=x, y=y))
                displays['level_map'].blit(source=self.collectables['sprites']['fraction' if collectable_count < max_count else 'fraction_filled'], dest=self.get_collectable_position(x=x, y=max_count + 4.1))
                if self.show_map:
                    self.main.text_handler.activate_text(text_group='map', text_id=f'{collectable_type}_current')
                    self.main.text_handler.activate_text(text_group='map', text_id=f'{collectable_type}_max')
                if collectable_count >= max_count:
                    displays['level_map'].blit(source=self.collectables['sprites']['medal'], dest=self.get_collectable_position(x=x, y=max_count + 8))

    def draw(self, displays):
        if self.alpha:
            for map_cell in self.map.values():
                map_cell.draw(displays=displays, icons=self.icons['icons'], offset=self.offset_dict['current'], alpha=self.alpha)
            self.draw_collectables(displays=displays)
        if self.show_map:
            if self.main.assets.data['game']['part_one'] or self.main.debug:
                if self.show_text or self.main.debug:
                    self.main.text_handler.activate_text(text_group='map', text_id='toggle')
                self.main.text_handler.activate_text(text_group='map', text_id='part_one_percent')
            if self.main.assets.data['game']['part_two'] or self.main.debug:
                if self.show_text or self.main.debug:
                    self.main.text_handler.activate_text(text_group='map', text_id='switch')
                self.main.text_handler.activate_text(text_group='map', text_id='part_two_percent')
                self.main.text_handler.activate_text(text_group='map', text_id='overall_percent')

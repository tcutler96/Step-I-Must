from scripts.tutorial import Tutorial
from scripts.cutscene import Cutscene
from scripts.level import Level
from scripts.map import Map
from copy import deepcopy


class Game:
    def __init__(self, main):
        self.main = main
        self.cutscene = Cutscene(main=self.main)
        self.level = Level(main=self.main)
        self.tutorials = Tutorial(main=self.main)
        self.map = Map(main=self.main)
        self.movement_dict = {'w': 'up', 'a': 'left', 's': 'down', 'd': 'right'}
        self.movement_held = {'up': 0, 'left': 0, 'down': 0, 'right': 0}
        self.movement_directions = {'w': (0, -1), 'a': (-1, 0), 's': (0, 1), 'd': (1, 0), 'up': (0, -1), 'left': (-1, 0), 'down': (0, 1), 'right': (1, 0)}
        self.move_delay = self.main.assets.settings['gameplay']['hold_to_move']
        self.move_timer = 0
        self.hold_move_delay = 30
        self.movement_speed = self.main.assets.settings['gameplay']['movement_speed']
        self.bump_amount = 0.4
        self.last_movement = None
        self.no_movement = False
        self.stored_movement = None
        self.resolve_state = None
        self.check_standing = False
        self.interpolating = False
        self.players_exited = None
        self.player_cells = None
        self.player_afk = 3600
        self.player_afk_timer = 0
        self.no_steps = False
        self.teleporter_data = None
        self.sign_data = None
        self.lock_data = None

    def reset_animations(self, force_reset=False):
        for cell in self.level.get_cells():
            for element in cell.elements.values():
                if element and element['state'].endswith(' animated') and not element['state'].startswith('portal'):
                    if self.main.assets.images['sprites_data'][element['name']]['frame_data'][element['state']]['loops'] or force_reset:
                        element['state'] = element['state'].replace(' animated', '')

    def reset_objects_while(self):
        for cell in self.level.get_cells():
            for object_data in cell.object_data.values():
                if object_data:
                    if not object_data['slid']:
                        object_data['last_slid'] = None
                    object_data['slid'] = False
                    object_data['bumped'] = False

    def reset_objects_end(self):
        for cell in self.level.get_cells():
            for object_data in cell.object_data.values():
                if object_data:
                    if object_data['name'] == 'player' and cell.elements['player']['state'] == 'moving':
                        cell.elements['player']['state'] = 'idle'
                    if not object_data['moved']:
                        object_data['last_moved'] = None
                    object_data['moved'] = False
                    if not object_data['conveyed']:
                        object_data['last_conveyed'] = None
                    object_data['conveyed'] = False
                    if not object_data['split']:
                        object_data['last_split'] = None
                    object_data['split'] = False

    def collect_collectable(self, cell):
        self.main.audio.play_sound(name='collectable', overlap=True)
        # self.main.audio.play_sound(name=f'collectable_{cell.elements['object']['state'].replace(' ', '_')}')
        collectable_type = cell.elements['object']['state'] + 's'
        if self.level.name != 'custom':
            self.main.assets.data['game']['collectables'][collectable_type].append(self.main.utilities.level_and_position(level=self.level.name, position=cell.object_data['object']['original_position']))
            self.map.update_collectables(collectable_type=collectable_type, level_name=self.level.name, position=cell.object_data['object']['original_position'])
            self.cutscene.start_cutscene(cutscene_type='collectable', cutscene_data={'collectable_type': collectable_type,
                                                                                     'collectable_position': (self.level.level_offset[0] + self.level.sprite_size * (cell.position[0] + 0.5),
                                                                                                              self.level.level_offset[1] + self.level.sprite_size * (cell.position[1] + 0.5)),
                                                                                     'end_response': 'map' if len(self.main.assets.data['game']['collectables'][collectable_type]) == 1 else None})
            self.main.assets.save_data()  # game (collectables)
        levels = self.level.cached_levels
        levels.append({'name': self.level.name, 'level': self.level.level})
        for count, level in enumerate(levels):
            if level['name'] == self.level.name:
                for level_cell in level['level'].values():
                    if count == len(self.level.cached_levels) - 1 and level_cell.position == cell.position:
                        pass
                    elif level_cell.check_element(name='collectable', state=collectable_type[:-1]) and level_cell.object_data['object']['original_position'] == cell.object_data['object']['original_position']:
                        level_cell.elements['object'] = None
                        level_cell.object_data['object'] = None
            for lock, lock_data in self.main.assets.data['locks'].items():
                if lock.startswith(level['name']) and collectable_type == lock_data['collectable_type']:
                    if len(self.main.assets.data['game']['collectables'][collectable_type]) >= lock_data['collectable_amount']:
                        level['level'][tuple(lock_data['position'])].elements['tile'] = None
        for lock, lock_data in self.main.assets.data['locks'].items():
            if collectable_type == lock_data['collectable_type']:
                difference = lock_data['collectable_amount'] - len(self.main.assets.data['game']['collectables'][collectable_type])
                if difference > 0:
                    self.main.text_handler.add_text(text_group='locks', text_id=lock, text=f'collect {difference} more {collectable_type[:-1] if difference == 1 else collectable_type}',
                                                    position='top', bounce=-3, display_layer='level_main')
        cell.elements['object'] = None
        cell.object_data['object'] = None
        # we sometimes get stuck in moving animation when we collect something...
        # need to resolve level loop (ie let things change states) still while cutscene is happening or pause all that until after cutscene?

    def resolve_object_conflict(self, revert_cell, revert_object_type, revert_movement, bump_cell, bump_object_type, bump_movement):
        count = self.revert_object(cell=revert_cell, object_type=revert_object_type, movement=revert_movement)
        bump_cell.object_data[bump_object_type]['moved'] = False
        self.bump_object(cell=bump_cell, object_type=bump_object_type, movement=bump_movement)
        return count

    def revert_object(self, cell, object_type, movement, count=1):
        old_cell = self.level.get_new_cell(position=cell.position, movement=movement)
        check_movement = cell.check_movement(object_type=object_type, movement=movement, new_cell=old_cell, push_allowed=False)
        if not check_movement[0]:
            movement = self.main.utilities.get_opposite_movement(movement=old_cell.object_data[check_movement[1]]['last_moved'])
            count = self.revert_object(cell=old_cell, object_type=check_movement[1], movement=movement, count=count + 1)
        old_cell.elements[object_type] = cell.elements[object_type]
        old_cell.object_data[object_type] = cell.object_data[object_type]
        old_cell.object_data[object_type]['blit_position'].pop(-1)
        old_cell.object_data[object_type]['moved'] = False
        if self.resolve_state in ['ice', 'ice_2']:
            old_cell.object_data[object_type]['last_slid'] = None
        elif self.resolve_state == 'conveyors':
            old_cell.object_data[object_type]['last_conveyed'] = None
        cell.elements[object_type] = None
        cell.object_data[object_type] = None
        self.bump_object(cell=old_cell, object_type=object_type, movement=old_cell.object_data[object_type]['last_moved'])
        return count

    def bump_object(self, cell, object_type, movement, bump_amount=None):
        if not bump_amount:
            self.main.audio.play_sound(name='bump')
            bump_amount = self.bump_amount
        if not cell.object_data[object_type]['bumped']:
            movement_speed = self.movement_speed // 0.125
            cell.object_data[object_type]['bumped'] = True
            cell.object_data[object_type]['blit_position'].append((cell.position[0] + movement[0] * bump_amount * movement_speed,
                                                                   cell.position[1] + movement[1] * bump_amount * movement_speed))
            cell.object_data[object_type]['blit_position'].append(cell.position)
            self.interpolating = True

    def get_respawn(self):
        respawn = [[], [], []]
        for cell in self.players_exited:
            movement = cell.object_data['player']['last_moved']
            position = (0 if movement[0] > 0 else self.level.grid_size - 1 if movement[0] < 0 else cell.position[0],
                        0 if movement[1] > 0 else self.level.grid_size - 1 if movement[1] < 0 else cell.position[1])
            respawn[0].append(position)
            respawn[1].append(position)
            respawn[2].append(cell.object_data['player']['facing_right'])
            self.bump_object(cell=cell, object_type='player', movement=movement, bump_amount=3.5)
        return respawn

    def transition_level(self, teleport=None):
        self.resolve_state = None
        self.no_movement = False
        self.movement_held = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        if self.level.name == 'custom':
            new_level = self.level.name
            respawn = self.get_respawn()
            centre = self.level.grid_to_display(position=self.players_exited[0].position, centre=True)
            bump = self.main.utilities.get_opposite_movement(movement=self.players_exited[0].object_data['player']['last_moved'])
        elif teleport:
            new_level = teleport[0]
            respawn = [[tuple(teleport[1])], [tuple(teleport[1])], [True]]
            centre = teleport[2]
            bump = None
        else:
            current_level = self.main.utilities.position_str_to_tuple(position=self.level.name)
            if len(self.players_exited) > 1:
                new_levels = {}
                for cell in self.players_exited:
                    movement = cell.object_data['player']['last_moved']
                    new_level = str((current_level[0] + movement[0], current_level[1] + movement[1]))
                    if new_level not in new_levels:
                        new_levels[new_level] = 1
                    else:
                        new_levels[new_level] += 1
                if len(new_levels) == 1:
                    self.main.audio.play_sound(name='level_transition')
                    new_level = list(new_levels.keys())[0]
                    respawn = self.get_respawn()
                    centre = self.level.grid_to_display(position=self.players_exited[0].position, centre=True)
                    bump = self.main.utilities.get_opposite_movement(movement=self.players_exited[0].object_data['player']['last_moved'])
                else:
                    self.main.audio.play_sound(name='cryprid_teleport')
                    cryptid = ''
                    for new_level in list(new_levels.keys()):
                        if cryptid != '':
                            cryptid += ' - '
                        cryptid += new_level
                    if cryptid in self.main.assets.data['teleporters']['cryptids']:
                        new_level, respawn = self.main.assets.data['teleporters']['cryptids'][cryptid]['destination'].split(' - ')
                        respawn = self.main.utilities.position_str_to_tuple(position=respawn)
                        respawn = [[respawn], [respawn], True]
                    else:
                        new_level = '(4, 4)'
                        respawn = [[(2, 2)], [(2, 2)], [True]]
                    centre = self.main.display.centre
                    bump = None
            else:
                movement = self.players_exited[0].object_data['player']['last_moved']
                new_level = str((current_level[0] + movement[0], current_level[1] + movement[1]))
                respawn = self.get_respawn()
                centre = self.level.grid_to_display(position=self.players_exited[0].position, centre=True)
                bump = self.main.utilities.get_opposite_movement(movement=movement)
        if new_level in self.map.levels or new_level == 'custom':
            if new_level != 'custom':
                self.cutscene.start_cutscene(cutscene_type='level', cutscene_data={'level_name': new_level})
                self.map.transition_level(old_level=self.level.name, new_level=new_level)
                self.main.assets.data['game']['level'] = new_level
                self.main.assets.data['game']['respawn'] = respawn
                self.main.assets.save_data()  # game (level, respawn, discovered_levels)
            self.level.name = new_level
            self.level.orignal_respawn = respawn
            self.main.transition.start_transition(style='circle', centre=centre, response=['level', self.level.name, 'original', bump],
                                                  queue=(True, 'circle', self.level.grid_to_display(position=respawn[0][0], centre=True)))
            if self.main.debug and self.teleporter_data['setting']:
                self.teleporter_data['setting']['new_level'] = new_level
                self.teleporter_data['setting']['new_position'] = respawn[0][0]
        else:
            self.reset_objects_end()
            print(f'level {new_level} not found...')

    def set_steps(self, increment=None, steps=None):
        if increment:
            self.level.steps += increment
        elif isinstance(steps, int):
            self.level.steps = steps
        if self.level.steps not in self.main.text_handler.text_elements['steps']:
            self.main.text_handler.add_text(text_group='steps', text_id=self.level.steps, text=str(self.level.steps), position='top_left', bounce=-3, alignment=('l', 'c'), display_layer='level_main')

    def resolve_standing(self, new_level=False):
        if self.check_standing or new_level or self.main.debug:
            self.check_standing = False
            steps = 0
            respawn = [[], [], []]
            steps_updated = False
            respawn_updated = False
            self.player_cells = {}
            self.no_steps = True
            self.teleporter_data['standing'] = []
            sign_data = self.sign_data
            self.sign_data = []
            self.lock_data = None
            for cell in self.level.get_cells():
                if cell.check_element(name='player'):
                    self.player_cells[cell.position] = cell
                    level_and_position = self.main.utilities.level_and_position(level=self.level.name, position=cell.position)

                    if cell.check_element(name='sign'):  # signs
                        self.main.audio.play_sound(name='scroll_open')
                        sign_position = self.level.name + ' - ' + str(cell.position)
                        if sign_position in self.main.assets.data['signs']:
                            self.sign_data.append(sign_position)

                    if self.main.debug:
                        self.no_steps = False
                        if cell.check_element(name='teleporter'):
                            self.teleporter_data['standing'] = [{'state': cell.elements['tile']['state'].split(' ')[0], 'level_and_position': level_and_position}]
                    else:
                        if cell.check_element(name=['permanent flag', 'temporary flag']):  # flags
                            steps_updated = True
                            steps = max(steps, int(cell.elements['object']['state']))
                            if cell.check_element(name='permanent flag'):
                                self.main.audio.play_sound(name='permanent_flag')
                                respawn_updated = True
                                respawn[0].append(cell.object_data['object']['original_position'])
                                respawn[1].append(cell.position)
                                respawn[2].append(True)
                            else:
                                self.main.audio.play_sound(name='temporary_flag')
                            if cell.check_element(name='player', state='dead') and not cell.check_element(name=['permanent flag', 'temporary flag'], state='0'):
                                cell.elements['player']['state'] = 'idle'

                        if cell.check_element(name='collectable'):  # collectables
                            self.collect_collectable(cell=cell)

                        if not cell.check_element(name='player', state='dead'):  # players
                            self.no_steps = False

                        for direction in cell.adjacent_directions:  # locks
                            new_cell = self.level.get_new_cell(position=cell.position, movement=direction)
                            if new_cell and new_cell.check_element(name='lock'):
                                new_level_and_position = self.main.utilities.level_and_position(level=self.level.name, position=new_cell.position)
                                if new_level_and_position in self.main.text_handler.text_elements['locks']:
                                    self.main.audio.play_sound(name='lock')
                                    self.lock_data = new_level_and_position

                        if level_and_position in self.main.assets.data['teleporters']['activations']:  # activations
                            activation = self.main.assets.data['teleporters']['activations'][level_and_position]
                            # either remove activated flag from activation data or reset it when we start a new game...
                            # if not activation['activated']:
                            if activation['two_players']:
                                two_players = False
                                for direction in cell.adjacent_directions:
                                    new_cell = self.level.get_new_cell(position=cell.position, movement=direction)
                                    if new_cell and new_cell.check_element(name='player', state=['idle', 'moving', 'sleeping']):
                                        two_players = True
                                if not two_players:
                                    break
                            # activation['activated'] = True
                            for portal in activation['portals']:
                                if portal not in self.main.assets.data['game']['active_portals']:
                                    self.main.audio.play_sound(name='portal_activate')
                                    self.main.assets.data['game']['active_portals'].append(portal)
                                    self.main.assets.save_data()  # game (active_portals)
                                    levels = self.level.cached_levels
                                    levels.append({'name': self.level.name, 'level': self.level.level})
                                    for count, level in enumerate(levels):
                                        if portal.startswith(level['name']):
                                            level_cell = level['level'][tuple(self.main.assets.data['teleporters']['portals'][portal]['position'])]
                                            if level_cell.check_element(name='teleporter', state='portal'):
                                                level_cell.elements['tile']['state'] += ' animated'

                        if cell.check_element(name='teleporter', state=['reciever', 'sender', 'portal animated']):  # teleporters
                            self.teleporter_data['standing'].append({'state': cell.elements['tile']['state'].split(' ')[0], 'level_and_position': level_and_position})

            if self.teleporter_data['standing']:
                if len(self.teleporter_data['standing']) == 1:
                    self.teleporter_data['standing'] = self.teleporter_data['standing'][0]
            if sign_data and sign_data != self.sign_data:
                self.main.audio.play_sound(name='scroll_close')
            if steps_updated:
                self.set_steps(steps=steps)
            elif new_level:
                self.set_steps(steps=5)
            if not self.main.debug:
                if not new_level and self.level.steps == 0:
                    self.main.audio.play_sound(name='game_over')
                    self.no_steps = True
                    for cell in self.player_cells.values():
                        cell.elements['player']['state'] = 'dead'
                if respawn_updated:
                    self.level.current_respawn = respawn

    def move_object(self, cell, object_type, movement, push_allowed=True, bump_allowed=True):
        new_cell = self.level.get_new_cell(position=cell.position, movement=movement)
        check_movement = cell.check_movement(object_type=object_type, movement=movement, new_cell=new_cell, push_allowed=push_allowed)
        if check_movement[0] and not self.players_exited:
            if cell.check_element(name='player', state='dead'):
                self.main.audio.play_sound(name='dead_player_pushed')
            if cell.check_element(name='rock'):
                self.main.audio.play_sound(name='rock_pushed')
            if cell.elements[object_type]['name'] == 'permanent flag' and self.level.current_respawn and cell.position in self.level.current_respawn[1]:
                self.level.current_respawn[1][self.level.current_respawn[1].index(cell.position)] = new_cell.position
            new_cell.elements[object_type] = deepcopy(cell.elements[object_type])
            new_cell.object_data[object_type] = deepcopy(cell.object_data[object_type])
            new_cell.object_data[object_type]['moved'] = True
            new_cell.object_data[object_type]['last_moved'] = movement
            new_cell.object_data[object_type]['blit_position'].append((new_cell.position[0], new_cell.position[1]))
            self.interpolating = True
            cell.elements[object_type] = None
            cell.object_data[object_type] = None
            if object_type == 'player' and new_cell.check_element(name='player'):
                if movement[0] > 0:
                    new_cell.object_data[object_type]['facing_right'] = True
                elif movement[0] < 0:
                    new_cell.object_data[object_type]['facing_right'] = False
                if new_cell.elements['player']['state'] in ['idle', 'sleeping']:
                    new_cell.elements['player']['state'] = 'moving'
            return True
        else:
            if object_type == 'player' and check_movement[1] == 'edge':
                cell.object_data['player']['moved'] = True
                cell.object_data['player']['last_moved'] = movement
                self.players_exited.append(cell)
                return True
            elif bump_allowed:
                self.bump_object(cell=cell, object_type=object_type, movement=movement)

    def move_players(self, movement):
        if movement == self.last_movement and self.no_movement:
            return
        if not self.move_timer:
            self.last_movement = movement
            self.no_movement = True
            self.players_exited = []
            player_moved = False
            for cell in self.level.get_cells():
                if cell.check_element(name='player', state=['idle', 'sleeping']) and not cell.object_data['player']['moved']:
                    if self.move_object(cell=cell, object_type='player', movement=movement):
                        player_moved = True
            if self.players_exited:
                self.main.audio.play_sound(name='player_move', overlap=True)
                self.movement_held = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
                self.no_movement = False
                self.transition_level()
            elif player_moved:
                self.main.audio.play_sound(name='player_move', overlap=True)
                self.level.clear_cache_redo()
                self.reset_animations(force_reset=True)
                self.no_movement = False
                self.move_timer = self.move_delay
                if self.main.debug:
                    if self.teleporter_data['setting']:
                        self.teleporter_data['setting']['new_position'] = (self.teleporter_data['setting']['new_position'][0] + movement[0],
                                                                           self.teleporter_data['setting']['new_position'][1] + movement[1])
                    self.resolve_state = 'end'
                else:
                    self.set_steps(increment=-1)
                    self.resolve_state = 'ice'

    def resolve_ice(self):
        self.check_standing = True
        self.resolve_standing()
        objects_slid = 0
        for cell in self.level.get_cells():
            if cell.check_element(name='ice'):
                for object_type, object_data in cell.object_data.items():
                    if object_data and object_data['moved'] and not object_data['slid']:
                        movement = cell.object_data[object_type]['last_moved']
                        opposite_movement = self.main.utilities.get_opposite_movement(movement=movement)
                        new_cell = self.level.get_new_cell(position=cell.position, movement=movement)
                        check_movement = cell.check_movement(object_type=object_type, movement=movement, new_cell=new_cell, push_allowed=False)
                        if new_cell and ((new_cell.object_data['object'] and new_cell.object_data['object']['slid']) or (new_cell.object_data['player'] and new_cell.object_data['player']['slid'])) and not check_movement[0]:
                            for new_object_type, new_object_data in new_cell.object_data.items():
                                if new_object_data and new_object_data['slid']:
                                    objects_slid -= 1
                                    # print(new_cell.object_data, new_object_type)
                                    self.resolve_object_conflict(revert_cell=new_cell, revert_object_type=new_object_type,
                                                                 revert_movement=self.main.utilities.get_opposite_movement(movement=new_cell.object_data[object_type]['last_moved']),
                                                                 bump_cell=cell, bump_object_type=object_type, bump_movement=movement)
                        elif new_cell and ((new_cell.check_element(name='ice')) and not check_movement[0] and new_cell.object_data[check_movement[1]]['moved']
                              and new_cell.object_data[check_movement[1]]['last_moved'] == opposite_movement):
                            pass
                        elif self.move_object(cell=cell, object_type=object_type, movement=movement):
                                if cell not in self.players_exited:
                                    objects_slid += 1
                                    new_cell.object_data[object_type]['slid'] = True
                                    new_cell.object_data[object_type]['last_slid'] = movement
                                    new_new_cell = self.level.get_new_cell(position=new_cell.position, movement=movement)
                                    while (new_cell and new_cell.check_element(name='ice')) and (new_new_cell and (new_new_cell.object_data['object'] or new_new_cell.object_data['player'])):
                                        for new_new_object_data in new_new_cell.object_data.values():
                                            if new_new_object_data and new_new_object_data['last_moved'] == movement:
                                                new_new_object_data['slid'] = True
                                                new_new_object_data['last_slid'] = movement
                                        new_cell = new_new_cell
                                        new_new_cell = self.level.get_new_cell(position=new_new_cell.position, movement=movement)
        if objects_slid:
            self.main.audio.play_sound(name='ice', overlap=True)
        if self.players_exited:
            self.transition_level()
        elif not objects_slid:
            if self.resolve_state == 'ice':
                self.resolve_state = 'conveyors'
                self.resolve_conveyors()
            elif self.resolve_state == 'ice_2':
                self.resolve_state = 'splitters'

    def resolve_conveyors(self):
        self.resolve_standing()
        objects_conveyed = 0
        for cell in self.level.get_cells():
            if cell.check_element(name='conveyor') and ((cell.elements['object'] and not cell.object_data['object']['conveyed']) or
                                                        (cell.elements['player'] and not cell.object_data['player']['conveyed'])):
                conveyors, objects_conveyed, _ = self.convey_cell(cell=cell, objects_conveyed=objects_conveyed)
                for conveyor in conveyors:
                    cell = self.level.level[conveyor]
                    if cell.check_element(name='conveyor'):
                        self.trigger_animation(cell=cell, object_type='tile')
        if objects_conveyed:
            self.main.audio.play_sound(name='conveyor')
        if self.players_exited:
            self.transition_level()
        else:
            if objects_conveyed:
                self.resolve_state = 'ice_2'
            else:
                self.resolve_state = 'splitters'

    def convey_cell(self, cell, objects_conveyed, queue=None, movement=None):
        movement = cell.conveyor_movements[cell.elements['tile']['state'].split(' ')[0]] if cell.check_element(name='conveyor') else movement
        new_cell = self.level.get_new_cell(position=cell.position, movement=movement)
        if queue:
            queue.append(cell.position)
        else:
            queue = [cell.position]
        object_conflict = False
        push_allowed = True
        # print(cell.position, self.players_exited, cell.elements)
        # we enter a convey recursion as the intial flag cannot move onto the new flag
        # this we set push allowed to False when doing our checks
        # this leads to a flag effectively pushing a player which is normally cannot do...
        for object_type, object_data in cell.object_data.items():
            if object_data and not object_data['conveyed']:
                check_movement = cell.check_movement(object_type=object_type, movement=movement, new_cell=new_cell, push_allowed=False)
                # print(object_type, check_movement)
                if check_movement[0] or check_movement[1] == 'edge':
                    cell.object_data[object_type]['conveyed'] = True
                    self.move_object(cell=cell, object_type=object_type, movement=movement, push_allowed=push_allowed)
                    if cell not in self.players_exited and new_cell:
                        objects_conveyed += 1
                        new_cell.object_data[object_type]['last_conveyed'] = movement
                else:
                    for new_object_type, new_object_data in new_cell.object_data.items():
                        if not object_conflict and not check_movement[0] and new_object_data and new_object_data['conveyed']:
                            if new_object_data['last_conveyed']:
                                cell.object_data[object_type]['conveyed'] = True
                                objects_conveyed -= self.resolve_object_conflict(revert_cell=new_cell, revert_object_type=new_object_type,
                                                                     revert_movement=self.main.utilities.get_opposite_movement(movement=new_object_data['last_conveyed']),
                                                                     bump_cell=cell, bump_object_type=object_type, bump_movement=movement)
                                object_conflict = True
                            else:
                                push_allowed = False
                    if not object_conflict:
                        if (new_cell.elements['object'] and not new_cell.object_data['object']['conveyed']) or (new_cell.elements['player'] and not new_cell.object_data['player']['conveyed']):
                            if new_cell.position in queue:
                                push_allowed = False
                            else:
                                queue, objects_conveyed, push_allowed = self.convey_cell(cell=new_cell, objects_conveyed=objects_conveyed, queue=queue, movement=movement)
                        cell.object_data[object_type]['conveyed'] = True
                        if cell.check_element(name='conveyor'):
                            if self.move_object(cell=cell, object_type=object_type, movement=movement, push_allowed=push_allowed):
                                if cell not in self.players_exited:
                                    objects_conveyed += 1
                                    new_cell.object_data[object_type]['last_conveyed'] = movement
                            else:
                                push_allowed = False
        return queue, objects_conveyed, push_allowed

    def resolve_splitters(self):
        for cell in self.level.get_cells():
            if cell.check_element(name='splitter') and ((cell.elements['object'] and not cell.object_data['object']['split']) or
                                                        (cell.elements['player'] and not cell.object_data['player']['split'])):
                splitters = cell.split_cell(level=self.level)
                if splitters:
                    self.main.audio.play_sound(name='splitter')
                    self.check_standing = True
                    for splitter in splitters:
                        self.trigger_animation(cell=self.level.level[splitter], object_type='tile')
        self.resolve_state = 'statues'

    def resolve_statues(self):
        for cell in self.level.get_cells():
            if cell.check_element(name='player', state=['idle', 'moving', 'sleeping']):
                next_position = cell.position
                movement = (1, 0) if cell.object_data['player']['facing_right'] else (-1, 0)
                while True:
                    next_position = (next_position[0] + movement[0], next_position[1] + movement[1])
                    if not self.level.position_on_grid(position=next_position):
                        break
                    next_cell = self.level.level[next_position]
                    if next_cell.check_element(name=['wall', 'player', 'rock']) or cell.check_element(name='barrier', state='vertical') or next_cell.check_element(name='barrier', state='vertical'):
                        break
                    elif next_cell.check_element(name='statue'):
                        self.main.audio.play_sound(name='statue')
                        cell.elements['object'] = {'name': 'rock', 'state': 'rock'}
                        cell.object_data['object'] = cell.object_data['player'] | {'name': 'rock'}
                        self.trigger_animation(cell=cell, object_type='object')
                        cell.elements['player'] = None
                        cell.object_data['player'] = None
                        self.check_standing = True
                        break
        self.resolve_state = 'spikes'

    def resolve_spikes(self):
        for cell in self.level.get_cells():
            if cell.check_element(name='spike') and cell.check_element(name='player', state=['idle', 'moving']):
                if not cell.check_element(name=['permanent flag', 'temporary flag']) or cell.check_element(name=['permanent flag', 'temporary flag'], state='0'):
                    self.main.audio.play_sound(name='spike')
                    cell.elements['player']['state'] = 'dead'
                    self.check_standing = True
        self.resolve_state = 'end'

    def trigger_animation(self, cell, object_type):
        if not cell.elements[object_type]['state'].endswith(' animated'):
            cell.elements[object_type]['state'] += ' animated'
        self.main.assets.reset_sprite(name=cell.elements[object_type]['name'])

    def remove_extra_players(self):
        for cell in self.player_cells.values():
            if not cell.check_element(name='teleporter'):
                cell.elements['player'] = None
                cell.object_data['player'] = None

    def check_teleport_data(self):
        data_updated = False
        not_list = not isinstance(self.teleporter_data['standing'], list)
        if not_list:
            self.teleporter_data['standing'] = [self.teleporter_data['standing']]
        for teleporter_data in self.teleporter_data['standing']:
            state = teleporter_data['state']
            level_and_position = teleporter_data['level_and_position']
            if level_and_position not in self.main.assets.data['teleporters'][state + 's']:
                self.main.assets.data['teleporters'][state + 's'][level_and_position] = {'position': list(self.main.utilities.position_str_to_tuple(position=level_and_position.split(' - ')[1])),
                                                                                         'destination': level_and_position if state == 'reciever' else None}
                data_updated = True
        if not_list:
            self.teleporter_data['standing'] = self.teleporter_data['standing'][0]
        return data_updated

    def update_activations(self, activation):
        empty_activations = []
        portals = self.main.assets.data['teleporters']['activations'][activation]['portals']
        for other_activation, activation_data in self.main.assets.data['teleporters']['activations'].items():
            if other_activation != activation:
                for portal in portals:
                    if portal in activation_data['portals']:
                        activation_data['portals'].remove(portal)
                        if not activation_data['portals']:
                            empty_activations.append(other_activation)
        for empty_activation in empty_activations:
            del self.main.assets.data['teleporters']['activations'][empty_activation]

    def update_teleporters(self):
        if not self.map.show_map:
            data_updated = False
            if self.teleporter_data['setting']:
                level_and_position = self.main.utilities.level_and_position(level=self.teleporter_data['setting']['new_level'], position=self.teleporter_data['setting']['new_position'])
                if not self.main.debug:
                    self.teleporter_data['setting'] = None
                    print('no longer setting warp')
                elif self.main.events.check_key(key='e'):
                    if self.teleporter_data['setting']['stage'] == 'warp destination':
                        self.main.assets.data['teleporters'][self.teleporter_data['setting']['state'] + 's'][self.teleporter_data['setting']['level_and_position']]['destination'] = level_and_position
                        data_updated = True
                        if self.teleporter_data['setting']['state'] == 'portal':
                            if (self.teleporter_data['standing'] and self.teleporter_data['standing']['state'] == 'portal' and
                                    self.teleporter_data['standing']['level_and_position'] != self.teleporter_data['setting']['level_and_position']):
                                self.check_teleport_data()
                                self.teleporter_data['setting']['paired'] = level_and_position
                                self.main.assets.data['teleporters'][self.teleporter_data['setting']['state'] + 's'][level_and_position]['destination'] = self.teleporter_data['setting']['level_and_position']
                                print('warp pair destination set, set warp pair activation...')
                            else:
                                print('warp destination set, set warp activation...')
                            self.teleporter_data['setting']['stage'] = 'warp activation'
                        else:
                            self.teleporter_data['setting'] = None
                            print('warp destination set')
                    elif self.teleporter_data['setting']['stage'] == 'warp activation':
                        activation = level_and_position
                        self.main.assets.data['teleporters']['activations'][activation] = {'position': self.teleporter_data['setting']['new_position'], 'portals': [self.teleporter_data['setting']['level_and_position']],
                                                                                           'two_players': self.main.events.check_key(key='e', modifier='ctrl'), 'activated': False}
                        data_updated = True
                        if 'paired' in self.teleporter_data['setting']:
                            self.main.assets.data['teleporters']['activations'][activation]['portals'].append(self.teleporter_data['setting']['paired'])
                            data_updated = True
                            print('warp pair activation set')
                        else:
                            print('warp activation set')
                        self.update_activations(activation=activation)
                        self.teleporter_data['setting'] = None
                    elif self.teleporter_data['setting']['stage'] == 'cryptid pair':
                        if (self.teleporter_data['standing'] and self.teleporter_data['standing']['state'] == 'portal' and
                                self.teleporter_data['standing']['level_and_position'] != self.teleporter_data['setting']['level_and_position']):
                            data_updated = self.check_teleport_data()
                            self.teleporter_data['setting']['paired'] = level_and_position
                            self.teleporter_data['setting']['stage'] = 'cryptid destination'
                            print('cryptid pair set, set cryptid pair destination...')
                    elif self.teleporter_data['setting']['stage'] == 'cryptid destination':
                        first = self.teleporter_data['setting']['level_and_position']
                        second = self.teleporter_data['setting']['paired']
                        data_updated = True
                        self.teleporter_data['setting'] = None
                        self.main.assets.data['teleporters']['cryptids'][first + ', ' + second] = {'teleporters': [first,  second], 'destination': level_and_position}
                        print('cryptid pair destination set')
            elif self.teleporter_data['standing']:
                if self.main.debug and self.main.events.check_key(key='t'):
                    if self.teleporter_data['standing']['state'] == 'portal' and self.teleporter_data['standing']['level_and_position'] in self.main.assets.data['teleporters']['portals']:
                        teleporter_data = self.main.assets.data['teleporters']['portals'][self.teleporter_data['standing']['level_and_position']]
                        if teleporter_data['destination']:
                            new_level, new_position = teleporter_data['destination'].split(' - ')
                            self.transition_level(teleport=[new_level, self.main.utilities.position_str_to_tuple(position=new_position),
                                                            self.level.grid_to_display(position=teleporter_data['position'], centre=True)])
                        else:
                            print('warp not set')
                    else:
                        print('warp not set')
                if self.main.events.check_key(key='e'):
                    data_updated = self.check_teleport_data()
                    if self.main.debug:
                        self.remove_extra_players()
                        if self.teleporter_data['standing']['state'] == 'reciever':
                            print('warp destination set')
                        else:
                            self.teleporter_data['setting'] = self.teleporter_data['standing'].copy()
                            self.teleporter_data['setting']['new_level'] = self.level.name
                            self.teleporter_data['setting']['new_position'] = tuple(self.main.assets.data['teleporters'][self.teleporter_data['setting']['state'] + 's']
                                                                                    [self.teleporter_data['setting']['level_and_position']]['position'])
                            if self.main.events.check_key(key='e', modifier='ctrl'):
                                self.teleporter_data['setting']['stage'] = 'cryptid pair'
                                print('set cryptid pair...')
                            else:
                                self.teleporter_data['setting']['stage'] = 'warp destination'
                                print('set warp destination...')
                    else:
                        if isinstance(self.teleporter_data['standing'], list):
                            cryptid_warp = False
                            for cryptid in self.main.assets.data['teleporters']['cryptids'].values():
                                if self.teleporter_data['standing'][0]['level_and_position'] in cryptid['teleporters'] and self.teleporter_data['standing'][1]['level_and_position'] in cryptid['teleporters']:
                                    self.main.audio.play_sound(name='cryptid_teleport')
                                    cryptid_warp = True
                                    new_level, new_position = cryptid['destination'].split(' - ')
                                    self.transition_level(teleport=[new_level, self.main.utilities.position_str_to_tuple(position=new_position), self.main.display.centre])
                                    break
                            if not cryptid_warp:
                                print('cryptid warp not set')
                        elif self.teleporter_data['standing']['state'] == 'reciever':
                            self.main.audio.play_sound(name='map_open')
                            self.map.show_map = True
                        else:
                            teleporter_data = self.main.assets.data['teleporters'][self.teleporter_data['standing']['state'] + 's'][self.teleporter_data['standing']['level_and_position']]
                            if teleporter_data['destination']:
                                self.main.audio.play_sound(name='teleport')
                                # unique sound for portal teleport
                                # self.main.audio.play_sound(name='portal_teleport' if self.teleporter_data['standing']['state'] == 'portal' else 'teleport')
                                new_level, new_position = teleporter_data['destination'].split(' - ')
                                self.transition_level(teleport=[new_level, self.main.utilities.position_str_to_tuple(position=new_position),
                                                                self.level.grid_to_display(position=teleporter_data['position'], centre=True)])
                            else:
                                print(f'warp not set')
            if data_updated:
                self.main.assets.save_data()  # teleporters (recievers, senders, portals, activations, cryptids)

    def update_map(self, mouse_position):
        if self.level.name != 'custom':
            selected_level = self.map.update(mouse_position=mouse_position if self.map.show_map else None, active_cutscene=self.cutscene.active)
            if selected_level:
                if selected_level[0] == self.level.name:
                    self.main.audio.play_sound(name='map_close')
                    self.map.show_map = False
                else:
                    self.main.audio.play_sound(name='teleport', overlap=True)
                    self.teleporter_data['standing'] = None
                    position = (7, 7)
                    if not self.main.debug:
                        for reciever in self.main.assets.data['teleporters']['recievers']:
                            if selected_level[0] in reciever:
                                position = tuple(self.main.assets.data['teleporters']['recievers'][reciever]['position'])
                    self.transition_level(teleport=[selected_level[0], position, selected_level[1]])

    def update_cutscene(self):
        if self.cutscene.update():
            self.movement_held = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
            return True
        if self.cutscene.end_trigger:
            self.cutscene.end_trigger = False
            if self.cutscene.end_response == 'map':
                self.main.audio.play_sound(name='map_open')
                self.map.set_target(target=self.map.get_target(level=self.level.name))
                self.map.show_map = True
        # what do we need to return here?
        
        # return self.cutscene.active_cutscene or self.cutscene.active

    def interpolate_blit_position(self, blit_position):
        if blit_position[0][0] < blit_position[1][0]:
            blit_position[0] = (blit_position[0][0] + self.movement_speed, blit_position[0][1])
        elif blit_position[0][0] > blit_position[1][0]:
            blit_position[0] = (blit_position[0][0] - self.movement_speed, blit_position[0][1])
        if abs(blit_position[0][0] - blit_position[1][0]) < self.movement_speed:
            blit_position[0] = (blit_position[1][0], blit_position[0][1])
        if blit_position[0][1] < blit_position[1][1]:
            blit_position[0] = (blit_position[0][0], blit_position[0][1] + self.movement_speed)
        elif blit_position[0][1] > blit_position[1][1]:
            blit_position[0] = (blit_position[0][0], blit_position[0][1] - self.movement_speed)
        if abs(blit_position[0][1] - blit_position[1][1]) < self.movement_speed:
            blit_position[0] = (blit_position[0][0], blit_position[1][1])
        if blit_position[0] == blit_position[1]:
            blit_position.pop(1)
        if len(blit_position) > 1:
            return True

    def update_blit_positions(self):
        self.interpolating = False
        for cell in self.level.get_cells():
            for object_type, object_data in cell.object_data.items():
                if object_data and len(object_data['blit_position']) > 1:
                    if self.interpolate_blit_position(blit_position=object_data['blit_position']):
                        self.interpolating = True

    def update_undo_redo(self):
        self.check_standing = True
        self.resolve_standing()
        self.tutorials.update_level(level_name=self.level.name)
        self.map.update_player(level_name=self.level.name)

    def load_level(self, name='empty', load_respawn=None, bump_player=None):
        self.tutorials.transition_level(level_name=self.level.name)
        self.map.show_map = False
        self.map.alpha = 0
        self.level.load_level(name=name, load_respawn=load_respawn, bump_player=bump_player)

    def reset_level(self):
        self.last_movement = None
        self.no_movement = False
        self.stored_movement = None
        self.resolve_state = None
        self.check_standing = False
        self.interpolating = False
        self.players_exited = None
        self.player_cells = None
        self.player_afk_timer = 0
        self.no_steps = False
        self.teleporter_data = {'standing': None, 'setting': None}
        self.sign_data = None
        self.lock_data = None
        self.map.reset_map()
        self.level.reset_cache()
        for lock, lock_data in self.main.assets.data['locks'].items():
            if lock_data['collectable_type'] and lock_data['collectable_amount']:
                difference = lock_data['collectable_amount'] - len(self.main.assets.data['game']['collectables'][lock_data['collectable_type']])
                if difference > 0:
                    self.main.text_handler.add_text(text_group='locks', text_id=lock, text=f'collect {difference} more {lock_data['collectable_type'][:-1] 
                    if difference == 1 else lock_data['collectable_type']}', position='top', bounce=-3, display_layer='level_main')

    def start_up(self, previous_game_state=None):
        self.main.change_menu_state()
        self.reset_level()
        self.level.name = self.main.assets.data['game']['level'] if previous_game_state == 'main_menu' else 'custom'
        self.tutorials.update_level(level_name=self.level.name)
        self.load_level(name=self.level.name, load_respawn='setting' if previous_game_state == 'main_menu' and self.main.assets.data['game']['respawn'] else 'level')

    def update(self, mouse_position):  # refactor this, draw everything all the time now that we have display layers in game and can see them all while menu is open etc...
        # separate into general updates, player updates (which only happen when we have control of the player), etc...
        self.tutorials.update()  # where should this go?
        if self.main.events.check_key(key='1'):
            self.cutscene.start_cutscene(cutscene_type='level', cutscene_data={'level_name': '(-1, -5)', 'force': True})
        if self.main.events.check_key(key='2'):
            self.cutscene.start_cutscene(cutscene_type='collectable', cutscene_data={'collectable_type': 'cheeses', 'collectable_position': self.main.display.centre, 'end_response': 'map'})

        if self.main.menu_state:  # we need to update all game aspects (tutorial, map etc) even when the menu is open
            self.main.display.set_cursor(cursor='arrow')
            self.update_map(mouse_position=None)
            self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player', 'level_ui', 'level_map'], effect='pixelate', effect_data={'length': 0.5})
        else:
            if self.main.debug or self.map.show_map:
                self.main.display.set_cursor(cursor='arrow')
            else:
                self.main.display.set_cursor(cursor=None)
            if self.interpolating:
                self.update_blit_positions()
            if not self.main.transition.active:
                if self.main.events.check_key(key=['escape', 'p']) and not self.cutscene.active:
                    self.main.audio.play_sound(name='menu_select')
                    self.main.change_menu_state(menu_state='game_paused')
                self.update_map(mouse_position=mouse_position)
                if not self.update_cutscene():
                    if self.player_cells and self.level.steps == 1:
                        self.main.shaders.apply_effect(display_layer=['level_player'], effect='grey')
                    elif self.no_steps or not self.player_cells:  # no more steps or players, game over, you can not do anything except open menu, map, move to reset, and press 'e' to teleport...
                        # self.main.audio.play_sound(name='game_over')
                        self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player'], effect='grey')
                    self.update_teleporters()
                    if not self.map.show_map:
                        if self.level.update():
                            self.update_undo_redo()
                    self.reset_animations()
                    if self.move_timer:
                        self.move_timer -= 1
                    keys_pressed = self.main.events.check_key(key=list(self.movement_directions.keys()), action='pressed')
                    if keys_pressed:
                        if keys_pressed[0] in self.movement_dict:
                            keys_pressed[0] = self.movement_dict[keys_pressed[0]]
                        self.move_timer = 0
                        self.player_afk_timer = 0
                        self.movement_held = {'up': 0, 'down': 0, 'left': 0, 'right': 0, keys_pressed[0]: 1}
                    keys_unpressed = self.main.events.check_key(key=list(self.movement_directions.keys()), action='unpressed')
                    if keys_unpressed:
                        if keys_unpressed[0] in self.movement_dict:
                            keys_unpressed[0] = self.movement_dict[keys_unpressed[0]]
                        self.movement_held[keys_unpressed[0]] = 0
                        self.no_movement = False
                    if self.interpolating:
                        if keys_pressed and not self.map.show_map:
                            self.stored_movement = self.movement_directions[keys_pressed[0]]
                    else:
                        self.reset_objects_while()
                        if self.resolve_state:
                            if self.resolve_state == 'ice':
                                self.resolve_ice()
                            elif self.resolve_state == 'conveyors':
                                self.resolve_conveyors()
                            elif self.resolve_state == 'ice_2':
                                self.resolve_ice()
                            if self.resolve_state == 'splitters':
                                self.resolve_splitters()
                            if self.resolve_state == 'statues':
                                self.resolve_statues()
                            if self.resolve_state == 'spikes':
                                self.resolve_spikes()
                            if self.resolve_state == 'end':
                                self.resolve_standing()
                                self.resolve_state = None
                                self.reset_objects_end()
                                self.level.cache_level()
                        else:
                            if self.player_afk_timer < self.player_afk:
                                self.player_afk_timer += 1
                                if self.player_afk_timer == self.player_afk:
                                    for player_cell in self.player_cells.values():
                                        if player_cell.check_element(name='player', state='idle'):
                                            self.main.audio.play_sound(name='player_sleep')
                                            player_cell.elements['player']['state'] = 'sleeping'
                            if not self.map.show_map:
                                if self.main.debug or (not self.main.debug and not self.no_steps):
                                    if self.stored_movement:
                                        self.move_players(movement=self.stored_movement)
                                        self.stored_movement = None
                                    else:
                                        if keys_pressed:
                                            self.move_players(movement=self.movement_directions[keys_pressed[0]])
                                        else:
                                            for key in self.movement_held:
                                                if self.movement_held[key]:
                                                    self.movement_held[key] += 1
                                                    if self.movement_held[key] > self.hold_move_delay:
                                                        self.move_players(movement=self.movement_directions[key])
                                else:
                                    if keys_pressed:
                                        self.no_steps = False
                                        self.stored_movement = None
                                        self.load_level(name=self.level.name, load_respawn='current')
            else:
                if not self.main.transition.fade_in:
                    # this triggers when we close the game, need to check that were transitioning levels, also it is a cool effect
                    self.main.shaders.apply_effect(display_layer=['level_background', 'level_main', 'level_player', 'level_ui', 'level_map'], effect='pixelate', effect_data={'length': 0.5})

    def draw(self, displays):
        self.level.draw(displays=displays)
        self.tutorials.draw(displays=displays)
        self.cutscene.draw(displays=displays)
        self.map.draw(displays=displays)
        self.main.text_handler.activate_text(text_group='steps', text_id=self.level.steps)
        if not self.player_cells or self.no_steps:
            self.main.text_handler.activate_text(text_group='game', text_id='reset')
        for sign in self.sign_data:
            if sign in self.main.text_handler.sign_lines:
                for offset in range(self.main.text_handler.sign_lines[sign]):
                    self.main.text_handler.activate_text(text_group='signs', text_id=f'{sign}_{offset}')
        if self.main.debug:
            if self.teleporter_data['standing'] or self.teleporter_data['setting']:
                self.main.text_handler.activate_text(text_group='game', text_id='set_warp')
        else:
            if self.teleporter_data['standing']:
                if isinstance(self.teleporter_data['standing'], list):
                    self.main.text_handler.activate_text(text_group='game', text_id='warp?')
                else:
                    self.main.text_handler.activate_text(text_group='game', text_id='warp')
            if self.lock_data:
                self.main.text_handler.activate_text(text_group='locks', text_id=self.lock_data)

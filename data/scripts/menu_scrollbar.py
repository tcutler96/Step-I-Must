import pygame as pg


class MenuScrollbar:
    def __init__(self, main, max_scroll, scroll_step):
        self.main = main
        self.max_scroll = max_scroll
        self.scroll_step = scroll_step
        self.padding = 5
        self.overlap = 4
        self.alpha_start = 100.0
        self.alpha_step = 15.5
        self.arrows = self.get_arrows()
        self.bar = self.get_bar()
        self.delay = 2
        self.timer = 0

    def get_arrows(self):
        arrows = {}
        for direction in ['up', 'down']:
            arrows[direction] = {}
            default_surface = self.main.utilities.get_image(group='scrollbar', name=f'{direction}_default')
            hovered_surface = self.main.utilities.get_image(group='scrollbar', name=f'{direction}_hovered')
            size = default_surface.get_size()
            position = (self.main.display.width - size[0] - self.padding, self.padding if direction == 'up' else self.main.display.height - self.padding - size[1])
            rect = pg.Rect(position, size)
            arrows[direction] = {'surfaces': {'default': default_surface, 'hovered': hovered_surface}, 'active_surface': 'default', 'size': size, 'position': position, 'rect': rect, 'alpha': self.alpha_start}
        return arrows

    def get_bar(self):
        surface = self.main.utilities.get_image(group='scrollbar', name='bar')
        size = surface.get_size()
        bar_start = self.arrows['up']['rect'].bottom - self.overlap
        bar_end = self.arrows['down']['rect'].top - size[1] + self.overlap
        scroll_size = round((bar_end - bar_start) / (self.max_scroll / self.scroll_step), 5)
        x_position = self.arrows['up']['rect'].center[0] - size[0] // 2
        y_position = bar_start
        positions = [(x_position, y_position)]
        while round(y_position) < bar_end:
            y_position += scroll_size
            positions.append((x_position, round(y_position)))
        bar = {'surface': surface, 'positions': positions, 'alpha': self.alpha_start}
        return bar

    def start_up(self):
        for direction in ['up', 'down']:
            self.arrows[direction]['alpha'] = self.alpha_start
            self.arrows[direction]['surfaces']['default'].set_alpha(self.arrows[direction]['alpha'])
            self.arrows[direction]['surfaces']['hovered'].set_alpha(self.arrows[direction]['alpha'])
        self.bar['alpha'] = self.alpha_start
        self.bar['surface'].set_alpha(self.bar['alpha'])

    def update(self, scroll, offset, mouse_position):
        if self.timer:
            self.timer -= 1
        response = None
        for direction in ['up', 'down']:
            arrow_data = self.arrows[direction]
            arrow_data['active_surface'] = 'default'
            if (direction == 'up' and scroll) or (direction == 'down' and scroll < self.max_scroll):
                if arrow_data['alpha'] < 255:
                    arrow_data['alpha'] = min(arrow_data['alpha'] + self.alpha_step, 255)
                    arrow_data['surfaces']['default'].set_alpha(arrow_data['alpha'])
                    arrow_data['surfaces']['hovered'].set_alpha(arrow_data['alpha'])
                elif offset == [0, 0] and arrow_data['rect'].collidepoint(mouse_position):
                    arrow_data['active_surface'] = 'hovered'
                    self.main.display.set_cursor(cursor='hand')
                    if not self.timer and self.main.events.check_key(key='mouse_1', action='held'):
                        self.timer = self.delay
                        response = direction
            elif arrow_data['alpha'] > self.alpha_start:
                arrow_data['alpha'] = max(arrow_data['alpha'] - self.alpha_step, self.alpha_start)
                arrow_data['surfaces']['default'].set_alpha(arrow_data['alpha'])
                arrow_data['surfaces']['hovered'].set_alpha(arrow_data['alpha'])
        if self.bar['alpha'] < 255:
            self.bar['alpha'] = min(self.bar['alpha'] + self.alpha_step, 255)
            self.bar['surface'].set_alpha(self.bar['alpha'])
        return response

    def draw(self, displays, scroll, offset):
        bar_position = self.bar['positions'][scroll // self.scroll_step]
        displays['ui'].blit(source=self.bar['surface'], dest=(bar_position[0], bar_position[1] + offset[1]))
        displays['ui'].blit(source=self.arrows['up']['surfaces'][self.arrows['up']['active_surface']], dest=(self.arrows['up']['position'][0], self.arrows['up']['position'][1] + offset[1]))
        displays['ui'].blit(source=self.arrows['down']['surfaces'][self.arrows['down']['active_surface']], dest=(self.arrows['down']['position'][0], self.arrows['down']['position'][1] + offset[1]))

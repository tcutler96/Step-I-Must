import pygame as pg


class TextElement:
    def __init__(self, main, text, surface, position, bounce, alpha_up, alpha_down, shadow_offset, display_layer, menu_state, active, delay, duration,
                 interactable, hovered_surface, hovered_position, hovered_shadow_offset):
        self.main = main
        self.text = text
        if isinstance(surface, tuple):
            self.surface = surface[0]
            self.shadow_surface = surface[1]
        else:
            self.surface = surface
            self.shadow_surface = None
        self.size = self.surface.get_size()
        self.position = position
        self.base_position = position
        self.bounce = bounce
        self.alpha = 0.0
        self.alpha_up = alpha_up
        self.alpha_down = alpha_down
        self.shadow_offset = shadow_offset
        self.base_shadow_offset = shadow_offset
        self.offset = [0, 0]
        self.scroll = 0
        self.rect = pg.Rect(self.position, self.size)
        self.display_layer = display_layer
        self.menu_state = menu_state
        self.active = active
        self.timer = 0
        self.delay = delay
        self.duration = duration
        self.interactable = interactable
        if isinstance(hovered_surface, tuple):
            self.hovered_surface = hovered_surface[0]
            self.hovered_shadow_surface = hovered_surface[1]
        else:
            self.hovered_surface = hovered_surface
            self.hovered_shadow_surface = None
        self.hovered_position = hovered_position
        self.base_hovered_position = hovered_position
        self.hovered_shadow_offset = hovered_shadow_offset
        self.hovered = False
        self.last_hovered = False
        self.selected = False

    def activate(self, delay, duration, offset):
        if not self.active:
            self.active = True
            self.timer = 0
            self.delay = delay * self.main.fps
            self.duration = duration * self.main.fps
            self.offset = tuple(offset)

    def deactivate(self):
        self.active = False

    def update_position(self, position):
        if position != self.base_position:
            self.base_position = position
            self.rect = pg.Rect(self.position, self.size)

    def update_positions(self, mouse_position, bounce, sway):
        self.position = (self.base_position[0] + self.offset[0], self.base_position[1] + self.offset[1] - self.scroll + self.bounce * bounce)
        self.hovered_position = (self.base_hovered_position[0] + self.offset[0], self.base_hovered_position[1] + self.offset[1] - self.scroll + self.bounce * bounce)
        self.rect = pg.Rect(self.position, self.size)
        if self.base_shadow_offset == 'mouse':
            self.shadow_offset = ((self.rect.center[0] - mouse_position[0]) // 16, (self.rect.center[1] - mouse_position[1]) // 32)
        elif self.base_shadow_offset == 'sway':
            self.shadow_offset = (3 + sway[0], 3 + sway[1])

    def update(self, mouse_position, bounce, sway):
        self.last_hovered = self.hovered
        self.hovered = False
        self.selected = False
        if self.active:
            if self.delay:
                self.timer += 1
            if self.timer == self.delay:
                self.timer = 0
                self.delay = 0
            if not self.delay:
                self.update_positions(mouse_position=mouse_position, bounce=bounce, sway=sway)
                if self.alpha < 255:
                    self.alpha = min(self.alpha + self.alpha_up, 255)
                    self.surface.set_alpha(self.alpha)
                    if self.shadow_surface:
                        self.shadow_surface.set_alpha(self.alpha)
                elif self.interactable and self.offset == (0, 0) and self.main.display.cursor.cursor and (self.menu_state == self.main.menu_state) and self.rect.collidepoint(mouse_position):
                    self.hovered = True
                    if not self.last_hovered:
                        self.main.audio.play_sound(name='menu_highlight', existing='overlap')
                    self.main.display.set_cursor(cursor='hand')
                    if self.main.events.check_key(key='mouse_1'):
                        self.selected = 'left'
                    elif self.main.events.check_key(key='mouse_3'):
                        self.selected = 'right'
                if self.duration:
                    self.timer += 1
                    if self.timer == self.duration:
                        self.active = False
                else:
                    self.active = False
        elif self.alpha:
            self.alpha = max(self.alpha - self.alpha_down, 0)
            self.surface.set_alpha(self.alpha)
            if self.shadow_surface:
                self.shadow_surface.set_alpha(self.alpha)

    def draw(self, displays):
        if self.rect.colliderect(self.main.display.rect):
            if self.hovered:
                if self.hovered_shadow_surface:
                    displays[self.display_layer].blit(source=self.hovered_shadow_surface, dest=(self.hovered_position[0] + self.hovered_shadow_offset[0], self.hovered_position[1] + self.hovered_shadow_offset[1]))
                displays[self.display_layer].blit(source=self.hovered_surface, dest=self.hovered_position)
            elif self.alpha:
                if self.shadow_surface:
                    displays[self.display_layer].blit(source=self.shadow_surface, dest=(self.position[0] + self.shadow_offset[0], self.position[1] + self.shadow_offset[1]))
                displays[self.display_layer].blit(source=self.surface, dest=self.position)

import pygame as pg


class TextElement:
    def __init__(self, main, text, surface, position, shadow_offset, display_layer, active, delay, duration, interactable, hovered_surface, hovered_position, hovered_shadow_offset):
        self.main = main
        self.text = text
        if isinstance(surface, tuple):
            self.surface = surface[0]
            self.shadow_surface = surface[1]
        else:
            self.surface = surface
            self.shadow_surface = None
        self.size = self.surface.get_size()
        self.alpha = 0.0
        self.alpha_step = 25.5
        self.position = position
        self.shadow_offset = shadow_offset
        self.offset = [0, 0]
        self.scroll = 0
        self.rect = pg.Rect(self.position, self.size)
        self.display_layer = display_layer if display_layer in self.main.display.display_layers else 'ui'
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
        self.hovered_shadow_offset = hovered_shadow_offset
        self.hovered = False
        self.selected = False

    def activate(self, delay, duration, offset):
        if not self.active:
            self.active = True
            self.timer = 0
            self.delay = delay * self.main.fps
            self.duration = duration * self.main.fps
            self.offset = tuple(offset)

    # def update_position(self, position):
    #     if position != self.position:
    #         self.position = position
    #         self.rect = pg.Rect(self.position, self.surface.get_size())

    def deactivate(self):
        self.active = False

    def update(self, mouse_position):
        self.hovered = False
        self.selected = False
        # control shadow offset here, add sin sway option for titles etc...
        # self.shadow_offset = (self.shadow_offset[0] + 1, self.shadow_offset[1])
        # add slight bounce to text to add a bit of character, move on same clock as the game sprites...
        if self.active:
            if self.delay:
                self.timer += 1
            if self.timer == self.delay:
                self.timer = 0
                self.delay = 0
            if not self.delay:
                if self.alpha < 255:
                    self.alpha = min(self.alpha + self.alpha_step, 255)
                    self.surface.set_alpha(self.alpha)
                    if self.shadow_surface:
                        self.shadow_surface.set_alpha(self.alpha)
                elif (self.interactable and self.offset == (0, 0) and self.main.display.cursor.cursor and
                      self.rect.collidepoint((mouse_position[0], mouse_position[1] + self.scroll))):
                    self.hovered = True
                    self.main.display.set_cursor(cursor='hand')
                    if self.main.events.check_key(key='mouse_1'):
                        self.selected = True
                if self.duration:
                    self.timer += 1
                    if self.timer == self.duration:
                        self.active = False
                else:
                    self.active = False
        elif self.alpha:
            self.alpha = max(self.alpha - self.alpha_step, 0)
            self.surface.set_alpha(self.alpha)
            if self.shadow_surface:
                self.shadow_surface.set_alpha(self.alpha)

    def draw(self, displays):
        position = (self.position[0] + self.offset[0], self.position[1] + self.offset[1] - self.scroll)
        hovered_position = (self.hovered_position[0] + self.offset[0], self.hovered_position[1] + self.offset[1] - self.scroll) if self.hovered_position else None
        rect = pg.Rect(position, self.size)
        if rect.colliderect(self.main.display.rect):
            if self.hovered:
                if self.hovered_shadow_surface:
                    displays[self.display_layer].blit(source=self.hovered_shadow_surface, dest=(hovered_position[0] + self.hovered_shadow_offset[0], hovered_position[1] + self.hovered_shadow_offset[1]))
                displays[self.display_layer].blit(source=self.hovered_surface, dest=hovered_position)
            elif self.alpha:
                if self.shadow_surface:
                    displays[self.display_layer].blit(source=self.shadow_surface, dest=(position[0] + self.shadow_offset[0], position[1] + self.shadow_offset[1]))
                displays[self.display_layer].blit(source=self.surface, dest=position)

import pygame as pg


class Particle:
    def __init__(self, main, display_layer, position=(0, 0), velocity=(0, 0), velocity_min=(-1, -1), velocity_max=(1, 1), velocity_loop=(False, False), acceleration=(0, 0),
                 size=1, size_min=0, size_max=1, size_step=0, size_loop=False, colour=(0, 0, 0), alpha=255, alpha_min=0, alpha_max=255, alpha_step=0, alpha_loop=False,
                 remove_age=60, remove_age_shrink=0.1, remove_age_fade=5, remove_size=True, remove_alpha=True):
        self.main = main
        self.display_layer = display_layer
        self.age = 0
        self.remove = False
        self.position = position
        self.velocity = velocity
        self.velocity_min = velocity_min
        self.velocity_max = velocity_max
        self.velocity_loop = velocity_loop
        self.acceleration = acceleration
        self.size = size
        self.size_min = min(size, size_min)
        self.size_max = max(size, size_max)
        self.size_step = size_step
        self.size_loop = size_loop
        self.colour = colour
        self.alpha = alpha
        self.alpha_min = alpha_min
        self.alpha_max = alpha_max
        self.alpha_step = alpha_step
        self.alpha_loop = alpha_loop
        self.remove_age = remove_age * self.main.fps
        self.remove_age_shrink = remove_age_shrink
        self.remove_age_fade = remove_age_fade
        self.remove_size = remove_size
        self.remove_alpha = remove_alpha

    def update_age(self):
        self.age += 1
        if self.remove_age and self.age >= self.remove_age:
            self.remove_age = 0
            if self.remove_age_shrink:
                self.remove_size = True
                self.size_min = 0
                self.size_step = -self.remove_age_shrink
                self.size_loop = False
            if self.remove_age_fade:
                self.remove_alpha = True
                self.alpha_min = 0
                self.alpha_step = -self.remove_age_fade
                self.alpha_loop = False

    def update_position(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        if self.acceleration[0]:
            self.velocity[0] += self.acceleration[0]
            if self.velocity[0] >= self.velocity_max[0]:
                self.velocity[0] = self.velocity_max[0]
                if self.velocity_loop[0]:
                    self.acceleration[0] *= -1
            elif self.velocity[0] <= self.velocity_min[0]:
                self.velocity[0] = self.velocity_min[0]
                if self.velocity_loop[0]:
                    self.acceleration[0] *= -1
        if self.acceleration[1]:
            self.velocity[1] += self.acceleration[1]
            if self.velocity[1] >= self.velocity_max[1]:
                self.velocity[1] = self.velocity_max[1]
                if self.velocity_loop[1]:
                    self.acceleration[1] *= -1
            elif self.velocity[1] <= self.velocity_min[1]:
                self.velocity[1] = self.velocity_min[1]
                if self.velocity_loop[1]:
                    self.acceleration[1] *= -1

    def update_size(self):
        if self.size_step:
            self.size += self.size_step
            if self.size >= self.size_max:
                self.size = self.size_max
                if self.size_loop:
                    self.size_step *= -1
            elif self.size <= self.size_min:
                self.size = self.size_min
                if self.size_loop:
                    self.size_step *= -1

    def update_alpha(self):
        if self.alpha_step:
            self.alpha += self.alpha_step
            if self.alpha >= self.alpha_max:
                self.alpha = self.alpha_max
                if self.alpha_loop:
                    self.alpha_step *= -1
            elif self.alpha <= self.alpha_min:
                self.alpha = self.alpha_min
                if self.alpha_loop:
                    self.alpha_step *= -1

    def update(self):
        self.update_age()
        self.update_position()
        self.update_size()
        self.update_alpha()
        if self.remove_size and int(self.size) <= 0:
            self.remove = True
        if self.remove_alpha and self.alpha <= 0:
            self.remove = True

    def draw(self, displays):
        if int(self.size) >= 1:
            particle_size = int(self.size)
            particle_surface = pg.Surface((particle_size * 2, particle_size * 2))
            pg.draw.circle(surface=particle_surface, color=self.colour, center=(particle_size, particle_size), radius=particle_size)
            particle_surface.set_colorkey((0, 0, 0))
            particle_surface.set_alpha(self.alpha)
            displays[self.display_layer].blit(source=particle_surface, dest=(int(self.position[0] - particle_size), int(self.position[1] - particle_size)))

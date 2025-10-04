from scripts.particle import Particle
import pygame as pg


class ParticleHandler:
    def __init__(self, main):
        self.main = main
        self.particles = []
        self.glow_types = {'default': pg.BLEND_ALPHA_SDL2, 'add': pg.BLEND_RGB_ADD, 'sub': pg.BLEND_RGB_SUB}

    def add_particle(self, amount=1, display_layer='ui', position=(0, 0), velocity=(0, 0), velocity_min=(-1, -1), velocity_max=(1, 1), velocity_loop=(False, False), acceleration=(0, 0),
                     size=1, size_min=0, size_max=1, size_step=0, size_loop=False, colour=(0, 0, 0), alpha=255, alpha_min=0, alpha_max=255, alpha_step=0, alpha_loop=False,
                     remove_age=60, remove_age_shrink=0.1, remove_age_fade=5, remove_size=True, remove_alpha=True):
        # add any additional input checks here
        if display_layer not in self.main.display.display_layers:
            display_layer = 'ui'
        if isinstance(colour, str):
            colour = self.main.utilities.get_colour(colour=colour)
        elif colour == (0, 0, 0):
            colour = (1, 1, 1)
        for _ in range(int(self.main.utilities.get_value(amount))):
            self.particles.append(Particle(main=self.main, display_layer=display_layer, position=self.main.utilities.get_value(position), velocity=self.main.utilities.get_value(velocity),
                                           velocity_min=self.main.utilities.get_value(velocity_min), velocity_max=self.main.utilities.get_value(velocity_max), velocity_loop=velocity_loop,
                                           acceleration=self.main.utilities.get_value(acceleration), size=self.main.utilities.get_value(size), size_min=self.main.utilities.get_value(size_min),
                                           size_max=self.main.utilities.get_value(size_max), size_step=self.main.utilities.get_value(size_step), size_loop=size_loop, colour=self.main.utilities.get_value(colour),
                                           alpha=self.main.utilities.get_value(alpha), alpha_min=self.main.utilities.get_value(alpha_min), alpha_max=self.main.utilities.get_value(alpha_max),
                                           alpha_step=self.main.utilities.get_value(alpha_step), alpha_loop=alpha_loop, remove_age=self.main.utilities.get_value(remove_age),
                                           remove_age_shrink=self.main.utilities.get_value(remove_age_shrink), remove_age_fade=self.main.utilities.get_value(remove_age_fade), remove_size=remove_size, remove_alpha=remove_alpha))

    def remove_particles(self, display_layer):
        if display_layer == 'all':
            self.particles = []
        else:
            for _, particle in sorted(enumerate(self.particles), reverse=True):
                if particle.display_layer == display_layer:
                    self.particles.remove(particle)

    def update(self):
        for _, particle in sorted(enumerate(self.particles), reverse=True):
            particle.update()
            if particle.remove:
                self.particles.remove(particle)

    def draw(self, displays):
        for _, particle in sorted(enumerate(self.particles), reverse=True):
            particle.draw(displays=displays)

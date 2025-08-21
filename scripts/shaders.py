import moderngl as mgl
from array import array


class Shaders:
    def __init__(self, main):
        self.main = main
        self.context = mgl.create_context()
        self.quad_buffer = self.context.buffer(data=array('f', [-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0]))
        self.vertex_shader, self.fragment_shader = self.main.assets.shaders['vertex'], self.main.assets.shaders['fragment']
        self.program = self.context.program(vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader)
        self.set_uniforms(uniforms={'fps': self.main.fps, 'resolution': self.main.display.size, 'aspect_ratio': self.main.display.aspect_ratio, 'pixel_size': self.main.display.pixel_size})
        self.render_object = self.context.vertex_array(program=self.program, content=[(self.quad_buffer, '2f 2f', 'vert', 'texcoord')], mode=mgl.TRIANGLE_STRIP)
        self.extra_textures = ['buffer']
        self.textures = self.create_textures()
        self.render_buffer = self.context.renderbuffer(size=self.main.display.size)
        self.frame_buffer = self.context.framebuffer(color_attachments=self.render_buffer)
        self.apply_shaders = self.main.assets.settings['shaders']['all']
        self.background = self.main.assets.settings['shaders']['background']
        self.chromatic_aberration = self.main.assets.settings['shaders']['chromatic_aberration']
        self.crt = self.main.assets.settings['shaders']['crt']
        self.vignette = self.main.assets.settings['shaders']['vignette']
        self.effect_data_length = 10
        self.default_effect_data = {'applied': 0, 'active': 0, 'scale': 0, 'length': 1, 'step': 0}
        self.effect_data = {'grey': {}, 'invert': {}, 'blur': {'current': 2, 'min': 2, 'max': 5},
                            'pixelate': {'current': 1, 'min': 1, 'max': 4}, 'chromatic': {},
                            'shockwave': {'x': 240, 'y': 160, 'amount': 0.1, 'width': 0.05},
                            'galaxy': {}, 'ripple': {}, 'gol': {'tick': False, 'counter': self.main.fps, 'speed': 5, 'draw': False},
                            'test': {}}
        self.shaders = self.load_shaders()
        self.missing_display_layers = []
        self.missing_effects = []
        # print("Max fragment uniform components:", self.context.info['GL_MAX_FRAGMENT_UNIFORM_COMPONENTS'])

    def change_resolution(self):
        self.context.viewport = (0, 0, *self.main.display.window_size)

    def set_uniforms(self, uniforms):
        for uniform, value in uniforms.items():
            try:
                self.program[uniform] = value
            except KeyError:
                pass

    def create_textures(self):
        textures = {}
        display_layers = self.main.display.display_layers + self.extra_textures
        for location, display_layer in enumerate(display_layers):
            texture = self.context.texture(size=self.main.display.size, components=4)
            texture.filter = (mgl.NEAREST, mgl.NEAREST)
            if display_layer not in self.extra_textures:
                texture.swizzle = 'BGRA'
            if display_layer == 'noise':
                texture.write(data=self.main.assets.images['other']['noise'].get_view('1'))
            texture.use(location=location)
            self.set_uniforms(uniforms={f'{display_layer}_display': location})
            textures[display_layer] = texture
        return textures

    def load_shaders(self):
        shaders = {display_layer: self.default_effect_data for display_layer in self.main.display.display_layers}
        for index, (effect, data) in enumerate(self.effect_data.items()):
            self.effect_data[effect] = {'index': index + 1, 'data': data}
            self.set_uniforms(uniforms={f'{effect}_index': index + 1})
        return shaders

    def clear_gol(self):
        self.textures['buffer'].release()
        buffer = self.context.texture(size=self.main.display.size, components=4)
        buffer.filter = (mgl.NEAREST, mgl.NEAREST)
        buffer.use(location=len(self.textures) - 1)
        self.textures['buffer'] = buffer

    def apply_effect(self, display_layer, effect, effect_data=None):
        if self.apply_shaders:
            display_layers = self.main.display.display_layers[:-1] if display_layer == 'all' else [display_layer] if not isinstance(display_layer, list) else display_layer
            for display_layer in display_layers:
                if display_layer in self.main.display.display_layers and (not effect or effect in self.effect_data):
                    if not effect:
                        self.shaders[display_layer]['applied'] = 0
                        self.shaders[display_layer]['active'] = 0
                    elif not self.shaders[display_layer]['active']:
                        if effect == 'gol':
                            self.clear_gol()
                        apply_effect_data = self.default_effect_data.copy() | self.effect_data[effect]['data'] | (effect_data if effect_data else {})
                        apply_effect_data['applied'] = self.effect_data[effect]['index']
                        apply_effect_data['active'] = self.effect_data[effect]['index']
                        apply_effect_data['step'] = ((1 / self.main.fps) / apply_effect_data['length']) if apply_effect_data['length'] > 0 else 1
                        del apply_effect_data['length']
                        if len(apply_effect_data) > self.effect_data_length:
                            print(f'warning: {effect} effect data exceeds limit, increase effect data length by at least {len(apply_effect_data) - self.effect_data_length}...')
                        self.shaders[display_layer] = apply_effect_data
                    elif not self.shaders[display_layer]['applied']:
                        self.shaders[display_layer]['applied'] = self.effect_data[effect]['index']
                else:
                    if display_layer not in self.main.display.display_layers and display_layer not in self.missing_display_layers:
                        print(f"'{display_layer}' display layer not found...")
                        self.missing_display_layers.append(display_layer)
                    if effect not in self.effect_data and effect not in self.missing_effects:
                        print(f"'{effect}' shader effect not found...")
                        self.missing_effects.append(effect)

    def update_effect_current(self, effect_data):
        if all(data in effect_data for data in ['current', 'min', 'max']):
            effect_data['current'] = effect_data['min'] + effect_data['scale'] * (effect_data['max'] - effect_data['min'])
        if all(data in effect_data for data in ['current_2', 'min_2', 'max_2']):
            effect_data['current_2'] = int(effect_data['min_2'] + effect_data['scale'] * (effect_data['max_2'] - effect_data['min_2']))

    def update_effect_scale(self, effect_data):
        if effect_data['applied'] == effect_data['active']:
            if effect_data['scale'] < 1:
                effect_data['scale'] = min(1, effect_data['scale'] + effect_data['step'])
                self.update_effect_current(effect_data=effect_data)
        elif effect_data['scale'] > 0:
                effect_data['scale'] = max(0, effect_data['scale'] - effect_data['step'])
                self.update_effect_current(effect_data=effect_data)
                if effect_data['scale'] <= 0:
                    effect_data['active'] = 0

    def update_effect_data(self):
        for display_layer, effect_data in self.shaders.items():  # dont need display_layer in the end, just use .values...
            if effect_data['active']:
                self.update_effect_scale(effect_data=effect_data)
                if effect_data['active'] == self.effect_data['grey']['index']:
                    pass
                elif effect_data['active'] == self.effect_data['invert']['index']:
                    pass
                elif effect_data['active'] == self.effect_data['blur']['index']:
                    pass
                elif effect_data['active'] == self.effect_data['pixelate']['index']:
                    pass
                elif effect_data['active'] == self.effect_data['shockwave']['index']:
                    pass
                elif effect_data['active'] == self.effect_data['test']['index']:
                    pass
                elif effect_data['active'] == self.effect_data['gol']['index']:
                    effect_data['tick'] = False
                    effect_data['counter'] -= (self.main.fps // effect_data['speed'])
                    if effect_data['counter'] <= 0:
                        effect_data['tick'] = True
                        effect_data['counter'] = self.main.fps
                    effect_data['draw'] = True

    def get_effect_data_uniforms(self, background=False):
        effect_data_uniforms = {}
        for display_layer, effect_data in self.shaders.items():
            effect_data_uniforms[f'{display_layer}_effect'] = list(effect_data.values()) + [0] * (self.effect_data_length - len(effect_data))
            if background and display_layer == 'background':
                break
        return effect_data_uniforms

    def update(self, mouse_position):
        if self.main.events.check_key('v', 'held'):
            self.apply_effect(display_layer=['ui', 'level_main'], effect='test')
        if self.chromatic_aberration:
            self.apply_effect(display_layer=['ui'], effect='chromatic', effect_data={'length': 0})
        if self.background:
            self.apply_effect(display_layer=['background'], effect=self.background, effect_data={'length': 0})
        self.update_effect_data()
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_active': self.main.events.mouse_active, 'mouse_position': mouse_position,
                                    'chromatic_aberration': self.chromatic_aberration and self.apply_shaders, 'crt': self.crt and self.apply_shaders,
                                    'vignette': self.vignette and self.apply_shaders} | self.get_effect_data_uniforms())

    def reset_effects(self):
        for display_layer, effect_data in self.shaders.items():
            self.shaders[display_layer]['applied'] = 0

    def draw(self, displays):
        for display_layer, display_surface in displays.items():
            self.textures[display_layer].write(data=display_surface.get_view('1'))
        if self.background == 'gol':
            self.frame_buffer.use()
            self.frame_buffer.clear()
            self.render_object.render()
            self.context.copy_framebuffer(dst=self.textures['buffer'], src=self.frame_buffer)
            self.context.screen.use()
            self.shaders['background']['draw'] = False
            self.set_uniforms(uniforms=self.get_effect_data_uniforms(background=True))
        self.render_object.render()
        self.reset_effects()

    def quit(self):
        self.context.release()
        self.quad_buffer.release()
        self.program.release()
        self.render_object.release()
        self.render_buffer.release()
        self.frame_buffer.release()
        for texture in self.textures.values():
            texture.release()

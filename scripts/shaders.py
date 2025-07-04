import moderngl as mgl
from array import array


class Shaders:
    def __init__(self, main):
        self.main = main
        self.context = mgl.create_context()
        self.quad_buffer = self.context.buffer(data=array('f', [-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0]))
        self.vertex_shader, self.fragment_shader = self.main.assets.shaders['vertex'], self.main.assets.shaders['fragment']
        self.program = self.context.program(vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader)
        self.set_uniforms(uniforms={'fps': self.main.fps, 'resolution': self.main.display.size, 'pixel': (1 / self.main.display.size[0], 1 / self.main.display.size[1])})
        self.render_object = self.context.vertex_array(program=self.program, content=[(self.quad_buffer, '2f 2f', 'vert', 'texcoord')], mode=mgl.TRIANGLE_STRIP)
        self.extra_textures = ['buffer']
        self.textures = self.create_textures()
        self.render_buffer = self.context.renderbuffer(size=self.main.display.size)
        self.frame_buffer = self.context.framebuffer(color_attachments=self.render_buffer)
        self.effect_data_length = 5
        self.shaders = self.load_shaders(effects={'grey': {}, 'invert': {}, 'blur': {'size': 3, 'length': 7}, 'pixelate': {'size': 3.5},  # play around with this value to get cool low poly effects...
                                                  'test': {}, 'gol': {'tick': False, 'counter': self.main.fps}})
        # crt option in setting should be applied to all layers/ right at the end of the shader steps, after last display layer has been drawn, test if we can apply an effect to every layer...

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
            texture.use(location=location)
            self.set_uniforms(uniforms={f'{display_layer}_display': location})
            textures[display_layer] = texture
        return textures

    def load_shaders(self, effects):
        shaders = {'display_layers': {f'{display_layer}_effect': [0] * self.effect_data_length for display_layer in self.main.display.display_layers}, 'effects': {}}
        for index, (effect, data) in enumerate(effects.items()):
            shaders['effects'][effect] = {'index': index + 1, 'data': data}
            self.set_uniforms(uniforms={f'{effect}_index': index + 1})
        return shaders

    def apply_effect(self, display_layer, effect):
        # accept list of display_layers and effect
        # accept 'all' as a input?
        if display_layer in self.main.display.display_layers and effect in self.shaders['effects']:
            effect_data = list(self.shaders['effects'][effect]['data'].values())
            if len(effect_data) >= self.effect_data_length:
                print(f'increase shader effect size (by at least {1 + len(effect_data) - self.effect_data_length})...')
            effect_data2 = [self.shaders['effects'][effect]['index']] + effect_data + [0] * (self.effect_data_length - 1 - len(effect_data))
            self.shaders['display_layers'][f'{display_layer}_effect'] = effect_data2
        elif display_layer not in self.main.display.display_layers:
            print(f'{display_layer} display layer not found...')
        elif effect not in self.shaders['effects']:
            print(f'{effect} effect not found...')

    def update_effect_data(self):
        # add scales to all shader effects so that they come into effect gradually...
        # greyscale fades in and out etc...
        # loop over each display layer, and if they have an active effect or active data (ie effect turned off but still transitioning to off state), then change variables...
        # need to controls for each effects min, max, and step, and whether we want to increase or decrease effect variable...
        for effect, data in self.shaders['effects'].items():
            data = data['data']
            if effect == 'blur':  # only increase if blur is active in a display layer...
                pass
                # data['fraction'] += 0.01
                # data['amount'] = int(data['blur_fraction'])
            elif effect == 'gol':
                data['tick'] = False
                data['counter'] -= 20
                if data['counter'] <= 0:
                    data['tick'] = True
                    data['counter'] = self.main.fps

    def get_effect_data(self):
        effect_data = self.shaders['display_layers']
        for effect in self.shaders['effects'].values():
            effect_data = effect_data | effect['data']
        return effect_data

    def update(self, mouse_position):
        if self.main.events.check_key('e', 'held'):
            self.apply_effect(display_layer='menu', effect='pixelate')
            self.apply_effect(display_layer='level', effect='pixelate')
        self.update_effect_data()
        if self.main.assets.settings['video']['background'] in self.shaders['effects']:
            self.apply_effect(display_layer='background', effect=self.main.assets.settings['video']['background'])
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_active': self.main.events.mouse_active, 'mouse_position': mouse_position} | self.get_effect_data())

    def reset_effects(self):  # maybe we dont automatically reset all layers, if a layer is currently transitioning in or out of an effect...
        # need to have shader effect variables for each application...
        # if we have the map open with the gaem blur, opening the menu should gradually blur the map, so it needs its own distinct variables...
        # we cant change an effect variable during runs, we would need a seprate variable completely for each display layer...
        # this variable could be changed and used for any and all effects...
        for display_layer in self.shaders['display_layers']:
            self.shaders['display_layers'][display_layer] = [0] * self.effect_data_length

    def draw(self, displays):
        for display_layer, display_surface in displays.items():
            self.textures[display_layer].write(data=display_surface.get_view('1'))
        if self.main.assets.settings['video']['background'] == 'gol':
            self.frame_buffer.use()
            self.frame_buffer.clear()
            self.set_uniforms(uniforms={'draw_buffer': True})  # store this variable in shader data dict...
            self.render_object.render()
            self.context.copy_framebuffer(dst=self.textures['buffer'], src=self.frame_buffer)
            self.context.screen.use()
            self.set_uniforms(uniforms={'draw_buffer': False})
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

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
        self.extra_textures = ['background_buffer']
        self.textures = self.create_textures()
        self.render_buffer = self.context.renderbuffer(size=self.main.display.size)
        self.frame_buffer = self.context.framebuffer(color_attachments=self.render_buffer)
        self.shaders = self.load_shaders(effects={'grey': {}, 'invert': {}, 'blur': {'blur_amount': 3, 'blur_fraction': 0}, 'pixelate': {'pixelate_amount': 1.6},
                                                  'test': {}, 'gol': {'gol_tick': False, 'gol_counter': self.main.fps}})
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
        self.set_uniforms(uniforms={'display_layers': display_layers})
        for location, display_layer in enumerate(display_layers):
            texture = self.context.texture(size=self.main.display.size, components=4)
            texture.filter = (mgl.NEAREST, mgl.NEAREST)
            if display_layer not in self.extra_textures:
                texture.swizzle = 'BGRA'
            texture.use(location=location)
            self.set_uniforms(uniforms={display_layer: location})
            textures[display_layer] = texture
        return textures

    def load_shaders(self, effects):
        shaders = {'display_layers': {display_layer + '_effect': 0 for display_layer in self.main.display.display_layers}, 'effects': {}}
        for index, (effect, data) in enumerate(effects.items()):
            shaders['effects'][effect] = {'index': index + 1, 'data': data}
            self.set_uniforms(uniforms={f'{effect}_index': index + 1})
        return shaders

    def apply_effect(self, dispay_layer, effect):
        # accept list of display_layers and effect
        # accept 'all' as a input?
        # applying an effect to a display layer that already has an effect applied to it should combine the two, make combined effect in fragment shader...
        if dispay_layer in self.main.display.display_layers and effect in self.shaders['effects']:
            self.shaders['display_layers'][dispay_layer + '_effect'] = self.shaders['effects'][effect]['index']
        elif dispay_layer not in self.main.display.display_layers:
            print(f'{dispay_layer} display layer not found...')
        elif effect not in self.shaders['effects']:
            print(f'{effect} effect not found...')

    def update_effect_data(self):
        # add scales to all shader effects so that they come into effect gradually...
        # greyscale fades in and out etc...
        for effect, data in self.shaders['effects'].items():
            data = data['data']
            if effect == 'blur':  # only increase if blur is active in a display layer...
                pass
                # data['blur_fraction'] += 0.01
                # data['blur_amount'] = int(data['blur_fraction'])
            elif effect == 'gol':
                data['gol_tick'] = False
                data['gol_counter'] -= 20
                if data['gol_counter'] <= 0:
                    data['gol_tick'] = True
                    data['gol_counter'] = self.main.fps

    def get_effect_data(self):
        effect_data = self.shaders['display_layers']
        for effect in self.shaders['effects'].values():
            effect_data = effect_data | effect['data']
        return effect_data

    def update(self, mouse_position):
        if self.main.events.check_key('e', 'held'):
            self.apply_effect(dispay_layer='menu', effect='grey')
        self.update_effect_data()
        if self.main.assets.settings['video']['background'] in self.shaders['effects']:
            self.apply_effect(dispay_layer='background', effect=self.main.assets.settings['video']['background'])
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_active': self.main.events.mouse_active, 'mouse_position': mouse_position} | self.get_effect_data())

    def reset_effects(self):  # maybe we dont automatically reset all layers, if a layer is currently transitioning in or out of an effect...
        for display_layer in self.shaders['display_layers']:
            self.shaders['display_layers'][display_layer] = 0

    def draw(self, displays):
        for display_layer, display_surface in displays.items():
            self.textures[display_layer].write(data=display_surface.get_view('1'))
        if self.main.assets.settings['video']['background'] == 'gol':
            self.frame_buffer.use()
            self.frame_buffer.clear()
            self.set_uniforms(uniforms={'draw_background': True})
            self.render_object.render()
            self.context.copy_framebuffer(dst=self.textures['background_buffer'], src=self.frame_buffer)
            self.context.screen.use()
            self.set_uniforms(uniforms={'draw_background': False})
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

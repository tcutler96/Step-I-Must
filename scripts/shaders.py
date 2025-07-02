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
        self.gol_tick = self.main.fps
        self.shaders = self.load_shaders(effects={'grey': {}, 'invert': {}, 'blur': {'blur_amount': 5, 'blur_fraction': 0}, 'pixelate': {'pixelate_amount': 1.6},
                                                  'test': {}, 'gol': {'gol_tick': False, 'gol_counter': self.main.fps}})
        # pass in shader effect data (ie default blur amount)
        # crt option in setting should be applied to all layers/ right at the end of the shader steps, after last display layer has been drawn...

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
        return shaders

    def apply_effect(self, dispay_layer, effect):  # accept list of display_layers and effect?
        if dispay_layer in self.main.display.display_layers and effect in self.shaders['effects']:
            self.shaders['display_layers'][dispay_layer + '_effect'] = self.shaders['effects'][effect]['index']

    def update_effect_data(self):
        for effect, data in self.shaders['effects'].items():
            data = data['data']
            if effect == 'blur':  # only increase if blur is active in a display layer...
                pass
                # data['blur_fraction'] += 0.01
                # data['blur_amount'] = int(data['blur_fraction'])
            elif effect == 'gol':
                data['gol_tick'] = False
                data['gol_counter'] -= 1
                if data['gol_counter'] == 0:
                    data['gol_tick'] = True
                    data['gol_counter'] = self.main.fps

    def get_effect_data(self):
        effect_data = self.shaders['display_layers']
        for effect in self.shaders['effects'].values():
            effect_data = effect_data | effect['data']
        return effect_data

    def update(self, mouse_position):
        if self.main.events.check_key('e', 'held'):
            self.apply_effect(dispay_layer='background', effect='test')
        self.update_effect_data()
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_active': self.main.events.mouse_active, 'mouse_position': mouse_position,
                                    'gol_tick': self.gol_tick == self.main.fps} | self.get_effect_data())

    def reset_effects(self):
        for display_layer in self.shaders['display_layers']:
            self.shaders['display_layers'][display_layer] = 0

    def draw(self, displays):
        for display_layer, display_surface in displays.items():
            self.textures[display_layer].write(data=display_surface.get_view('1'))
        self.frame_buffer.use()  # we only need to use frame buffer render pass when background is set to gol...
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

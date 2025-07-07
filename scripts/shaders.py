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
        self.empty_effect_data = [0] * self.effect_data_length
        self.shaders = self.load_shaders(effects={'grey': {'scale': 0, 'step': 1 / self.main.fps}, 'invert': {'scale': 0, 'step': 1 / self.main.fps}, 'blur': {'size': 1, 'length': 3, 'counter': self.main.fps},
                                                  'pixelate': {'size': 1, 'counter': self.main.fps},  # play around with this value to get cool low poly effects...
                                                  'test': {}, 'gol': {'tick': False, 'counter': self.main.fps, 'speed': 5}})
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
        shaders = {'display_layers': {f'{display_layer}_effect': self.empty_effect_data for display_layer in self.main.display.display_layers}, 'effects': {}}
        for index, (effect, data) in enumerate(effects.items()):
            shaders['effects'][effect] = {'index': index + 1, 'data': data}
            self.set_uniforms(uniforms={f'{effect}_index': index + 1})
        return shaders

    def clear_gol(self):
        self.textures['buffer'].release()
        buffer = self.context.texture(size=self.main.display.size, components=4)
        buffer.filter = (mgl.NEAREST, mgl.NEAREST)
        buffer.use(location=len(self.textures) - 1)
        self.textures['buffer'] = buffer

    def apply_effect(self, display_layer, effect):
        # trying to apply an effect while the same effect is currently fading out wil not trigger until fade is finished (shouldnt be a big problem if the fade length is short, ie 1 second)...
        # need a variable to keep track of whether an effect has been/ is being applied and another to keep track of whether it is currently active (no longer being applied but 'fading' out)...
        # effect_data [applied, active, data...(scale, counter)]
        # if effect is applied, then active is true
        # if applied and active, then increase variables (fade in)
        # if not applied but active, then decrease variables (fade out)
        display_layers = self.main.display.display_layers if display_layer == 'all' else [display_layer] if not isinstance(display_layer, list) else display_layer
        # maybe dont include transition display layer in 'all', transition display layer is always last so just use display_layers[:-1], need to test applying effect to all display layers...
        for display_layer in display_layers:
            if display_layer in self.main.display.display_layers and (not effect or effect in self.shaders['effects']):
                display_layer += '_effect'
                if not effect:
                    self.shaders['display_layers'][display_layer] = self.empty_effect_data
                elif not self.shaders['display_layers'][display_layer][0]:
                    if effect == 'gol':
                        self.clear_gol()
                    effect_data = list(self.shaders['effects'][effect]['data'].values())
                    if len(effect_data) >= self.effect_data_length:
                        print(f'increase shader effect size (by at least {len(effect_data) + 1 - self.effect_data_length})...')
                    effect_data2 = [self.shaders['effects'][effect]['index']] + effect_data + [0] * (self.effect_data_length - 1 - len(effect_data))
                    self.shaders['display_layers'][display_layer] = effect_data2
            else:
                print(f"either '{display_layer}' display layer does not exist or '{effect}' effect does not exist...")

    def update_effect_data(self):
        blur = 5
        # loop over each display layer, and if they have an active effect or active data (ie effect turned off but still transitioning to off state), then change variables...
        # need to have controls for each effects min, max, and step, and whether we want to increase or decrease effect variable...
        for display_layer, effect_data in self.shaders['display_layers'].items():
            if effect_data[0] == self.shaders['effects']['grey']['index']:  # this doesnt turn off once it has been turned on...
                effect_data[1] += effect_data[2]  # effects are no longer being reset, need to be able to detect when an effect has been turned off/ is no longer being applied and then automatically fade it out/ off...
                if effect_data[1] <= 0 or effect_data[1] >= 1:
                    effect_data[2] *= -1
            elif effect_data[0] == self.shaders['effects']['invert']['index']:
                effect_data[1] += effect_data[2]
                if effect_data[1] <= 0 or effect_data[1] >= 1:
                    effect_data[2] *= 0
            elif effect_data[0] == self.shaders['effects']['blur']['index']:
                effect_data[3] -= blur
                if effect_data[3] <= 0:
                    effect_data[1] = min(blur, effect_data[1] + 1)
                    effect_data[2] = effect_data[1] * 2 + 1
                    effect_data[3] = self.main.fps
            elif effect_data[0] == self.shaders['effects']['pixelate']['index']:
                effect_data[2] -= 30
                if effect_data[2] <= 0:
                    effect_data[1] = min(6.4, effect_data[1] + 0.25)
                    effect_data[2] = self.main.fps
            elif effect_data[0] == self.shaders['effects']['test']['index']:
                pass
            elif effect_data[0] == self.shaders['effects']['gol']['index']:
                effect_data[1] = False
                effect_data[2] -= (self.main.fps // effect_data[3])
                if effect_data[2] <= 0:
                    effect_data[1] = True
                    effect_data[2] = self.main.fps
                effect_data[4] = True

    def update(self, mouse_position):
        if self.main.events.check_key('e', 'held'):
            self.apply_effect(display_layer=['menu', 'level'], effect='test')
        self.apply_effect(display_layer='background', effect=self.main.assets.settings['video']['background'])
        self.update_effect_data()
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_active': self.main.events.mouse_active, 'mouse_position': mouse_position} | self.shaders['display_layers'])

    def reset_effects(self):
        # dont automatically reset all layers, if a layer is currently transitioning in or out of an effect then leave it to finish...
        # we can handle this functionality in the update function i think...
        for display_layer, effect_data in self.shaders['display_layers'].items():
            # self.shaders['display_layers'][display_layer] = self.empty_effect_data
            self.shaders['display_layers'][display_layer][0] = 0

    def draw(self, displays):
        for display_layer, display_surface in displays.items():
            self.textures[display_layer].write(data=display_surface.get_view('1'))
        if self.main.assets.settings['video']['background'] == 'gol':
            self.frame_buffer.use()
            self.frame_buffer.clear()
            self.render_object.render()
            self.context.copy_framebuffer(dst=self.textures['buffer'], src=self.frame_buffer)
            self.context.screen.use()
            self.shaders['display_layers']['background_effect'][4] = False
            self.set_uniforms(uniforms={'background_effect': self.shaders['display_layers']['background_effect']})
        self.render_object.render()
        # self.reset_effects()

    def quit(self):
        self.context.release()
        self.quad_buffer.release()
        self.program.release()
        self.render_object.release()
        self.render_buffer.release()
        self.frame_buffer.release()
        for texture in self.textures.values():
            texture.release()

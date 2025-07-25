import moderngl as mgl
from array import array


class Shaders:
    def __init__(self, main):
        self.main = main
        self.context = mgl.create_context()
        self.quad_buffer = self.context.buffer(data=array('f', [-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0]))
        self.vertex_shader, self.fragment_shader = self.main.assets.shaders['vertex'], self.main.assets.shaders['fragment']
        self.program = self.context.program(vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader)
        self.set_uniforms(uniforms={'fps': self.main.fps, 'resolution': self.main.display.size, 'aspect_ratio': self.main.display.aspect_ratio, 'pixel_size': (1 / self.main.display.size[0], 1 / self.main.display.size[1])})
        self.render_object = self.context.vertex_array(program=self.program, content=[(self.quad_buffer, '2f 2f', 'vert', 'texcoord')], mode=mgl.TRIANGLE_STRIP)
        self.extra_textures = ['noise', 'buffer']
        self.textures = self.create_textures()
        self.render_buffer = self.context.renderbuffer(size=self.main.display.size)
        self.frame_buffer = self.context.framebuffer(color_attachments=self.render_buffer)
        self.effect_data_length = 10
        self.empty_effect_data = [0] * self.effect_data_length
        # default values for shader effects, we can optionally pass in values when shader effect is applied...
        # {'scale': 0.0-1.0, 'length': int (seconds), extra parameters...}
        self.shaders = self.load_shaders(effects={'grey': {'scale': 0, 'length': 0.5},
                                                  'invert': {'scale': 0, 'length': 0.5},
                                                  'blur': {'scale': 0, 'length': 0.5, 'samples': 2, 'min_samples': 2, 'max_samples': 25},
                                                  'pixelate': {'size': 1, 'counter': self.main.fps},  # play around with this value to get cool low poly effects, can switch between 12 - 16, can have diffent values for x and y...
                                                  'distort': {'scale': 0, 'step': 0.5, 'x': 240, 'y': 160, 'amount': 0.1, 'width': 0.05}, 'test': {}, 'gol': {'tick': False, 'counter': self.main.fps, 'speed': 5, 'draw': False}})
        self.apply_shaders = self.main.assets.settings['video']['shaders']
        self.background_effect = self.main.assets.settings['video']['background']
        # crt option in setting should be applied to all layers/ right at the end of the shader steps, after last display layer has been drawn, test if we can apply an effect to every layer...
        # how inefficient is it to have one fragment shader, would we get better frames from individual shaders?
        # pass in shader effect variables so we can control them (ie only greyscale the player layer slightly when we only have 1 step left but fully pixealte on teleport)...
        # add distortion effect to grey effect that is used when low/ out of steps...
        # have dict with all default shader effect data
        # have another dict for currently active shader effects, organised by display layers...
        # shader effect data for each display layer is left in dict form for easier manipulation...
        # convert to list at the end of the update function to be set as uniforms for fragment shader...

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

    def load_shaders(self, effects):
        shaders = {'display_layers': {f'{display_layer}_effect': self.empty_effect_data.copy() for display_layer in self.main.display.display_layers}, 'effects': {}}
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
        if self.apply_shaders:  # add shader options (fancy, simple, disabled), scale effects by some value?
            # if display_layer != 'background':
            #     print(display_layer, effect)
            display_layers = self.main.display.display_layers if display_layer == 'all' else [display_layer] if not isinstance(display_layer, list) else display_layer
            # maybe dont include transition display layer in 'all', transition display layer is always last so just use display_layers[:-1], need to test applying effect to all display layers...
            for display_layer in display_layers:
                if display_layer in self.main.display.display_layers and (not effect or effect in self.shaders['effects']):
                    display_layer += '_effect'
                    if not effect:
                        self.shaders['display_layers'][display_layer][0:2] = [0] * 2
                    elif not self.shaders['display_layers'][display_layer][1]:
                        if effect == 'gol':
                            self.clear_gol()
                        effect_data = list(self.shaders['effects'][effect]['data'].values())
                        if len(effect_data) >= self.effect_data_length:
                            print(f'increase shader effect size (by at least {len(effect_data) + 1 - self.effect_data_length})...')
                        self.shaders['display_layers'][display_layer] = [self.shaders['effects'][effect]['index']] * 2 + effect_data + [0] * (self.effect_data_length - 2 - len(effect_data))
                    elif not self.shaders['display_layers'][display_layer][0]:
                        self.shaders['display_layers'][display_layer][0] = self.shaders['effects'][effect]['index']
                else:
                    print(f"either '{display_layer}' display layer does not exist or '{effect}' effect does not exist...")

    def update_effect_data2(self, effect_data):
        if effect_data[0] == effect_data[1]:  # increase values
            if effect_data[2] < 1:
                effect_data[2] = min(1, effect_data[2] + (1 / self.main.fps) / effect_data[3])
                effect_data[4] = int(effect_data[5] + effect_data[2] * (effect_data[6] - effect_data[5]))
                if effect_data[2] >= 1:  # max value, stop endless loop
                    pass
        else:  # decrease values
            if effect_data[2] > 0:
                effect_data[2] = max(0, effect_data[2] - (1 / self.main.fps) / effect_data[3])
                effect_data[4] = int(effect_data[5] + effect_data[2] * (effect_data[6] - effect_data[5]))
                if effect_data[2] <= 0:  # min value
                    effect_data[1] = 0

    def update_effect_data(self):
        for display_layer, effect_data in self.shaders['display_layers'].items():  # dont need display_layer in the end, just use .values...
            if effect_data[1] == self.shaders['effects']['grey']['index']:
                self.update_effect_data2(effect_data=effect_data)  # we can just call this generic update function at the top of this loop and then do effect specific changes if needed...
            elif effect_data[1] == self.shaders['effects']['invert']['index']:
                self.update_effect_data2(effect_data=effect_data)
            elif effect_data[1] == self.shaders['effects']['blur']['index']:
                self.update_effect_data2(effect_data=effect_data)  # generic update of effect data (ie scale)
                # then we can make more effect specific changes here...
            elif effect_data[1] == self.shaders['effects']['pixelate']['index']:
                # self.update_effect_data2(effect_data=effect_data)
                if effect_data[0] == effect_data[1]:
                    effect_data[3] -= 30
                    if effect_data[3] <= 0:
                        effect_data[2] = min(16, effect_data[2] + 1)
                        effect_data[3] = self.main.fps
                else:
                    effect_data[3] -= 30
                    if effect_data[3] <= 0:
                        effect_data[2] = max(0, effect_data[2] - 1)
                        effect_data[3] = self.main.fps
                        if effect_data[2] <= 0:
                            effect_data[1] = 0
            elif effect_data[1] == self.shaders['effects']['distort']['index']:
                if effect_data[0]:
                    effect_data[2] = min(1, effect_data[2] + effect_data[3] / self.main.fps)
                else:
                    effect_data[2] = max(0, effect_data[2] - effect_data[3] / self.main.fps)
                    if effect_data[2] == 0:
                        effect_data[1] = 0
            elif effect_data[1] == self.shaders['effects']['test']['index']:
                if effect_data[0]:
                    pass
                else:
                    effect_data[1] = 0
            elif effect_data[1] == self.shaders['effects']['gol']['index']:
                if effect_data[0]:
                    effect_data[2] = False
                    effect_data[3] -= (self.main.fps // effect_data[4])
                    if effect_data[3] <= 0:
                        effect_data[2] = True
                        effect_data[3] = self.main.fps
                    effect_data[5] = True
                else:
                    effect_data[1] = 0

    def update(self, mouse_position):
        if self.main.events.check_key('x', 'held'):
            self.apply_effect(display_layer=['menu', 'level', 'ui'], effect='blur')
        if self.background_effect == 'gol':
            self.apply_effect(display_layer='background', effect='gol')
        self.update_effect_data()
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_active': self.main.events.mouse_active, 'mouse_position': mouse_position} | self.shaders['display_layers'])

    def reset_effects(self):
        for display_layer, effect_data in self.shaders['display_layers'].items():
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
            self.shaders['display_layers']['background_effect'][5] = False
            self.set_uniforms(uniforms={'background_effect': self.shaders['display_layers']['background_effect']})
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

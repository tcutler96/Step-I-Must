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
        self.effect_data_length = 6
        self.empty_effect_data = [0] * self.effect_data_length
        self.shaders = self.load_shaders(effects={'grey': {'scale': 0, 'step': 1}, 'invert': {'scale': 0, 'step': 1},
                                                  'blur': {'size': 1, 'length': 3, 'counter': self.main.fps},
                                                  'pixelate': {'size': 1, 'counter': self.main.fps},  # play around with this value to get cool low poly effects, can switch between 12 - 16, can have diffent values for x and y...
                                                  'test': {}, 'gol': {'tick': False, 'counter': self.main.fps, 'speed': 5, 'draw': False}})
        self.apply_shaders = self.main.assets.settings['video']['shaders']
        self.background_effect = self.main.assets.settings['video']['background']
        # crt option in setting should be applied to all layers/ right at the end of the shader steps, after last display layer has been drawn, test if we can apply an effect to every layer...
        # how inefficient is it to have one fragment shader, would we get better frames from individual shaders?

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
        shaders = {'display_layers': {f'{display_layer}_effect': self.empty_effect_data.copy() for display_layer in self.main.display.display_layers}, 'effects': {}}
        for index, (effect, data) in enumerate(effects.items()):
            shaders['effects'][effect] = {'index': index + 1, 'data': data}
            self.set_uniforms(uniforms={f'{effect}_index': index + 1})
        return shaders

    def clear_gol(self):  # gol background cycles through 4 versions of texture for some reason, could leave it as is as a cool quirk...
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
                    if not effect:  # if None effect passed in, then force effect data to be empty (maybe just set the first two indexes to zero and let the update function naturally fade out current effect)...
                        # self.shaders['display_layers'][display_layer] = self.empty_effect_data
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

    def update_effect_data(self):
        blur = 3 # add max blur variable in blur effect data...
        for display_layer, effect_data in self.shaders['display_layers'].items():  # dont need display_layer in the end, just use .values...
            if effect_data[1] == self.shaders['effects']['grey']['index']:
                if effect_data[0]:
                    effect_data[2] = min(1, effect_data[2] + effect_data[3] / self.main.fps)
                else:
                    effect_data[2] = max(0, effect_data[2] - effect_data[3] / self.main.fps)
                    if effect_data[2] == 0:
                        effect_data[1] = 0
            elif effect_data[1] == self.shaders['effects']['invert']['index']:
                if effect_data[0]:
                    effect_data[2] = min(1, effect_data[2] + effect_data[3] / self.main.fps)
                else:
                    effect_data[2] = max(0, effect_data[2] - effect_data[3] / self.main.fps)
                    if effect_data[2] == 0:
                        effect_data[1] = 0
            elif effect_data[1] == self.shaders['effects']['blur']['index']:
                # can we make a universal function to handle changing effect values, or is it not needed?
                # might need to have all effect datas follow the same default layout...
                # effect_data = [applied bool, active bool, counter, ]
                if effect_data[0]:  # increase values
                    effect_data[4] -= 15  # count down counter (-1 or -1/fps each time)
                    if effect_data[4] <= 0:  # counter hits zero, value change triggered
                        effect_data[2] = min(blur, effect_data[2] + 1)  # add step value, use min and max function with value min and max
                        effect_data[3] = effect_data[2] * 2 + 1  # extra effect values
                        effect_data[4] = self.main.fps  # set counter to default value
                        if effect_data[2] >= blur:  # max value, stop endless loop
                            pass
                else:  # decrease values
                    effect_data[4] -= 15
                    if effect_data[4] <= 0:
                        effect_data[2] = max(0, effect_data[2] - 1)
                        effect_data[3] = effect_data[2] * 2 + 1
                        effect_data[4] = self.main.fps
                        if effect_data[2] <= 0:  # min value
                            effect_data[1] = 0  # reset reset of effect data here or in reset_effects function?
            elif effect_data[1] == self.shaders['effects']['pixelate']['index']:
                print(1)
                if effect_data[0]:
                    effect_data[3] -= 30
                    if effect_data[3] <= 0:
                        effect_data[2] = min(16.4, effect_data[2] + 1.25)
                        effect_data[3] = self.main.fps
                else:
                    effect_data[3] -= 30
                    if effect_data[3] <= 0:
                        effect_data[2] = max(0, effect_data[2] - 1.25)
                        effect_data[3] = self.main.fps
                        if effect_data[2] <= 0:
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
        # if self.main.events.check_key('e', 'held'):
        #     self.apply_effect(display_layer=['menu', 'level'], effect='blur')
        self.apply_effect(display_layer='background', effect=self.background_effect)
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

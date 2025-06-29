import moderngl as mgl
from array import array


class Shaders:
    def __init__(self, main):
        self.main = main
        self.context = mgl.create_context()
        self.quad_buffer = self.context.buffer(data=array('f', [-1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, -1.0, -1.0, 0.0, 1.0, 1.0, -1.0, 1.0, 1.0]))
        self.vertex_shader, self.fragment_shader = self.main.assets.shaders['vertex'], self.main.assets.shaders['fragment']
        self.program = self.context.program(vertex_shader=self.vertex_shader, fragment_shader=self.fragment_shader)
        self.set_uniforms(uniforms={'fps': self.main.fps, 'resolution': self.main.display.window_size, 'pixel': (1 / self.main.display.size[0], 1 / self.main.display.size[1])})
        self.render_object = self.context.vertex_array(program=self.program, content=[(self.quad_buffer, '2f 2f', 'vert', 'texcoord')], mode=mgl.TRIANGLE_STRIP)
        self.extra_textures = ['background_buffer']
        self.textures = self.create_textures()
        self.render_buffer = self.context.renderbuffer(size=self.main.display.size)
        self.frame_buffer = self.context.framebuffer(color_attachments=self.render_buffer)
        self.apply_shader = False
        self.gol_tick = self.main.fps

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
            if display_layer != 'background_buffer':
                texture.swizzle = 'BGRA'
            texture.use(location=location)
            self.set_uniforms(uniforms={f'{display_layer}': location})
            textures[display_layer] = texture
        return textures

    def change_resolution(self):
        self.context.viewport = (0, 0, *self.main.display.window_size)
        # self.set_uniforms(uniforms={'resolution': self.main.display.window_size, 'pixel': (1 / self.main.display.window_size[0], 1 / self.main.display.window_size[1])})

    def update(self, mouse_position):
        self.gol_tick -= 5
        if self.gol_tick == 0:
            self.gol_tick = self.main.fps
        self.set_uniforms(uniforms={'time': self.main.runtime_seconds, 'mouse_posistion': mouse_position, 'mouse_active': self.main.events.mouse_active,
                                    'shader': self.apply_shader, 'gol_tick': self.gol_tick == self.main.fps})

    def draw(self, displays):
        for display_layer, display_surface in displays.items():
            self.textures[display_layer].write(data=display_surface.get_view('1'))
        self.frame_buffer.use()
        self.frame_buffer.clear()
        self.set_uniforms(uniforms={'draw_background': True})
        self.render_object.render()
        self.context.copy_framebuffer(dst=self.textures['background_buffer'], src=self.frame_buffer)
        self.context.screen.use()
        self.set_uniforms(uniforms={'draw_background': False})
        self.render_object.render()

    def quit(self):
        self.context.release()
        self.quad_buffer.release()
        self.program.release()
        self.render_object.release()
        self.render_buffer.release()
        self.frame_buffer.release()
        for texture in self.textures.values():
            texture.release()

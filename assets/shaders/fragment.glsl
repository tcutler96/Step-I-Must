#version 330 core

uniform sampler2D background;
uniform sampler2D menu;
uniform sampler2D level;
uniform sampler2D steps;
uniform sampler2D map;
uniform sampler2D level_editor;
uniform sampler2D ui;
uniform sampler2D transition;
uniform sampler2D background_buffer;
//uniform sampler2D noise;
uniform vec2 resolution;
uniform vec2 pixel;
uniform float time;
uniform bool shader;
uniform bool draw_background;
uniform bool gol_tick;

in vec2 uv;
out vec4 out_colour;

const vec4 on_colour = vec4(0.96, 0.95, 0.76, 1.0);
const vec4 off_colour = vec4(0.19, 0.16, 0.24, 1.0);

bool check_colour(vec4 colour) {
    vec4 difference = colour - on_colour;
    float absolute = abs(difference.r) + abs(difference.g) + abs(difference.b);
    return absolute < 0.015;
}

vec4 get_colour(vec2 uv, sampler2D surface) {  // this is pointless atm, need to be able to apply chosen shaders...
    vec4 colour = texture(surface, uv);
//    float grey = 0.299 * colour.r + 0.587 * colour.g + 0.114 * colour.b;
    return colour;
}

vec4 apply_shader(vec4 colour, int shader) {
    return colour;
}

vec4 game_of_life(vec2 uv) {
    return vec4(1.0);
}

void main() {
    vec2 uv_flipped = vec2(uv.x, 1.0 - uv.y);
    // when resolution is changed, this code no longer works, it still behaves with the old resolution for some reason...
//    vec4 buffer_colour = texture(buffer0, uv_flipped);
//    int current = int(check_colour(buffer_colour));
//    int surround = -current;
//    for (float i = -1.0; i < 2.0; i++) {
//        for (float j = -1.0; j < 2.0; j++) {
//            float x = uv_flipped.x + i * pixel.x;
//            float y = uv_flipped.y + j * pixel.y;
//            vec4 surround_colour = texture(buffer_surface, vec2(x, y));
//            surround += int(check_colour(surround_colour));
//        }
//    }
//    if (current == 1 && (surround < 1.5 || surround > 3.5)) {
//        current = 0;
//    } else if (current == 0 && (surround > 2.5 && surround < 3.5)) {
//        current = 1;
//    }
//    out_colour = vec4((on_colour.r * current) + (off_colour.r * (1 - current)), (on_colour.g * current) + (off_colour.g * (1 - current)), (on_colour.b * current) + (off_colour.b * (1 - current)), 1.0);

//    out_colour = texture(unscaled, uv);

    if (draw_background) {  // is there an easier way to combine the new background frame with the last one
        // would be cooler if we could scale the gol by the scale factor, would be easier to see what is happening...
        vec4 colour1 = get_colour(uv, background);
        vec4 colour2 = get_colour(uv_flipped, background_buffer);
        int current = int(check_colour(colour1)) | int(check_colour(colour2));
        if (gol_tick) {
            int surround = -current;
            for (float i = -1.0; i < 2.0; i++) {
                for (float j = -1.0; j < 2.0; j++) {
                    float x = uv.x + i * pixel.x;
                    float y = uv.y + j * pixel.y;
                    float x2 = uv_flipped.x + i * pixel.x;
                    float y2 = uv_flipped.y + j * pixel.y;
                    vec4 surround_colour = texture(background, vec2(x, y));
                    vec4 surround_colour2 = texture(background_buffer, vec2(x2, y2));
                    surround += int(check_colour(surround_colour)) | int(check_colour(surround_colour2));
                }
            }
            if (current == 1 && (surround < 1.5 || surround > 3.5)) {
                current = 0;
            } else if (current == 0 && (surround > 2.5 && surround < 3.5)) {
                current = 1;
            }
        }
        out_colour = vec4((on_colour.r * current) + (off_colour.r * (1 - current)), (on_colour.g * current) + (off_colour.g * (1 - current)), (on_colour.b * current) + (off_colour.b * (1 - current)), 1.0);
    } else {

        // add function that can apply simple shaders (ie grey, inverse) to each layer colour as wanted, add data input that tells which tells which shaders to apply to which layer...
        out_colour = vec4(0.0);
//        vec4 background_colour = get_colour(uv_flipped, background_buffer);
        vec4 background_colour = get_colour(uv, background);
        out_colour = mix(out_colour, background_colour, background_colour.a);
        vec4 menu_colour = get_colour(uv, menu);
//        if (shader) {
//            menu_colour = vec4(1.0 - menu_colour.r, 1.0 - menu_colour.g, 1.0 - menu_colour.b, menu_colour.a);
//        }
        out_colour = mix(out_colour, menu_colour, menu_colour.a);
        vec4 level_colour = texture(level, uv);
        if (shader) {
            float brightness = level_colour.r * 0.2126 + level_colour.r * 0.7152 + level_colour.b * 0.0722;
            level_colour = vec4(vec3(brightness), level_colour.a);
//            level_colour = vec4(1.0 - level_colour.r, 1.0 - level_colour.g, 1.0 - level_colour.b, level_colour.a);
        }
        out_colour = mix(out_colour, level_colour, level_colour.a);
        vec4 steps_colour = texture(steps, uv);
        out_colour = mix(out_colour, steps_colour, steps_colour.a);
        vec4 map_colour = texture(map, uv);
        out_colour = mix(out_colour, map_colour, map_colour.a);
        vec4 level_editor_colour = texture(level_editor, uv);
        out_colour = mix(out_colour, level_editor_colour, level_editor_colour.a);
        vec4 ui_colour = texture(ui, uv);
        out_colour = mix(out_colour, ui_colour, ui_colour.a);
        vec4 transition_colour = texture(transition, uv);
        out_colour = mix(out_colour, transition_colour, transition_colour.a);
    }
}

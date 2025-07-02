#version 330 core

uniform sampler2D background;
uniform int background_effect;
uniform sampler2D level;
uniform int level_effect;
uniform sampler2D steps;
uniform int steps_effect;
uniform sampler2D map;
uniform int map_effect;
uniform sampler2D level_editor;
uniform int level_editor_effect;
uniform sampler2D menu;
uniform int menu_effect;
uniform sampler2D ui;
uniform int ui_effect;
uniform sampler2D transition;
uniform int transition_effect;
uniform sampler2D background_buffer;

uniform int fps;
uniform vec2 resolution;
uniform vec2 pixel;
uniform float time;
uniform vec2 mouse_active;
uniform vec2 mouse_posistion;

uniform int blur_amount;
int blur_length = blur_amount * 2 + 1;
uniform float pixelate_amount;
uniform bool draw_background;
uniform bool gol_tick;
const vec4 on_colour = vec4(0.96, 0.95, 0.76, 1.0);
const vec4 off_colour = vec4(0.19, 0.16, 0.24, 1.0);

in vec2 uv;
out vec4 out_colour;

bool check_colour(vec4 colour) {
    vec4 difference = colour - on_colour;
    float absolute = abs(difference.r) + abs(difference.g) + abs(difference.b);
    return absolute < 0.015;
}

vec4 game_of_life(vec2 uv) {
    return vec4(1.0);
}

vec4 grey(sampler2D display_layer) {
    vec4 colour = texture(display_layer, uv);
    float brightness = colour.r * 0.2126 + colour.r * 0.7152 + colour.b * 0.0722;
    colour.rgb = vec3(brightness);
    return colour;
}

vec4 invert(sampler2D display_layer) {
    vec4 colour = texture(display_layer, uv);
    colour = vec4(vec3(1.0) - colour.rgb, colour.a);
    return colour;
}

vec4 blur(sampler2D display_layer) {
    vec4 colour = vec4(0.0);
    for (int i = 0; i < blur_length; i++) {
            for (int j = 0; j < blur_length; j++) {
                colour += texture(display_layer, uv + pixel * (vec2(i, j) - blur_amount));
            }
        }
    colour /= blur_length * blur_length;
    return colour;
}

vec4 pixelate(sampler2D display_layer) {
    float dx = pixelate_amount * pixel[0];
    float dy = pixelate_amount * pixel[1];
    vec4 colour = texture(display_layer, vec2(dx * ceil(uv.x / dx), dy * ceil(uv.y / dy)));
    return colour;
}

vec4 test(sampler2D display_layer) {
    vec4 colour = texture(display_layer, vec2(fract(uv.x * 3), fract(uv.y * 2)));
    return colour;
}

vec4 get_colour(sampler2D display_layer, int effect, vec4 out_colour) {
    vec4 colour;
    if (effect==1) {  // grey
        colour = grey(display_layer);
    } else if (effect==2) {  // invert
        colour = invert(display_layer);
    } else if (effect==3) {  // blur
        colour = blur(display_layer);
    } else if (effect==4) {  // pixelate
        colour = pixelate(display_layer);
    } else if (effect==5) {  // test
        colour = test(display_layer);
    } else {  // no effect
        colour = texture(display_layer, uv);
    }
    out_colour = mix(out_colour, colour, colour.a);
    return out_colour;
}

void main() {
    vec2 uv_flipped = vec2(uv.x, 1.0 - uv.y);
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
        vec4 colour1 = texture(background, uv);
        vec4 colour2 = texture(background_buffer, uv);
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
        out_colour = vec4(0.0);
        out_colour = get_colour(background, background_effect, out_colour);
        out_colour = get_colour(level, level_effect, out_colour);
        out_colour = get_colour(steps, steps_effect, out_colour);
        out_colour = get_colour(map, map_effect, out_colour);
        out_colour = get_colour(level_editor, level_editor_effect, out_colour);
        out_colour = get_colour(menu, menu_effect, out_colour);
        out_colour = get_colour(ui, ui_effect, out_colour);
        out_colour = get_colour(transition, transition_effect, out_colour);
    }
}

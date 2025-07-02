#version 330 core

uniform int fps;
uniform vec2 resolution;
uniform vec2 pixel;
uniform float time;
uniform bool mouse_active;
uniform vec2 mouse_position;

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

uniform int grey_index;
uniform int invert_index;
uniform int blur_index;
uniform int pixelate_index;
uniform int test_index;
uniform int gol_index;

uniform int blur_amount;
int blur_length = blur_amount * 2 + 1;
uniform float pixelate_amount;
uniform bool draw_background;
uniform bool gol_tick;
const vec4 on_colour = vec4(0.96, 0.95, 0.76, 1.0);
const vec4 off_colour = vec4(0.19, 0.16, 0.24, 1.0);

in vec2 uv;
vec2 uv_flipped = vec2(uv.x, 1.0 - uv.y);
out vec4 out_colour;

bool check_colour(vec4 colour) {
    vec4 difference = colour - on_colour;
    float absolute = abs(difference.r) + abs(difference.g) + abs(difference.b);
    return absolute < 0.015;
}

int get_current(vec2 offset) {
    return int(check_colour(texture(background, uv + pixel * offset))) | int(check_colour(texture(background_buffer, uv_flipped + pixel * offset)));
}

vec4 game_of_life() {
        int current = get_current(vec2(0.0));
        if (gol_tick) {
            int surround = -current;
            for (float i = -1.0; i < 2.0; i++) {
                for (float j = -1.0; j < 2.0; j++) {
                    surround += get_current(vec2(i, j));
                }
            }
            if (current == 1 && (surround < 1.5 || surround > 3.5)) {
                current = 0;
            } else if (current == 0 && (surround > 2.5 && surround < 3.5)) {
                current = 1;
            }
        }
        vec4 colour = vec4(mix(off_colour.rgb, on_colour.rgb, current), 1.0);
    return colour;
}

vec4 grey(sampler2D display_layer) {
    vec4 colour = texture(display_layer, uv);
    colour.rgb = vec3(colour.r * 0.2126 + colour.r * 0.7152 + colour.b * 0.0722);
    return colour;
}

vec4 invert(sampler2D display_layer) {
    vec4 colour = texture(display_layer, uv);
    colour = vec4(vec3(1.0) - colour.rgb, colour.a);
    return colour;
}

vec4 blur(sampler2D display_layer) {
    vec4 colour;
    for (float i = 0.0; i < blur_length; i++) {
            for (float j = 0.0; j < blur_length; j++) {
                colour += texture(display_layer, uv + pixel * (vec2(i, j) - blur_amount));
            }
        }
    colour /= pow(blur_length, 2.0);
    return colour;
}

vec4 pixelate(sampler2D display_layer) {
    float dx = pixelate_amount * pixel[0];
    float dy = pixelate_amount * pixel[1];
    vec4 colour = texture(display_layer, vec2(dx * ceil(uv.x / dx), dy * ceil(uv.y / dy)));
    return colour;
}

vec4 test(sampler2D display_layer) {
    vec4 colour;
//    vec4 colour = texture(display_layer, vec2(fract(uv.x * 3), fract(uv.y * 2)));  // tile effect
    if (mouse_active) {
        vec2 Z, R = vec2(2.0 + 1.0 * (mouse_position.x / resolution.x), 1.0 + 100.0 * mouse_position.x / resolution.x);  // mandelbrot effect
        for (colour *= 0.0; colour.a++ < 1e2 && dot(Z, Z) < 4.0;
             Z = (2 * uv - R.xy) / R.y + mat2(Z, -Z.y, Z.x) * Z);
        colour += colour.a / 1e2;
        colour = mix(off_colour, on_colour, colour.r);
    } else {
        colour = texture(display_layer, uv);
    }
    return colour;
}

vec4 gol(sampler2D display_layer) {
    vec4 colour = texture(display_layer, uv_flipped);
    return colour;
}

vec4 get_colour(sampler2D display_layer, int effect_index, vec4 out_colour) {
    vec4 colour;
    if (effect_index==grey_index) {
        colour = grey(display_layer);
    } else if (effect_index==invert_index) {
        colour = invert(display_layer);
    } else if (effect_index==blur_index) {
        colour = blur(display_layer);
    } else if (effect_index==pixelate_index) {
        colour = pixelate(display_layer);
    } else if (effect_index==test_index) {
        colour = test(display_layer);
    } else if (effect_index==gol_index) {
        colour = gol(display_layer);
    } else {
        colour = texture(display_layer, uv);
    }
    out_colour = mix(out_colour, colour, colour.a);
    return out_colour;
}

void main() {
    if (draw_background) {
        out_colour = game_of_life();
    } else {
        out_colour = vec4(0.0);
        if (background_effect==6) {
            out_colour = get_colour(background_buffer, background_effect, out_colour);
        } else {
            out_colour = get_colour(background, background_effect, out_colour);
        }
        out_colour = get_colour(level, level_effect, out_colour);
        out_colour = get_colour(steps, steps_effect, out_colour);
        out_colour = get_colour(map, map_effect, out_colour);
        out_colour = get_colour(level_editor, level_editor_effect, out_colour);
        out_colour = get_colour(menu, menu_effect, out_colour);
        out_colour = get_colour(ui, ui_effect, out_colour);
        out_colour = get_colour(transition, transition_effect, out_colour);
    }
}

#version 330 core

uniform int fps;
uniform vec2 resolution;
uniform vec2 pixel;
uniform float time;
uniform bool mouse_active;
uniform vec2 mouse_position;

const int effect_data_length = 5;
uniform sampler2D background_display;
uniform float background_effect[effect_data_length];
uniform sampler2D level_display;
uniform float level_effect[effect_data_length];
uniform sampler2D steps_display;
uniform float steps_effect[effect_data_length];
uniform sampler2D map_display;
uniform float map_effect[effect_data_length];
uniform sampler2D level_editor_display;
uniform float level_editor_effect[effect_data_length];
uniform sampler2D menu_display;
uniform float menu_effect[effect_data_length];
uniform sampler2D ui_display;
uniform float ui_effect[effect_data_length];
uniform sampler2D transition_display;
uniform float transition_effect[effect_data_length];
uniform sampler2D buffer_display;

uniform float grey_index;
uniform float invert_index;
uniform float blur_index;
uniform float pixelate_index;
uniform float test_index;
uniform float gol_index;

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
    return int(check_colour(texture(background_display, uv + pixel * offset))) |
    int(check_colour(texture(buffer_display, uv_flipped + pixel * offset)));
}

vec4 game_of_life() {
        int current = get_current(vec2(0.0));
        if (bool(background_effect[1])) {
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

vec4 grey(sampler2D display_layer, float effect[effect_data_length]) {
    vec4 colour = texture(display_layer, uv);
    colour.rgb = mix(colour.rgb, vec3(colour.r * 0.2126 + colour.r * 0.7152 + colour.b * 0.0722), effect[1]);
    return colour;
}

vec4 invert(sampler2D display_layer, float effect[effect_data_length]) {
    vec4 colour = texture(display_layer, uv);
//    colour = vec4(vec3(1.0) - colour.rgb, colour.a);  // add scale to invert colour, use mix function again...
    colour.rgb = mix(colour.rgb, vec3(1.0) - colour.rgb, effect[1]);
    return colour;
}

vec4 blur(sampler2D display_layer, float effect[effect_data_length]) {
    vec4 colour;
    for (float i = 0.0; i < int(effect[2]); i++) {
            for (float j = 0.0; j < int(effect[2]); j++) {
                colour += texture(display_layer, uv + pixel * (vec2(i, j) - int(effect[1])));
            }
        }
    colour /= pow(int(effect[2]), 2.0);
    return colour;
}

vec4 pixelate(sampler2D display_layer, float effect[effect_data_length]) {
    float dx = effect[1] * pixel[0];
    float dy = effect[1] * pixel[1];
    vec4 colour = texture(display_layer, vec2(dx * (floor(uv.x / dx) + 0.5), dy * (floor(uv.y / dy) + 0.5)));
    return colour;
}

vec4 test(sampler2D display_layer, float effect[effect_data_length]) {
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

vec4 gol(sampler2D display_layer, float effect[effect_data_length]) {
    vec4 colour = texture(display_layer, uv_flipped);
    return colour;
}

vec4 get_colour(sampler2D display_layer, float effect[effect_data_length], vec4 out_colour) {
    vec4 colour;
    if (effect[0]==grey_index) {
        colour = grey(display_layer, effect);
    } else if (effect[0]==invert_index) {
        colour = invert(display_layer, effect);
    } else if (effect[0]==blur_index) {
        colour = blur(display_layer, effect);
    } else if (effect[0]==pixelate_index) {
        colour = pixelate(display_layer, effect);
    } else if (effect[0]==test_index) {
        colour = test(display_layer, effect);
    } else if (effect[0]==gol_index) {
        colour = gol(display_layer, effect);
    } else {
        colour = texture(display_layer, uv);
    }
    out_colour = mix(out_colour, colour, colour.a);
    return out_colour;
}

void main() {
    if (background_effect[0]==gol_index && bool(background_effect[4])) {  // this doesnt work as intended, gol cells linger while gol effect is not selected...
        out_colour = game_of_life();
    } else {
        out_colour = vec4(0.0);
        if (background_effect[0]==gol_index) {
            out_colour = get_colour(buffer_display, background_effect, out_colour);
        } else {
            out_colour = get_colour(background_display, background_effect, out_colour);
        }
        out_colour = get_colour(level_display, level_effect, out_colour);
        out_colour = get_colour(steps_display, steps_effect, out_colour);
        out_colour = get_colour(map_display, map_effect, out_colour);
        out_colour = get_colour(level_editor_display, level_editor_effect, out_colour);
        out_colour = get_colour(menu_display, menu_effect, out_colour);
        out_colour = get_colour(ui_display, ui_effect, out_colour);
        out_colour = get_colour(transition_display, transition_effect, out_colour);
    }
}

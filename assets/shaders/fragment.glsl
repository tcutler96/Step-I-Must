#version 330 core

uniform int fps;
uniform vec2 resolution;
uniform vec2 aspect_ratio;
uniform vec2 pixel_size;
uniform float time;
uniform bool mouse_active;
uniform vec2 mouse_position;

#define effect_applied 0
#define effect_active 1
#define effect_scale 2
#define effect_current 4
#define effect_current_2 7

const int effect_data_length = 10;
uniform sampler2D background_display;
uniform float background_effect[effect_data_length];
uniform sampler2D level_background_display;
uniform float level_background_effect[effect_data_length];
uniform sampler2D level_main_display;
uniform float level_main_effect[effect_data_length];
uniform sampler2D level_player_display;
uniform float level_player_effect[effect_data_length];
uniform sampler2D level_ui_display;
uniform float level_ui_effect[effect_data_length];
uniform sampler2D level_map_display;
uniform float level_map_effect[effect_data_length];
uniform sampler2D ui_display;
uniform float ui_effect[effect_data_length];
uniform sampler2D transition_display;
uniform float transition_effect[effect_data_length];
uniform sampler2D buffer_display;

uniform float grey_index;
uniform float invert_index;
uniform float blur_index;
uniform float pixelate_index;
uniform float shockwave_index;
uniform float galaxy_index;
uniform float gol_index;
uniform float test_index;

const float pi = atan(1.0) * 4.0;
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
    return int(check_colour(texture(background_display, uv + pixel_size * offset))) |
    int(check_colour(texture(buffer_display, uv_flipped + pixel_size * offset)));
}

vec4 game_of_life() {
        int current = get_current(vec2(0.0));
        if (bool(background_effect[3])) {
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

vec4 grey(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = texture(display_layer, uv);
    colour.rgb = mix(colour.rgb, vec3(colour.r * 0.2126 + colour.g * 0.7152 + colour.b * 0.0722), effect_data[effect_scale]);
    return colour;
}

vec4 invert(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = texture(display_layer, uv);
    colour.rgb = mix(colour.rgb, vec3(1.0) - colour.rgb, effect_data[effect_scale]);
    return colour;
}

float gaussian(vec2 i, float sigma) {
    return 1.0 / (2.0 * pi * pow(sigma, 2)) * exp(-((pow(i.x, 2) + pow(i.y, 2)) / (2.0 * pow(sigma, 2))));
}

vec4 blur(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = vec4(0.0);
    float sigma = effect_data[effect_current] * 0.25;
    float accum = 0.0;
    vec2 offset;
    float weight;
    for (int x = -int(effect_data[effect_current]) / 2; x < int(effect_data[effect_current]) / 2; ++x) {
        for (int y = -int(effect_data[effect_current]) / 2; y < int(effect_data[effect_current]) / 2; ++y) {
            offset = vec2(x, y);
            weight = gaussian(offset, sigma);
            colour += texture(display_layer, uv + pixel_size * offset).rgba * weight;
            accum += weight;
        }
    }
    colour /= accum;
    return colour;
}

vec4 pixelate(sampler2D display_layer, float effect_data[effect_data_length]) {
    float pixel_width = effect_data[effect_current] * pixel_size[0];
    float pixel_height = effect_data[effect_current_2] * pixel_size[1];
    vec4 colour = texture(display_layer, vec2(pixel_width * (floor(uv.x / pixel_width) + 0.5), pixel_height * (floor(uv.y / pixel_height) + 0.5)));
    return colour;
}

float get_map(float magnitude, float scale, float effect_data[effect_data_length]) {
    float outer_map = 1.0 - smoothstep(effect_data[effect_scale] - effect_data[7], effect_data[effect_scale], magnitude);
    float inner_map = smoothstep(effect_data[effect_scale] - effect_data[7] * 2.0, effect_data[effect_scale] - effect_data[7], magnitude);
    float map = outer_map * inner_map;
    map *= smoothstep(0.0, 0.25, scale);
    map *= 1.0 - smoothstep(0.25, 1.0, scale);
    return map;
}

vec4 shockwave(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec2 direction = uv - vec2(effect_data[4], effect_data[5]) / resolution;
    float magnitude = length(direction * aspect_ratio);

    float map_r = get_map(magnitude, effect_data[effect_scale] + 0.02, effect_data);
    float map_g = get_map(magnitude, effect_data[effect_scale], effect_data);
    float map_b = get_map(magnitude, effect_data[effect_scale] - 0.02, effect_data);

    vec2 displacement_r = normalize(direction) * effect_data[6] * map_r;
    vec2 displacement_g = normalize(direction) * effect_data[6] * map_g;
    vec2 displacement_b = normalize(direction) * effect_data[6] * map_b;

    float colour_r = texture(display_layer, uv - displacement_r).r;
    float colour_g = texture(display_layer, uv - displacement_g).g;
    float colour_b = texture(display_layer, uv - displacement_b).b;

    vec4 colour = vec4(colour_r, colour_g, colour_b, texture(display_layer, uv - displacement_g).a);
    colour.rgb += map_g * 0.5;
    return colour;
}

float field(vec3 p, float s, int l) {
	float strength = 7.0 + 0.03 * log(1.e-6 + fract(sin(time) * 4373.11));
	float accum = s / 4.0;
	float prev = 0.0;
	float tw = 0.0;
	for (int i = 0; i < l; ++i) {
		float mag = dot(p, p);
		p = abs(p) / mag + vec3(-0.5, -0.4, -1.5);
		float w = exp(-float(i) / 7.0);
		accum += w * exp(-strength * pow(abs(mag - prev), 2.2));
		tw += w;
		prev = mag;
	}
	return max(0.0, 5.0 * accum / tw - 0.7);
}

vec3 nrand3(vec2 seed) {
	vec3 a = fract(cos(seed.x * 8.3e-3 + seed.y) * vec3(1.3e5, 4.7e5, 2.9e5));
	vec3 b = fract(sin(seed.x * 0.3e-3 + seed.y) * vec3(8.1e5, 1.0e5, 0.1e5));
	vec3 c = mix(a, b, 0.5);
	return c;
}

vec4 galaxy(sampler2D display_layer) {
	float freqs[4];
	freqs[0] = 0.5 + 0.5 * sin(time / 5);
	freqs[1] = 0.1 + 0.1 * sin(time / 5);
	freqs[2] = 0.5 + 0.5 * sin(time / 5);
	freqs[3] = 0.1 + 0.1 * sin(time / 5);

    vec2 uv = 2.0 * uv - 1.0;
	vec2 uvs = uv * aspect_ratio;
	vec3 p = vec3(uvs / 4.0, 0) + vec3(1.0, -1.3, 0.0);
	p += 0.2 * vec3(sin(time / 16.0), sin(time / 12.0),  sin(time / 128.0));

    // Galaxy
	float t = field(p, freqs[2], 20);
	float v = (1.0 - exp((abs(uv.x) - 1.0) * 6.0)) * (1.0 - exp((abs(uv.y) - 1.0) * 6.0));
    // Second Layer
	vec3 p2 = vec3(uvs / (4.0 + sin(time * 0.11) * 0.2 + 0.2 + sin(time * 0.15) * 0.3 + 0.4), 1.5) + vec3(2.0, -1.3, -1.0);
	p2 += 0.25 * vec3(sin(time / 16.0), sin(time / 12.0),  sin(time / 128.0));
	float t2 = field(p2, freqs[3], 15);
	vec4 c2 = mix(0.4, 1.0, v) * vec4(1.3 * t2 * t2 * t2 ,1.8  * t2 * t2, t2 * freqs[0], t2);

    // Stars
	vec2 seed = p.xy * 4.0;
	seed = floor(seed * resolution.x);
	vec3 rnd = nrand3(seed);
	vec4 starcolor = vec4(pow(rnd.y, 40.0));
	// Second Layer
	vec2 seed2 = p2.xy * 2.0;
	seed2 = floor(seed2 * resolution.x);
	vec3 rnd2 = nrand3(seed2);
	starcolor += vec4(pow(rnd2.y, 40.0));

	vec4 colour = mix(freqs[3]- 0.3, 1.0, v) * vec4(1.5 * freqs[2] * t * t * t, 1.2 * freqs[1] * t * t, freqs[3] * t, 1.0) + c2 + starcolor;
    return colour;
}

vec4 gol(sampler2D display_layer) {
    vec4 colour = texture(display_layer, uv_flipped);
    return colour;
}

uniform float influence = 1.0;
uniform float radius = 0.1;

const mat4 THRESHOLD_MATRIX = mat4(
		vec4(1.0 / 17.0,  9.0 / 17.0,  3.0 / 17.0, 11.0 / 17.0),
		vec4(13.0 / 17.0,  5.0 / 17.0, 15.0 / 17.0,  7.0 / 17.0),
		vec4(4.0 / 17.0, 12.0 / 17.0,  2.0 / 17.0, 10.0 / 17.0),
		vec4(16.0 / 17.0,  8.0 / 17.0, 14.0 / 17.0,  6.0 / 17.0));

vec4 test(sampler2D display_layer, float effect_data[effect_data_length]) {
//    vec4 colour = texture(display_layer, vec2(fract(uv.x * 4), fract(uv.y * 3)));  // tile effect

//    vec4 colour = texture(display_layer, uv);  // dithering, cool for lighting system...
//    vec2 uv = uv / pixel_size;
//	float distance = (clamp(1.0 - distance(uv, (mouse_position)) * pixel_size.x / radius, 0.0, 1.0)) * influence * (1.5 + 0.25 * abs(sin(time)));
//	colour.a *= step(0.0, THRESHOLD_MATRIX[int(uv.x) % 4][int(uv.y) % 4] - distance);

//    float amount = 0.0;
//	amount = (1.0 + sin(time * 6.0)) * 0.5;
//	amount *= 1.0 + sin(time * 16.0) * 0.5;
//	amount *= 1.0 + sin(time * 19.0) * 0.5;
//	amount *= 1.0 + sin(time * 27.0) * 0.5;
//	amount = pow(amount, 3.0);
//	amount *= 0.05;
//    vec4 colour;
//    colour.r = texture(display_layer, vec2(uv.x + amount, uv.y)).r;
//    colour.ga = texture(display_layer, uv).ga;
//    colour.b = texture(display_layer, vec2(uv.x - amount,uv.y)).b;
//	colour *= (1.0 - amount * 0.5);

//     apply chromatic abertation to the player when we are low on steps, needs to effect the pixels off the player...
    float cut_off = 0.75;
    float v = abs(sin(0.1 + time));
//    float v = texture(noise, uv * time).r;
    vec2 offset = v < cut_off ? vec2(0.0) : vec2(pow((v - cut_off) * 1 / (1.0 - cut_off), 2) * 0.005);
	vec4 colour = vec4(texture(display_layer, uv - offset * 2).r, texture(display_layer, uv).g, texture(display_layer, uv + offset * 2).b, texture(display_layer, uv).a);

//    vec4 colour = texture(display_layer, xy);

    return colour;
}

vec4 get_colour(sampler2D display_layer, float effect_data[effect_data_length], vec4 out_colour) {
    vec4 colour;
    if (effect_data[effect_active]==grey_index) {
        colour = grey(display_layer, effect_data);
    } else if (effect_data[effect_active]==invert_index) {
        colour = invert(display_layer, effect_data);
    } else if (effect_data[effect_active]==blur_index) {
        colour = blur(display_layer, effect_data);
    } else if (effect_data[effect_active]==pixelate_index) {
        colour = pixelate(display_layer, effect_data);
    } else if (effect_data[effect_active]==shockwave_index) {
        colour = shockwave(display_layer, effect_data);
    } else if (effect_data[effect_active]==galaxy_index) {
        colour = galaxy(display_layer);
    } else if (effect_data[effect_active]==gol_index) {
        colour = gol(display_layer);
    } else if (effect_data[effect_active]==test_index) {
        colour = test(display_layer, effect_data);
    } else {
        colour = texture(display_layer, uv);
    }
    out_colour = mix(out_colour, colour, colour.a);
    return out_colour;
}

void main() {
    if (background_effect[effect_applied]==gol_index && bool(background_effect[7])) {
        out_colour = game_of_life();
    } else {
        out_colour = vec4(0.0);
        if (background_effect[effect_applied]==gol_index) {
            out_colour = get_colour(buffer_display, background_effect, out_colour);
        } else {
            out_colour = get_colour(background_display, background_effect, out_colour);
        }
        out_colour = get_colour(level_background_display, level_background_effect, out_colour);
        out_colour = get_colour(level_main_display, level_main_effect, out_colour);
        out_colour = get_colour(level_player_display, level_player_effect, out_colour);
        out_colour = get_colour(level_ui_display, level_ui_effect, out_colour);
        out_colour = get_colour(level_map_display, level_map_effect, out_colour);
        out_colour = get_colour(ui_display, ui_effect, out_colour);
        out_colour = get_colour(transition_display, transition_effect, out_colour);

//        out_colour = get_colour(final_display, final_effect, out_colour);
//        out_colour.rgb = vec3(out_colour.r * 0.2126 + out_colour.g * 0.7152 + out_colour.b * 0.0722);
    }
}

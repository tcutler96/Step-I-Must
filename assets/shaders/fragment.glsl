#version 330 core

uniform int fps;
uniform vec2 resolution;
uniform vec2 aspect_ratio;
uniform vec2 pixel_size;
uniform float time;
uniform bool mouse_active;
uniform vec2 mouse_position;
uniform bool chromatic_aberration;
uniform bool crt;
uniform bool vignette;

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
uniform float chromatic_index;
uniform float shockwave_index;
uniform float galaxy_index;
uniform float ripple_index;
uniform float gol_index;
uniform float test_index;

#define effect_applied 0
#define effect_active 1
#define effect_scale 2
#define effect_current 4
#define effect_current_2 7

const vec4 gol_on_colour = vec4(0.96, 0.95, 0.76, 1.0);
const vec4 gol_off_colour = vec4(0.19, 0.16, 0.24, 1.0);

in vec2 uv;
vec2 uv_flipped = vec2(uv.x, 1.0 - uv.y);
out vec4 out_colour;

bool check_colour(vec4 colour) {
    vec4 difference = colour - gol_on_colour;
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
        vec4 colour = vec4(mix(gol_off_colour.rgb, gol_on_colour.rgb, current), 1.0);
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

vec4 blur(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = texture(display_layer, uv);
    return colour;
}

vec4 pixelate(sampler2D display_layer, float effect_data[effect_data_length]) {
    float pixelate_size = int(effect_data[effect_current]) * pixel_size[0];
    vec2 centre = pixelate_size * (floor(uv / pixelate_size) + 0.5);
    vec2 half_pixelate_size = pixelate_size * vec2(0.5);

    vec4 colour = 0.4 * texture(display_layer, centre);
    colour += 0.15 * texture(display_layer, centre + vec2(-half_pixelate_size.x, -half_pixelate_size.y));
    colour += 0.15 * texture(display_layer, centre + vec2(half_pixelate_size.x, -half_pixelate_size.y));
    colour += 0.15 * texture(display_layer, centre + vec2(half_pixelate_size.x, half_pixelate_size.y));
    colour += 0.15 * texture(display_layer, centre + vec2(-half_pixelate_size.x, half_pixelate_size.y));

    colour.rgb *= 1.0 - 0.5 * effect_data[effect_scale];
    return colour;
}

vec4 chromatic(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour;
    float shift = effect_data[effect_scale] * pixel_size.x;
    shift += 0.25 * shift * sin(time * 0.5);

    colour.r  = texture(display_layer, uv + vec2(shift)).r;
    colour.ga = texture(display_layer, uv).ga;
    colour.b  = texture(display_layer, uv + vec2(-shift)).b;
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

    float map_r = get_map(magnitude, effect_data[effect_scale] + 0.2, effect_data);
    float map_g = get_map(magnitude, effect_data[effect_scale], effect_data);
    float map_b = get_map(magnitude, effect_data[effect_scale] - 0.2, effect_data);

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
    return mix(a, b, 0.5);
}

vec4 galaxy(sampler2D display_layer) {
    float freqs[4];
    freqs[0] = 0.6 + 0.4 * sin(time / 4.0);
    freqs[1] = 0.15 + 0.1 * sin(time / 5.0);
    freqs[2] = 0.55 + 0.45 * sin(time / 6.0);
    freqs[3] = 0.12 + 0.08 * sin(time / 5.5);

    vec2 uv_scaled = 2.0 * uv - 1.0;
    vec2 uvs = uv_scaled * aspect_ratio;

    vec3 p = vec3(uvs / 4.0, 0) + vec3(1.0, -1.3, 0.0);
    p += 0.2 * vec3(sin(time / 16.0), sin(time / 12.0), sin(time / 128.0));

    float t = field(p, freqs[2], 20);
    // Second layer
    vec3 p2 = vec3(uvs / (4.0 + sin(time * 0.11) * 0.2 + 0.2 + sin(time * 0.15) * 0.3 + 0.4), 1.5) + vec3(2.0, -1.3, -1.0);
    p2 += 0.25 * vec3(sin(time / 16.0), sin(time / 12.0), sin(time / 128.0));
    float t2 = field(p2, freqs[3], 15);
    vec4 c2 = vec4(1.5 * t2 * t2 * t2, 1.9 * t2 * t2, 1.3 * t2 * freqs[0], 1.0);

    // Stars
    vec2 seed1 = floor(p.xy * 2.0 * resolution.x);
    vec3 rnd1 = nrand3(seed1);
    vec4 starcolor = vec4(pow(rnd1.y, 35.0));
    if (rnd1.x > 0.975) starcolor.rgb *= vec3(1.3, 1.0, 0.8);
    if (rnd1.x < 0.025) starcolor.rgb *= vec3(0.7, 0.9, 1.4);

    vec2 seed2 = floor(p2.xy * resolution.x);
    vec3 rnd2 = nrand3(seed2);
    starcolor += vec4(pow(rnd2.y, 35.0));

    vec4 colour = vec4(1.8 * freqs[2] * t * t * t + c2.r + starcolor.r, 1.4 * freqs[1] * t * t + c2.g + starcolor.g, 1.2 * freqs[3] * t + c2.b + starcolor.b, 1.0);

    // Slight gamma correction
    colour.rgb = pow(colour.rgb, vec3(0.88));

    return colour;
}

vec4 gol(sampler2D display_layer) {
    vec4 colour = texture(display_layer, uv_flipped);
    return colour;
}

const float ripple_life   = 2.5;
const float splash_life  = 0.5;
const float big_ripple_life    = 4.0;

float hash(float n) { return fract(sin(n) * 43758.5453); }
vec2 hash2(float n) { return vec2(hash(n * 1.13), hash(n * 7.77)); }

vec4 ripple(sampler2D display_layer) {
    // subtle whole-screen wobble
    vec2 distortedUV = uv;
    distortedUV += vec2(
        sin((uv.y + time * 0.2) * 20.0) * 0.002,
        cos((uv.x + time * 0.15) * 20.0) * 0.002
    );

    float brightnessMod = 0.0;
    vec2 totalRefraction = vec2(0.0);

    // main raindrops
    for (int i = 0; i < 10; i++) {
        float startPhase = hash(float(i) * 12.345) * ripple_life;
        float cycleTime = time + startPhase;
        float t = mod(cycleTime, ripple_life);
        float cycleIndex = floor(cycleTime / ripple_life);
        vec2 centre = hash2(float(i) + cycleIndex * 123.456);
        float speed = 0.15 + hash(float(i) + cycleIndex) * 0.10;
        float waveWidth = 0.006 + hash(float(i) + cycleIndex*2.0) * 0.005;
        float dist = length(uv - centre);
        float radius = t * speed;
        float edgeDist = abs(dist - radius);
        float ring = exp(-pow(edgeDist / waveWidth, 2.0)) * (1.0 - t / ripple_life);
        vec2 dir = normalize(uv - centre);
        totalRefraction += dir * ring * (0.015 + 0.008 * brightnessMod);
        brightnessMod += ring * 0.15;
    }

    // tiny splashes
    for (int i = 0; i < 20; i++) {
        float startTime = hash(float(i) * 91.3) * splash_life * 3.0;
        float t = mod(time + startTime, splash_life);
        float cycleIndex = floor((time + startTime) / splash_life);
        vec2 centre = hash2(float(i) + cycleIndex * 987.654);
        float dist = length(uv - centre);
        float splash = exp(-pow(dist / 0.01, 2.0)) * (1.0 - t / splash_life);
        vec2 dir = normalize(uv - centre);
        totalRefraction += dir * splash * 0.02;
        brightnessMod += splash * 0.05;
    }

    // occasional big drops
    for (int i = 0; i < 5; i++) {
        float startTime = hash(float(i) * 321.0) * big_ripple_life * 2.0;
        float t = mod(time + startTime, big_ripple_life);
        float cycleIndex = floor((time + startTime) / big_ripple_life);
        vec2 centre = hash2(float(i) + cycleIndex * 555.555);
        float dist = length(uv - centre);
        float radius = t * 0.12;
        float edgeDist = abs(dist - radius);
        float ring = exp(-pow(edgeDist / 0.015, 2.0)) * (1.0 - t / big_ripple_life);
        vec2 dir = normalize(uv - centre);
        totalRefraction += dir * ring * 0.03;
        brightnessMod += ring * 0.1;
    }

    distortedUV += totalRefraction;
    vec3 baseCol = texture(display_layer, distortedUV).rgb;
    baseCol += brightnessMod;
    vec4 colour = vec4(baseCol, 1.0);
    return colour;
}

uniform float influence = 1.0;
uniform float radius = 0.1;
const mat4 THRESHOLD_MATRIX = mat4(
		vec4(1.0 / 17.0,  9.0 / 17.0,  3.0 / 17.0, 11.0 / 17.0),
		vec4(13.0 / 17.0,  5.0 / 17.0, 15.0 / 17.0,  7.0 / 17.0),
		vec4(4.0 / 17.0, 12.0 / 17.0,  2.0 / 17.0, 10.0 / 17.0),
		vec4(16.0 / 17.0,  8.0 / 17.0, 14.0 / 17.0,  6.0 / 17.0));

#define MAX_RADIUS 2
#define DOUBLE_HASH 0
#define HASHSCALE1 .1031
#define HASHSCALE3 vec3(.1031, .1030, .0973)

float hash12(vec2 p) {
	vec3 p3 = fract(vec3(p.xyx) * HASHSCALE1);
    p3 += dot(p3, p3.yzx + 19.19);
    return fract((p3.x + p3.y) * p3.z);
}

vec2 hash22(vec2 p) {
	vec3 p3 = fract(vec3(p.xyx) * HASHSCALE3);
    p3 += dot(p3, p3.yzx+19.19);
    return fract((p3.xx+p3.yz)*p3.zy);
}

vec4 test(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = texture(display_layer, uv);  // dithering, cool for lighting system...
    vec2 uv = uv / pixel_size;
	float distance = (clamp(1.0 - distance(uv, (mouse_position)) * pixel_size.x / radius, 0.0, 1.0)) * influence * (1.5 + 0.25 * abs(sin(time)));
    float threshold = THRESHOLD_MATRIX[int(uv.x) % 4][int(uv.y) % 4];
    colour.a *= step(distance, threshold);
    return colour;
}

vec4 apply_crt(vec4 colour) {
    colour.g *= (sin(uv.y * resolution.y * 2.0) + 1.0) * 0.1 + 1.0;
    colour.rb *= (cos(uv.y * resolution.y * 2.0) + 1.0) * 0.1 + 1.0;
    return colour;
}

vec4 apply_vignette(vec4 colour) {
    float animation = 0.5 + 0.5 * sin(time * 0.75);
    float animated_border = 0.1 + 0.1 * animation;
    float animated_strength = 0.3 + 0.3 * (1.0 - animation);

    float dist_x = min(uv.x, 1.0 - uv.x);
    float dist_y = min(uv.y, 1.0 - uv.y);

    float fade_x = pow(smoothstep(0.0, animated_border * 0.75, dist_x), 3.0);
    float fade_y = pow(smoothstep(0.0, animated_border * 0.75, dist_y), 3.0);
    float rect_mask = fade_x * fade_y;
    float corner_dist = length(vec2(dist_x, dist_y));
    float round_mask = smoothstep(animated_border * 0.2, animated_border * 0.75, corner_dist);
    float vignette_mask = mix(rect_mask, round_mask, 0.5);

    vec3 tinted = mix(vec3(0.086, 0.051, 0.075), colour.rgb, vignette_mask);
    colour.rgb = mix(tinted, colour.rgb, 1.0 - animated_strength);
    return colour;
}

vec4 get_colour(sampler2D display_layer, float effect_data[effect_data_length], vec4 out_colour) {
    vec4 colour;
    if (effect_data[effect_active] == grey_index) colour = grey(display_layer, effect_data);
    else if (effect_data[effect_active] == invert_index) colour = invert(display_layer, effect_data);
    else if (effect_data[effect_active] == blur_index) colour = blur(display_layer, effect_data);
    else if (effect_data[effect_active] == pixelate_index) colour = pixelate(display_layer, effect_data);
    else if (effect_data[effect_active] == chromatic_index) colour = chromatic(display_layer, effect_data);
    else if (effect_data[effect_active] == shockwave_index) colour = shockwave(display_layer, effect_data);
    else if (effect_data[effect_active] == galaxy_index) colour = galaxy(display_layer);
    else if (effect_data[effect_active] == ripple_index) colour = ripple(display_layer);
    else if (effect_data[effect_active] == gol_index) colour = gol(display_layer);
    else if (effect_data[effect_active] == test_index) colour = test(display_layer, effect_data);
    else colour = texture(display_layer, uv);
    out_colour = mix(out_colour, colour, colour.a);
    return out_colour;
}

void main() {
    if (background_effect[effect_applied] == gol_index && bool(background_effect[7])) out_colour = game_of_life();
    else {
        out_colour = vec4(0.0);
        if (background_effect[effect_applied] == gol_index) out_colour = get_colour(buffer_display, background_effect, out_colour);
        else out_colour = get_colour(background_display, background_effect, out_colour);
        out_colour = get_colour(level_background_display, level_background_effect, out_colour);
        out_colour = get_colour(level_main_display, level_main_effect, out_colour);
        out_colour = get_colour(level_player_display, level_player_effect, out_colour);
        out_colour = get_colour(level_ui_display, level_ui_effect, out_colour);
        out_colour = get_colour(level_map_display, level_map_effect, out_colour);
        out_colour = get_colour(ui_display, ui_effect, out_colour);
        out_colour = get_colour(transition_display, transition_effect, out_colour);

        if (crt) out_colour = apply_crt(out_colour);
        if (vignette) out_colour = apply_vignette(out_colour);
    }
}

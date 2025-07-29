#version 330 core

uniform int fps;
uniform vec2 resolution;
uniform vec2 aspect_ratio;
uniform vec2 pixel_size;
uniform float time;
uniform bool mouse_active;
uniform vec2 mouse_position;

const int effect_data_length = 10;
uniform sampler2D background_display;
uniform float background_effect[effect_data_length];
uniform sampler2D level_background_display;
uniform float level_background_effect[effect_data_length];
uniform sampler2D level_display;
uniform float level_effect[effect_data_length];
uniform sampler2D player_display;
uniform float player_effect[effect_data_length];
uniform sampler2D level_text_display;
uniform float level_text_effect[effect_data_length];
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
uniform sampler2D noise;

uniform float grey_index;
uniform float invert_index;
uniform float blur_index;
uniform float pixelate_index;
uniform float shockwave_index;
uniform float test_index;
uniform float gol_index;

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

    // apply chromatic abertation to the level walls...
//    float cut_off = 0.75;
//    float v = abs(sin(0.1 + time));
////    float v = texture(noise, uv * time).r;
//    vec2 offset = v < cut_off ? vec2(0.0) : vec2(pow((v - cut_off) * 1 / (1.0 - cut_off), 2) * 0.005);
//	vec4 colour = vec4(texture(display_layer, uv - offset).r, texture(display_layer, uv).g, texture(display_layer, uv + offset).b, texture(display_layer, uv).a);

//    vec2 xy = uv;
////    xy.y += sin(5 + time) * 0.01 * effect_data[2];  // bounce up and down
//    xy.y += sin(xy.x * 5 + time) * 0.01 * effect_data[2];  // sin wave sway
//    vec4 colour = texture(display_layer, xy);

    vec4 colour = texture(display_layer, uv);
    colour.rgb = mix(colour.rgb, vec3(colour.r * 0.2126 + colour.g * 0.7152 + colour.b * 0.0722), effect_data[2]);
    return colour;
}

vec4 invert(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = texture(display_layer, uv);
    colour.rgb = mix(colour.rgb, vec3(1.0) - colour.rgb, effect_data[2]);
    return colour;
}

float gaussian(vec2 i, float sigma) {
    return 1.0 / (2.0 * pi * pow(sigma, 2)) * exp(-((pow(i.x, 2) + pow(i.y, 2)) / (2.0 * pow(sigma, 2))));
}

vec4 blur(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = vec4(0.0);
    float sigma = effect_data[4] * 0.25;
    float accum = 0.0;
    vec2 offset;
    float weight;
    for (int x = -int(effect_data[4]) / 2; x < int(effect_data[4]) / 2; ++x) {
        for (int y = -int(effect_data[4]) / 2; y < int(effect_data[4]) / 2; ++y) {
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
    float pixel_width = effect_data[4] * pixel_size[0];
    float pixel_height = effect_data[4] / 2 * pixel_size[1];
    vec4 colour = texture(display_layer, vec2(pixel_width * (floor(uv.x / pixel_width) + 0.5), pixel_height * (floor(uv.y / pixel_height) + 0.5)));
    return colour;
}

float get_map(float d, float t, float effect_data[effect_data_length]) {
    float outer_map = 1.0 - smoothstep(effect_data[2] - effect_data[7], effect_data[2], d);
    float inner_map = smoothstep(effect_data[2] - effect_data[7] * 2.0, effect_data[2] - effect_data[7], d);
    float map = outer_map * inner_map;
    map *= smoothstep(0.0, 0.25, t);
    map *= 1.0 - smoothstep(0.25, 1.0, t);
    return map;
}

vec4 shockwave(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec2 direction = uv - vec2(effect_data[4], effect_data[5]) / resolution;
    float d = length(direction * aspect_ratio);

    float map_r = get_map(d, effect_data[2] + 0.02, effect_data);
    float map_g = get_map(d, effect_data[2], effect_data);
    float map_b = get_map(d, effect_data[2] - 0.02, effect_data);

    vec2 displacement_r = normalize(direction) * effect_data[6] * map_r;
    vec2 displacement_g = normalize(direction) * effect_data[6] * map_g;
    vec2 displacement_b = normalize(direction) * effect_data[6] * map_b;

    float r = texture(display_layer, uv - displacement_r).r;
    float g = texture(display_layer, uv - displacement_g).g;
    float b = texture(display_layer, uv - displacement_b).b;

    vec4 colour = vec4(r, g, b, texture(display_layer, uv - displacement_g).a);
    colour.rgb += map_g * 0.5;
    return colour;
}

float field(vec3 p, float s) {
	float strength = 7. + .03 * log(1.e-6 + fract(sin(time) * 4373.11));
	float accum = s/4.;
	float prev = 0.;
	float tw = 0.;
	for (int i = 0; i < 26; ++i) {
		float mag = dot(p, p);
		p = abs(p) / mag + vec3(-.5, -.4, -1.5);
		float w = exp(-float(i) / 7.);
		accum += w * exp(-strength * pow(abs(mag - prev), 2.2));
		tw += w;
		prev = mag;
	}
	return max(0., 5. * accum / tw - .7);
}

float field2(vec3 p, float s) {
	float strength = 7. + .03 * log(1.e-6 + fract(sin(time) * 4373.11));
	float accum = s/4.;
	float prev = 0.;
	float tw = 0.;
	for (int i = 0; i < 18; ++i) {
		float mag = dot(p, p);
		p = abs(p) / mag + vec3(-.5, -.4, -1.5);
		float w = exp(-float(i) / 7.);
		accum += w * exp(-strength * pow(abs(mag - prev), 2.2));
		tw += w;
		prev = mag;
	}
	return max(0., 5. * accum / tw - .7);
}

vec3 nrand3( vec2 co ) {
	vec3 a = fract( cos( co.x*8.3e-3 + co.y )*vec3(1.3e5, 4.7e5, 2.9e5) );
	vec3 b = fract( sin( co.x*0.3e-3 + co.y )*vec3(8.1e5, 1.0e5, 0.1e5) );
	vec3 c = mix(a, b, 0.5);
	return c;
}

float field3(vec3 p) {
	float strength = 7. + .03 * log(1.e-6 + fract(sin(time) * 4373.11));
	float accum = 0.;
	float prev = 0.;
	float tw = 0.;
	for (int i = 0; i < 32; ++i) {
		float mag = dot(p, p);
		p = abs(p) / mag + vec3(-.5, -.4, -1.5);
		float w = exp(-float(i) / 7.);
		accum += w * exp(-strength * pow(abs(mag - prev), 2.3));
		tw += w;
		prev = mag;
	}
	return max(0., 5. * accum / tw - .7);
}

vec3 palette(float t, vec3 a, vec3 b, vec3 c, vec3 d ){
    return a + b * cos(6.28318 * (c * t + d));
}

vec3 palette2(float t) {
    return 0.5 + 0.5 * cos(6.28318 * (t + vec3(0.3, 0.416, 0.557)));
}

vec4 test(sampler2D display_layer, float effect_data[effect_data_length]) {
//    vec4 colour = texture(display_layer, vec2(fract(uv.x * 4), fract(uv.y * 3)));  // tile effect
//    vec4 colour = vec4(palette(uv.x + 0.1 * time, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.3, 0.416, 0.557)), 1.0);  // gradient
//    vec4 colour = vec4(palette(uv.x + 0.1 * time, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.3, 0.2, 0.2)), 1.0);  // gradient
    vec4 colour = vec4(palette(uv.y - 0.1 * time, vec3(0.5), vec3(0.5), vec3(1.0), vec3(0.3 * sin(time), 0.2, 0.2)), 1.0);  // gradient
//    vec4 colour = vec4(palette(uv.x + 0.1 * time, vec3(0.8, 0.5, 0.4), vec3(0.2, 0.4, 0.2), vec3(2.0, 1.0, 1.0), vec3(0.0, 0.25, 0.25)), 1.0);  // gradient
//    colour.rgb = colour.gbr;

//	vec2 uv = 2. * uv - 1.;  // galaxy fractal
//	vec2 uvs = uv * aspect_ratio;
//	vec3 p = vec3(uvs / 4., 0) + vec3(1., -1.3, 0.);
//	p += .2 * vec3(sin(time / 16.), sin(time / 12.),  sin(time / 128.));
//	float t = field3(p);
//	float v = (1. - exp((abs(uv.x) - 1.) * 6.)) * (1. - exp((abs(uv.y) - 1.) * 6.));
//	vec4 colour = mix(.4, 1., v) * vec4(1.8 * t * t * t, 1.4 * t * t, t, 1.0);

//    vec2 uv = 2. * uv - 1.;  // galaxy fractal
//	vec2 uvs = uv * aspect_ratio;
//	vec3 p = vec3(uvs / 4., 0) + vec3(1., -1.3, 0.);
//	p += .2 * vec3(sin(time / 16.), sin(time / 12.),  sin(time / 128.));
//
//	float freqs[4];
//	freqs[0] = 1.;  // colour, blue to green
//	freqs[1] = 0.5 * sin(time / 10);  // brightness/ pink shine
//	freqs[2] = 1.;  // similar to above but less
//	freqs[3] = 0.5 * sin(time);  // darkness, edges
//
//	float t = field(p,freqs[2]);
//	float v = (1. - exp((abs(uv.x) - 1.) * 6.)) * (1. - exp((abs(uv.y) - 1.) * 6.));
//
//    //Second Layer
//	vec3 p2 = vec3(uvs / (4.+sin(time*0.11)*0.2+0.2+sin(time*0.15)*0.3+0.4), 1.5) + vec3(2., -1.3, -1.);
//	p2 += 0.25 * vec3(sin(time / 16.), sin(time / 12.),  sin(time / 128.));
//	float t2 = field2(p2,freqs[3]);
//	vec4 c2 = mix(.4, 1., v) * vec4(1.3 * t2 * t2 * t2 ,1.8  * t2 * t2 , t2* freqs[0], t2);
//
//
//	//Let's add some stars
//	vec2 seed = p.xy * 2.0;
//	seed = floor(seed * resolution.x);
//	vec3 rnd = nrand3( seed );
//	vec4 starcolor = vec4(pow(rnd.y,40.0));
//
//	//Second Layer
//	vec2 seed2 = p2.xy * 2.0;
//	seed2 = floor(seed2 * resolution.x);
//	vec3 rnd2 = nrand3( seed2 );
//	starcolor += vec4(pow(rnd2.y,40.0));
//
//	vec4 colour = mix(freqs[3]-.3, 1., v) * vec4(1.5*freqs[2] * t * t * t , 1.2*freqs[1] * t * t, freqs[3]*t, 1.0)+c2+starcolor;
    return colour;
}

vec4 gol(sampler2D display_layer, float effect_data[effect_data_length]) {
    vec4 colour = texture(display_layer, uv_flipped);
    return colour;
}

vec4 get_colour(sampler2D display_layer, float effect_data[effect_data_length], vec4 out_colour) {
    vec4 colour;
    if (effect_data[1]==grey_index) {
        colour = grey(display_layer, effect_data);
    } else if (effect_data[1]==invert_index) {
        colour = invert(display_layer, effect_data);
    } else if (effect_data[1]==blur_index) {
        colour = blur(display_layer, effect_data);
    } else if (effect_data[1]==pixelate_index) {
        colour = pixelate(display_layer, effect_data);
    } else if (effect_data[1]==shockwave_index) {
        colour = shockwave(display_layer, effect_data);
    } else if (effect_data[1]==test_index) {
        colour = test(display_layer, effect_data);
    } else if (effect_data[1]==gol_index) {
        colour = gol(display_layer, effect_data);
    } else {
        colour = texture(display_layer, uv);
    }
    out_colour = mix(out_colour, colour, colour.a);
    return out_colour;
}

void main() {
    if (background_effect[0]==gol_index && bool(background_effect[7])) {
        out_colour = game_of_life();
    } else {
        out_colour = vec4(0.0);
        if (background_effect[0]==gol_index) {
            out_colour = get_colour(buffer_display, background_effect, out_colour);
        } else {
            out_colour = get_colour(background_display, background_effect, out_colour);
        }
        out_colour = get_colour(level_background_display, level_background_effect, out_colour);
        out_colour = get_colour(level_display, level_effect, out_colour);
        out_colour = get_colour(player_display, player_effect, out_colour);
        out_colour = get_colour(level_text_display, level_text_effect, out_colour);
        out_colour = get_colour(map_display, map_effect, out_colour);
        out_colour = get_colour(level_editor_display, level_editor_effect, out_colour);
        out_colour = get_colour(menu_display, menu_effect, out_colour);
        out_colour = get_colour(ui_display, ui_effect, out_colour);
        out_colour = get_colour(transition_display, transition_effect, out_colour);

//        out_colour = get_colour(final_display, final_effect, out_colour);
//        out_colour.rgb = vec3(out_colour.r * 0.2126 + out_colour.g * 0.7152 + out_colour.b * 0.0722);
    }
}

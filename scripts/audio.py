import pygame as pg


class Audio:
    def __init__(self, main):
        self.main = main
        self.mixer = pg.mixer
        self.mixer.set_num_channels(16)
        self.volume_adjustments = {'name of sound file': 'volume adjustment in the range 0-1', 'conveyor': 0.25, 'cutscene_dialogue': 2, 'ice': 0.5}
        # test change
        self.audio, self.music = self.load_audio()
        self.music_themes = {'main_menu': ['edgy_demo'], 'splash': ['edgy_demo'], 'level_editor': ['edgy_demo'], 'game': ['chill_idea'], 'current': None, 'index': 0}
        self.music_switching = False
        self.music_switch_fade = 2.5
        self.music_volume = self.get_volume(audio_type='music')
        self.music_volume_current = self.music_volume
        self.music_volume_step = 0.005
        self.missing_sounds = []

    def load_audio(self):
        audio = self.main.assets.audio
        for audio_type, audio_data in audio.items():
            for audio_name, audio_file in audio_data.items():
                sound_volume = self.get_volume(audio_type='sound')
                if audio_type == 'sound':
                    audio_file.set_volume(sound_volume * (self.volume_adjustments[audio_name] if audio_name in self.volume_adjustments else 1))
        music = self.mixer.music
        music.set_volume(self.get_volume(audio_type='music'))
        return audio, music

    def get_volume(self, audio_type):
        if audio_type in ['sound', 'music']:
            return self.main.assets.settings['audio'][audio_type + '_volume'] * self.main.assets.settings['audio']['master_volume']

    def play_sound(self, name, loops=0, fade=0, existing='overlap'):
        if name in self.audio['sound']:
            if existing == 'stop' and self.audio['sound'][name].get_num_channels():
                self.stop_sound(name=name, fade=0)
            elif not self.audio['sound'][name].get_num_channels() or existing == 'overlap':
                self.audio['sound'][name].play(loops=loops, fade_ms=self.main.utilities.s_to_ms(s=fade))
        elif self.main.testing:
            if name not in self.missing_sounds:
                print(f"'{name}' sound file not found...")
                self.missing_sounds.append(name)
            if not self.audio['sound']['placeholder'].get_num_channels():
                self.audio['sound']['placeholder'].play(loops=loops, fade_ms=self.main.utilities.s_to_ms(s=fade))

    def stop_sound(self, name, fade=1):
        if name in self.audio['sound']:
            self.audio['sound'][name].fadeout(self.main.utilities.s_to_ms(s=fade))

    def start_music(self, game_state=None, fade=1):
        if game_state:
            if game_state in self.music_themes and self.music_themes[game_state] != self.music_themes['current']:
                self.music_themes['current'] = self.music_themes[game_state]
                self.music_themes['index'] = 0
            else:
                return
        self.music.load(filename=self.audio['music'][self.music_themes['current'][self.music_themes['index']]]['path'])
        self.music.play(fade_ms=self.main.utilities.s_to_ms(s=fade))

    def stop_music(self, game_state=None, fade=1):
        if game_state:
            if game_state in self.music_themes and self.music_themes[game_state] != self.music_themes['current']:
                self.music_themes['current'] = None
                self.music_themes['index'] = 0
                self.music_switching = False
            else:
                return
        self.music.fadeout(self.main.utilities.s_to_ms(s=fade))

    def change_volume(self, audio_type):
        if audio_type in ['sound_volume', 'master_volume']:
            sound_volume = self.get_volume(audio_type='sound')
            for sound in self.audio['sound'].values():
                sound.set_volume(sound_volume * (self.volume_adjustments[sound] if sound in self.volume_adjustments else 1))
        if audio_type in ['music_volume', 'master_volume']:
            self.music_volume = self.get_volume(audio_type='music')

    def update(self):
        if self.music_themes['current']:
            if not self.music_switching:
                if self.music.get_pos() >= self.audio['music'][self.music_themes['current'][self.music_themes['index']]]['length'] - self.main.utilities.s_to_ms(s=self.music_switch_fade):
                    self.music_switching = True
                    self.stop_music(fade=self.music_switch_fade)
                    self.music_themes['index'] = (self.music_themes['index'] + 1) % len(self.music_themes['current'])
            elif not self.music.get_busy():
                self.music_switching = False
                self.start_music(fade=self.music_switch_fade)
        if self.music_volume_current != self.music_volume:
            self.music_volume_current += self.music_volume_step if self.music_volume_current < self.music_volume else -self.music_volume_step
            if abs(self.music_volume_current - self.music_volume) < self.music_volume_step:
                self.music_volume_current = self.music_volume
            if self.music_volume_current:
                self.music.set_volume(self.music_volume_current)


    def quit(self):
        self.mixer.fadeout(self.main.utilities.s_to_ms(s=1))
        self.music.fadeout(self.main.utilities.s_to_ms(s=1))

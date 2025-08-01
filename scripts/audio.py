import pygame as pg


class Audio:
    def __init__(self, main):
        self.main = main
        self.mixer = pg.mixer
        self.mixer.set_num_channels(16)
        self.audio, self.music = self.load_audio()
        self.music_theme = None
        self.music_volume = self.get_volume(audio_type='music')
        self.music_volume_current = self.music_volume
        self.music_volume_step = 0.005

    def load_audio(self):
        audio = self.main.assets.audio
        for audio_type, audio_data in audio.items():
            for audio_name, audio_file in audio_data.items():
                if audio_type == 'sound':
                    audio_file.set_volume(self.get_volume(audio_type='sound'))
        music = self.mixer.music
        music.set_volume(self.get_volume(audio_type='music'))
        return audio, music

    def get_volume(self, audio_type):
        if audio_type in ['sound', 'music']:
            return self.main.assets.settings['audio'][audio_type + '_volume'] * self.main.assets.settings['audio']['master_volume']

    def play_sound(self, name, loops=0, fade=0, overlap=False):
        if name in self.audio['sound']:
            if not self.audio['sound'][name].get_num_channels() or overlap:
                self.audio['sound'][name].play(loops=loops, fade_ms=self.main.utilities.s_to_ms(s=fade))
        elif self.main.testing:
            if not self.audio['sound']['placeholder'].get_num_channels():
                # print(f"'{name}' sound file not found...")
                self.audio['sound']['placeholder'].play(loops=loops, fade_ms=self.main.utilities.s_to_ms(s=fade))

    def stop_sound(self, name, fade=1):
        if name in self.audio['sound']:
            self.audio['sound'][name].fadeout(self.main.utilities.s_to_ms(s=fade))

    def play_music(self, music_theme=None, fade=10):
        if music_theme != self.music_theme and music_theme in self.audio['music']:
            self.music_theme = music_theme
            self.music.load(filename=self.audio['music'][self.music_theme])
            self.music.play(loops=-1, fade_ms=self.main.utilities.s_to_ms(s=fade))

    def stop_music(self, fade=1):
        self.music_theme = None
        self.music.fadeout(self.main.utilities.s_to_ms(s=fade))

    def change_volume(self, audio_type):
        if audio_type in ['sound_volume', 'master_volume']:
            for sound in self.audio['sound'].values():
                sound.set_volume(self.get_volume(audio_type='sound'))
        if audio_type in ['music_volume', 'master_volume']:
            self.music_volume = self.get_volume(audio_type='music')

    def update(self):
        if self.music_volume_current != self.music_volume:
            self.music_volume_current += self.music_volume_step if self.music_volume_current < self.music_volume else -self.music_volume_step
            if abs(self.music_volume_current - self.music_volume) < self.music_volume_step:
                self.music_volume_current = self.music_volume
            if self.music_volume_current:
                self.music.set_volume(self.music_volume_current)


    def quit(self):
        self.mixer.fadeout(self.main.utilities.s_to_ms(s=1))
        self.music.fadeout(self.main.utilities.s_to_ms(s=1))

import pygame as pg


class Audio:
    def __init__(self, main):
        self.main = main
        self.mixer = pg.mixer
        self.mixer.set_num_channels(16)
        self.volume_adjustments = {'name of sound file': 'volume adjustment in the range 0-1', 'conveyor': 0.25, 'cutscene_dialogue': 2}
        self.audio, self.music = self.load_audio()
        self.music_themes = {'main_menu': ['edgy_demo'], 'splash': ['edgy_demo'], 'level_editor': ['edge_demo'], 'game': ['chill_idea']}
        self.music_theme = None
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

    def play_sound(self, name, loops=0, fade=0, overlap=False):
        if name in self.audio['sound']:
            if not self.audio['sound'][name].get_num_channels() or overlap:
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

    def start_music(self, game_state=None, fade=5):
        if not self.music_theme and game_state in self.music_themes:
            self.music_theme = self.music_themes[game_state]
            self.music.load(filename=self.audio['music'][self.music_theme[0]])
            # if theres only 1 music for the current game state then just play the music track with -1 loops
            # else play the first music theme with no loop and then queue the next one, we then need to detect when the music changes in order the queue the next theme...
            self.music.play(loops=-1, fade_ms=self.main.utilities.s_to_ms(s=fade))
            # test queing up a music track, how does it sound at the end, start one track and set pos to near the end and queue up another
            # get list of music themes, play the first one, need to add functionality for looping over list of music themes...
            # check if music theme is not already being played...
            # this can be handled in transition class when we trigger a new game state, either stop current music theme (ie set to None) or leave current music theme playing...
            print(self.music_theme)

    def stop_music(self, game_state=None, fade=5):
        if game_state in self.music_themes and self.music_theme != self.music_themes[game_state][0]:
            self.music_theme = None
            self.music.fadeout(self.main.utilities.s_to_ms(s=fade))

    def change_volume(self, audio_type):
        if audio_type in ['sound_volume', 'master_volume']:
            sound_volume = self.get_volume(audio_type='sound')
            for sound in self.audio['sound'].values():
                sound.set_volume(sound_volume * (self.volume_adjustments[sound] if sound in self.volume_adjustments else 1))
        if audio_type in ['music_volume', 'master_volume']:
            self.music_volume = self.get_volume(audio_type='music')

    def update(self):
        if self.main.events.check_key('space'):
            print(self.music.get_pos())
        if self.music_volume_current != self.music_volume:
            self.music_volume_current += self.music_volume_step if self.music_volume_current < self.music_volume else -self.music_volume_step
            if abs(self.music_volume_current - self.music_volume) < self.music_volume_step:
                self.music_volume_current = self.music_volume
            if self.music_volume_current:
                self.music.set_volume(self.music_volume_current)


    def quit(self):
        self.mixer.fadeout(self.main.utilities.s_to_ms(s=1))
        self.music.fadeout(self.main.utilities.s_to_ms(s=1))

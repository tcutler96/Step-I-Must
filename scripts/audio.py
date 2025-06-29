import pygame as pg


class Audio:
    def __init__(self, main):
        self.main = main
        pg.mixer.set_num_channels(16)
        self.audio = self.load_audio()
        self.mixer = pg.mixer
        self.music = self.mixer.music
        self.music_theme = None
        self.music.set_volume(self.get_volume(audio_type='music'))

    def load_audio(self):
        audio = self.main.assets.audio
        for audio_type, audio_data in audio.items():
            for audio_name, audio_file in audio_data.items():
                if audio_type == 'sound':
                    audio_file.set_volume(self.get_volume(audio_type='sound'))
        return audio

    def get_fade_ms(self, fade):
        return int(fade * 1000)

    def get_volume(self, audio_type):
        if audio_type in ['sound', 'music']:
            return self.main.assets.settings['audio'][audio_type + '_volume'] * self.main.assets.settings['audio']['master_volume']

    def play_sound(self, name, loops=0, fade=0):
        if name in self.audio['sound']:
            self.audio['sound'][name].play(loops=loops, fade_ms=self.get_fade_ms(fade=fade))

    def stop_sound(self, name, fade=0):
        if name in self.audio['sound']:
            if fade:
                self.audio['sound'][name].fadeout(self.get_fade_ms(fade=fade))
            else:
                self.audio['sound'][name].stop()

    def play_music(self, music_theme=None, fade=1):
        if music_theme != self.music_theme and music_theme in self.audio['music']:
            self.music_theme = music_theme
            self.music.load(filename=self.audio['music'][self.music_theme])
            self.music.play(loops=-1, fade_ms=self.get_fade_ms(fade=fade))

    def stop_music(self, fade=1):
        self.music_theme = None
        self.music.fadeout(self.get_fade_ms(fade=fade))


    def switch_music(self, music_theme=None, fade=1):
        # fade music out as soon as we start transition to new game state/ music theme
        # set music end event to be picked up by events handler
        # load and play new music theme with a fadein...
        print(0)
        # maybe we redo this whole system, play music theme when we enter a game state (triggered at transition middle and game state start up)
        # triggering a game state transition fades out current music theme (same length as transition)
        # entering a new game state (startup function) fades in new music them (same length as transition)
        if music_theme != self.music_theme:
            print(1)
            if self.music_theme:
                print(2)
                self.music.fadeout(fade * 1000)
                self.music.set_endevent(self.main.events.custom_events['music_end'])
                self.update_music_theme(music_theme=music_theme)
            else:
                print(3)
                self.update_music_theme(music_theme=music_theme)
                self.play_music(fade=fade)

    def update_music_theme(self, music_theme):
        self.music_theme = music_theme if music_theme in self.audio['music'] else None


    def update_volume(self, name, value):
        music = False
        sound = False
        if name == 'master' and value != self.audio_settings['master_volume']:
            self.audio_settings['master_volume'] = value
            music = True
            sound = True
        elif name == 'music' and value != self.audio_settings['music_volume']:
            self.audio_settings['music_volume'] = value
            music = True
        elif name == 'sound' and value != self.audio_settings['sound_volume']:
            self.audio_settings['sound_volume'] = value
            sound = True
        self.update_volume(music, sound)

    def update(self):
        pass
        # if self.main.events.check_key()

        # if self.main.events.check_key(key='m'):
        #     self.play_music = not self.play_music
        #     if self.play_music:
        #         # self.music.play(loops=-1, fade_ms=5000)
        #         self.audio['music']['main_menu'].play(fade_ms=5000)
        #     else:
        #         # self.music.fadeout(5000)
        #         self.audio['music']['main_menu'].fadeout(5000)



    def quit(self):  # fade out all active sounds...
        self.mixer.fadeout(1000)






















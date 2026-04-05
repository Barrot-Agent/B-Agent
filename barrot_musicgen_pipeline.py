import os
import musicgen

class BarrotMusicGenPipeline:
    def __init__(self, music_gen_config):
        self.music_gen_config = music_gen_config
        self.music_gen = musicgen.MusicGen(music_gen_config)

    def generate_music(self, prompt):
        music = self.music_gen.create(prompt)
        return music

    def save_music(self, music, output_path):
        with open(output_path, 'wb') as file:
            file.write(music)
        print(f"Music saved to {output_path}")

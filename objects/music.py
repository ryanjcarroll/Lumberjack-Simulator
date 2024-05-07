import random

class MusicPlayer:
    def __init__(self, sound_manager):
        # initialize variables
        self.sound_manager = sound_manager
        self.played_music_files = []
        self.unplayed_music_files = []

        # Load all music files using the sound asset manager
        self.load_music_files()

    def load_music_files(self):
        # Get the paths of all music files from the sound asset manager
        self.unplayed_music_files = self.sound_manager.sounds["music"]

    def play_random_song(self):
        # If there are no unplayed songs left, reload the music files
        if not self.unplayed_music_files:
            self.unplayed_music_files = self.played_music_files

        # Pick a random song from the unplayed songs list
        song = random.choice(self.unplayed_music_files)
        song.play()

        # Remove the played song from the unplayed songs list
        self.played_music_files.append(song)
        self.unplayed_music_files.remove(song)

    def stop_music(self):
        # Stop the music using the sound asset manager
        self.sound_manager.stop_music()
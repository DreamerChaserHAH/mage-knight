import pygame

def play_audio_clip(file_path, channel=1):
    # Load the audio file
    pygame.mixer.music.load(file_path)
    
    # Play the audio file
    pygame.mixer.Channel(channel).play(pygame.mixer.Sound(file_path))
    
def play_background_music(file_path):
    # Load the audio file
    pygame.mixer.music.load(file_path)
    
    # Play the audio file in an infinite loop
    pygame.mixer.Channel(0).play(pygame.mixer.Sound(file_path), loops=-1)


# Example usage
if __name__ == "__main__":
    play_audio_clip("path_to_your_audio_file.mp3")
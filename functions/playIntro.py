import vlc
import time
from .getDefault import get_default


def play_intro():
    player = vlc.MediaPlayer(f'{get_default()}/voiceActivatedAssistant/roboIntro.wav')
    player.play()
    time.sleep(3)

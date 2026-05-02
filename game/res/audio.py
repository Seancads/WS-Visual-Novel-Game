import os
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(BASE_DIR, "assets", "sounds")

SFX_HOVER = None
SFX_CLICK = None
MUSIC_MENU = None
MUSIC_GAME = None
_initialized = False
_current_music = None


def init_audio():
    """Initialize mixer and load sound assets from assets/sounds."""
    global SFX_HOVER, SFX_CLICK, MUSIC_MENU, MUSIC_GAME, _initialized
    if _initialized:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.set_volume(0.40)
    except Exception as e:
        print("audio.init_audio: mixer.init failed:", e)
        return

    def load_sound(fn):
        p = os.path.join(SOUNDS_DIR, fn)
        if not os.path.exists(p):
            return None
        try:
            return pygame.mixer.Sound(p)
        except Exception:
            return None

    SFX_HOVER = load_sound("hover.mp3")
    SFX_CLICK = load_sound("click.mp3")

    menu_path = os.path.join(SOUNDS_DIR, "menu.mp3")
    MUSIC_MENU = menu_path if os.path.exists(menu_path) else None
    game_path = os.path.join(SOUNDS_DIR, "game.mp3")
    MUSIC_GAME = game_path if os.path.exists(game_path) else None

    _initialized = True


def play_sfx(name: str):
    try:
        if name == "hover" and SFX_HOVER:
            SFX_HOVER.play()
        elif name == "click" and SFX_CLICK:
            SFX_CLICK.play()
    except Exception:
        pass


def play_music(name: str, loop: bool = True):
    """Play a music track, but only restart if it's different from the current one."""
    global _current_music

    # If the same music is already playing, do nothing
    if name == _current_music and pygame.mixer.music.get_busy():
        return

    try:
        # Choose the file path based on name
        if name == "menu" and MUSIC_MENU:
            filepath = MUSIC_MENU
        elif name == "game" and MUSIC_GAME:
            filepath = MUSIC_GAME
        else:
            return  # unknown or missing track

        # If some music is playing, fade it out before loading a new one
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(300)

        pygame.mixer.music.load(filepath)
        pygame.mixer.music.play(-1 if loop else 0)
        _current_music = name
    except Exception:
        pass


def stop_music():
    """Stop music and reset the current track tracker."""
    global _current_music
    try:
        pygame.mixer.music.stop()
        _current_music = None
    except Exception:
        pass
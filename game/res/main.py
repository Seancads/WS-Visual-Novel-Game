import pygame
import sys
import json
import os
from menus import MainMenu, ChapterSelect
from gameplay import GameplayScene
import audio

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None
        self.current_scene_name = ""
        self.menu_anim_t = 0.0

    def add_scene(self, name, scene):
        self.scenes[name] = scene

    def change(self, name, **kwargs):
        if name in self.scenes:
            self.current_scene_name = name
            self.current_scene = self.scenes[name]
            if hasattr(self.current_scene, 'enter'):
                self.current_scene.enter(**kwargs)

    def update(self):
        self.menu_anim_t += 0.04
        if self.current_scene and hasattr(self.current_scene, 'update'):
            self.current_scene.update(self.menu_anim_t)

    def draw(self):
        if self.current_scene and hasattr(self.current_scene, 'draw'):
            self.current_scene.draw(self.menu_anim_t)

def load_config():
    config_path = resource_path("config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    pygame.init()
    try:
        audio.init_audio()
    except Exception:
        pass

    config = load_config()
    pygame.display.set_caption(config.get("title", "Game"))

    try:
        icon_path = resource_path("assets/icon.ico")
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    except Exception as e:
        print(f"Could not load icon: {e}")

    screen = pygame.display.set_mode((config["screen_width"], config["screen_height"]))
    pygame.display.set_caption(config["title"])
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)

    scene_manager = SceneManager()

    main_menu = MainMenu(screen, clock, font, scene_manager)
    scene_manager.add_scene("main_menu", main_menu)

    chapter_sel = ChapterSelect(screen, clock, font, scene_manager, config)
    scene_manager.add_scene("chapter_select", chapter_sel)

    gameplay = GameplayScene(screen, clock, font, scene_manager, config)
    scene_manager.add_scene("gameplay", gameplay)

    scene_manager.change("main_menu")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if scene_manager.current_scene:
                scene_manager.current_scene.handle_event(event)
        scene_manager.update()
        scene_manager.draw()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
import pygame
import sys
import math
import random
import os
from pygame.locals import *
from save import load_save
from theme import *
import audio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_IMG = os.path.join(BASE_DIR, "assets", "images")

def _load_icon(filename, size, invert=False):
    try:
        path = os.path.join(ASSET_IMG, filename)
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        if invert:
            img = _invert_alpha_image(img)
        return img
    except Exception:
        return None

def _invert_alpha_image(surface):
    arr = pygame.surfarray.pixels3d(surface).copy()
    arr[:] = 255 - arr
    new = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    new_arr = pygame.surfarray.pixels3d(new)
    new_arr[:] = arr
    del new_arr
    alpha = pygame.surfarray.pixels_alpha(surface).copy()
    alpha_new = pygame.surfarray.pixels_alpha(new)
    alpha_new[:] = alpha
    del alpha_new
    return new

def _load_menu_bg():
    try:
        path = os.path.join(ASSET_IMG, "menu.png")
        img = pygame.image.load(path).convert_alpha()
        w = int(SCREEN_W * 1.05)
        h = int(SCREEN_H * 1.05)
        img = pygame.transform.smoothscale(img, (w, h))
        max_dx = w - SCREEN_W
        max_dy = h - SCREEN_H
        return img, max_dx, max_dy
    except Exception:
        return None, 0, 0

def _load_star_icon(size):
    try:
        path = os.path.join(ASSET_IMG, "star.png")
        img = pygame.image.load(path).convert_alpha()
        img = pygame.transform.smoothscale(img, size)
        return img
    except Exception:
        return None

def draw_gradient_bg(surface):
    h = surface.get_height()
    w = surface.get_width()
    for y in range(h):
        t = y / h
        r = int(C_BG_TOP[0] + (C_BG_BOTTOM[0] - C_BG_TOP[0]) * t)
        g = int(C_BG_TOP[1] + (C_BG_BOTTOM[1] - C_BG_TOP[1]) * t)
        b = int(C_BG_TOP[2] + (C_BG_BOTTOM[2] - C_BG_TOP[2]) * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (w, y))

def draw_panel(surface, rect, alpha=230, border_color=None, radius=None):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((*C_PANEL_BG, alpha))
    surface.blit(panel, rect.topleft)
    bc = border_color or C_PANEL_BORDER
    r = radius if radius is not None else BORDER_RADIUS
    pygame.draw.rect(surface, bc, rect, 2, border_radius=r)

def draw_text_centered(surface, text, font, color, cx, cy):
    surf = font.render(text, True, color)
    surface.blit(surf, (cx - surf.get_width() // 2, cy - surf.get_height() // 2))
    return surf

def make_font(size, bold=False):
    try:
        return pygame.font.SysFont("Arial", size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)

def draw_star_row(surface, star_img, x, y, filled, total=3, size=24, gap=4):
    if star_img is None:
        font = make_font(size + 4)
        for i in range(total):
            star_num = total - i
            col = C_STAR_ON if filled >= star_num else C_STAR_OFF
            s = font.render("★", True, col)
            surface.blit(s, (x + i * (size + gap), y))
        return
    for i in range(total):
        star_num = total - i
        if filled >= star_num:
            sx = x + i * (size + gap)
            # Scale the star image to the desired size
            scaled_star = pygame.transform.smoothscale(star_img, (size, size))
            # Collected star: draw normally
            surface.blit(scaled_star, (sx, y))
        # Uncollected stars are invisible (not drawn)

class Button:
    def __init__(self, rect, text, callback,
                 color=None, hover_color=None, icon=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color or C_BTN_DEFAULT
        self.hover_color = hover_color or C_BTN_HOVER
        self.icon = icon
        self.hovered = False
        self._scale = 1.0
        self._target = 1.0

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            prev = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            self._target = 1.04 if self.hovered else 1.0
            if self.hovered and not prev:
                try: audio.play_sfx('hover')
                except Exception: pass
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._scale = 0.96
                try: audio.play_sfx('click')
                except Exception: pass
                self.callback()
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self._target = 1.04 if self.hovered else 1.0

    def update(self):
        self._scale += (self._target - self._scale) * 0.18

    def draw(self, surface, font):
        self.update()
        cx, cy = self.rect.center
        w = int(self.rect.width * self._scale)
        h = int(self.rect.height * self._scale)
        r = pygame.Rect(cx - w // 2, cy - h // 2, w, h)

        sr = r.move(3, 3)
        shadow = pygame.Surface((sr.width, sr.height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 70))
        surface.blit(shadow, sr.topleft)

        col = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, col, r, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, C_PANEL_BORDER, r, 2, border_radius=BORDER_RADIUS)

        lbl = font.render(self.text, True, C_TEXT_PRIMARY)
        if self.icon:
            ih = min(h - 14, self.icon.get_height())
            iw = int(self.icon.get_width() * (ih / self.icon.get_height()))
            ico = pygame.transform.smoothscale(self.icon, (iw, ih))
            total_w = ico.get_width() + 10 + lbl.get_width()
            ix = r.centerx - total_w // 2
            iy = r.centery - ih // 2
            surface.blit(ico, (ix, iy))
            surface.blit(lbl, (ix + ico.get_width() + 10,
                               r.centery - lbl.get_height() // 2))
        else:
            surface.blit(lbl, (r.centerx - lbl.get_width() // 2,
                               r.centery - lbl.get_height() // 2))

class MainMenu:
    def __init__(self, screen, clock, font, scene_manager):
        self.screen = screen
        self.clock = clock
        self.font = font
        self.scene_manager = scene_manager
        self._bg, self._bg_dx, self._bg_dy = _load_menu_bg()
        self._play_icon = _load_icon("play.png", (28, 28), invert=True)
        self._build()

    def _build(self):
        cx = self.screen.get_width() // 2
        btn_w = 380
        self.buttons = [
            Button((cx - btn_w // 2, 400, btn_w, BTN_H_LG), "PLAY",
                lambda: self.scene_manager.change("chapter_select"),
                color=C_BTN_SAFE, hover_color=C_BTN_SAFE_H,
                icon=self._play_icon),
            Button((cx - btn_w // 2, 480, btn_w, BTN_H_LG), "EXIT",
                sys.exit,
                color=C_BTN_DANGER, hover_color=C_BTN_DANGER_H),
        ]

    def enter(self, **_):
        try: audio.play_music("menu")
        except Exception: pass

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self, t):
        pass

    def draw(self, t):
        w = self.screen.get_width()
        h = self.screen.get_height()
        if self._bg:
            dx = int((math.sin(t * 0.25) + 1) / 2 * self._bg_dx)
            dy = int((math.cos(t * 0.25) + 1) / 2 * self._bg_dy)
            self.screen.blit(self._bg, (-dx, -dy))
            vg = pygame.Surface((w, h), pygame.SRCALPHA)
            vg.fill((8, 12, 26, 165))
            self.screen.blit(vg, (0, 0))
            vig = pygame.Surface((w, h), pygame.SRCALPHA)
            for i in range(20):
                alpha = 30 - i
                rct = pygame.Rect(i*5, i*5, w - i*10, h - i*10)
                pygame.draw.rect(vig, (0, 0, 0, alpha), rct, 50)
            self.screen.blit(vig, (0, 0))
        else:
            draw_gradient_bg(self.screen)

        card_w, card_h = 700, 225
        card = pygame.Rect(w // 2 - card_w // 2, 150, card_w, card_h)
        draw_panel(self.screen, card, alpha=200, radius=12)
        pygame.draw.rect(self.screen, C_ACCENT, card.inflate(4, 4), 2, border_radius=13)

        pulse = 0.88 + 0.12 * math.sin(t)
        title_font = make_font(FS_TITLE, bold=True)

        glow_shades = [
            (int(C_ACCENT[0]*0.4), int(C_ACCENT[1]*0.3), 0),
            (int(C_ACCENT[0]*0.6), int(C_ACCENT[1]*0.45), 0),
            (int(C_ACCENT[0]*0.8), int(C_ACCENT[1]*0.6), 0),
            (int(C_ACCENT[0]*pulse), int(C_ACCENT[1]*pulse*0.75), 0)
        ]
        for idx, off in enumerate([4,3,2,1]):
            shade = glow_shades[idx]
            glow_col = (min(255, shade[0]), min(255, shade[1]), shade[2])
            gs = title_font.render("ECHOES OF VALOR", True, glow_col)
            self.screen.blit(gs, (w // 2 - gs.get_width() // 2 + off,
                                225 - gs.get_height() // 2 + off))

        title_surf = title_font.render("ECHOES OF VALOR", True, C_ACCENT)
        self.screen.blit(title_surf,
                        (w // 2 - title_surf.get_width() // 2,
                        225 - title_surf.get_height() // 2))

        rule_y = 280
        line_w = 240
        pygame.draw.line(self.screen, C_ACCENT_DIM, (w//2 - line_w, rule_y), (w//2 - 40, rule_y), 2)
        pygame.draw.line(self.screen, C_ACCENT_DIM, (w//2 + 40, rule_y), (w//2 + line_w, rule_y), 2)
        diamond = [(w//2, rule_y-4), (w//2+4, rule_y), (w//2, rule_y+4), (w//2-4, rule_y)]
        pygame.draw.polygon(self.screen, C_ACCENT, diamond)

        sub_font = make_font(FS_SMALL)
        draw_text_centered(self.screen,
                        "A Visual Novel About Brotherhood and Sacrifice",
                        sub_font, C_TEXT_SECONDARY, w // 2, 320)

        for b in self.buttons:
            b.draw(self.screen, self.font)

        ver_font = make_font(FS_TINY)
        ver_surf = ver_font.render("v1.0", True, (*C_TEXT_SECONDARY, 120))
        self.screen.blit(ver_surf, (w - ver_surf.get_width() - 14,
                                    h - ver_surf.get_height() - 10))

        pygame.display.flip()

class ChapterSelect:
    def __init__(self, screen, clock, font, scene_manager, config):
        self.screen = screen
        self.clock = clock
        self.font = font
        self.scene_manager = scene_manager
        self.config = config

        self._bg, self._bg_dx, self._bg_dy = _load_menu_bg()
        self._particles = []
        self._particle_timer = 0.0

        self.items = []
        self.item_w = 700
        self.item_h = 120
        self.item_gap = 12
        self.start_y = 100
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0
        self.max_scroll_y = 0

        self._return_icon = _load_icon("return.png", (22, 22), invert=True)
        self._lock_icon = _load_icon("lock.png", (28, 28), invert=True)
        self._star_img = _load_star_icon((22, 22))

        self.back_btn = Button(
            (40, self.screen.get_height() - 78, 150, BTN_H_SM), "BACK",
            lambda: scene_manager.change("main_menu"),
            color=C_BTN_BACK, hover_color=C_BTN_BACK_H,
            icon=self._return_icon)

    def _build_list(self):
        self.items.clear()
        chapters = self.config["chapters"]
        item_w = self.item_w
        item_h = self.item_h
        gap = self.item_gap
        start_x = (self.screen.get_width() - item_w) // 2

        for i, ch in enumerate(chapters):
            x = start_x
            y = self.start_y + i * (item_h + gap)
            rect = pygame.Rect(x, y, item_w, item_h)

            ch_id = ch["id"]
            locked = ch_id > self.save["chapter_unlocked"]

            cb = lambda cid=ch_id: self.scene_manager.change("gameplay", chapter_id=cid)
            self.items.append({
                "rect": rect,
                "chapter": ch,
                "locked": locked,
                "cb": cb,
                "hover": False,
                "scale": 1.0,
                "target_scale": 1.0,
            })

        total_height = self.start_y * 2 + len(chapters) * item_h + (len(chapters) - 1) * gap
        self.max_scroll_y = max(0, total_height - self.screen.get_height())
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0

    def enter(self, **_):
        self.save = load_save()
        if "chapter_unlocked" not in self.save:
            self.save["chapter_unlocked"] = 1
        self._build_list()
        try: audio.play_music("menu")
        except Exception: pass

    def handle_event(self, event):
        self.back_btn.handle_event(event)

        if event.type == MOUSEWHEEL:
            self.target_scroll_y -= event.y * 40
            self.target_scroll_y = max(0, min(self.target_scroll_y, self.max_scroll_y))

        for item in self.items:
            moved_rect = item["rect"].move(0, -self.scroll_y)
            if event.type == MOUSEMOTION:
                item["hover"] = moved_rect.collidepoint(event.pos)
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if moved_rect.collidepoint(event.pos) and not item["locked"]:
                    item["cb"]()
                    return

    def update(self, t):
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * 0.12

        self._particle_timer += 0.016
        if self._particle_timer > 0.05:
            self._particle_timer = 0
            if len(self._particles) < 50:
                self._particles.append({
                    "pos": [random.randint(0, self.screen.get_width()), -10],
                    "speed": random.uniform(0.4, 1.2),
                    "size": random.randint(2, 5),
                    "alpha": random.randint(60, 160)
                })
        new_particles = []
        for p in self._particles:
            p["pos"][1] += p["speed"]
            if p["pos"][1] < self.screen.get_height() + 20:
                new_particles.append(p)
        self._particles = new_particles

        self.back_btn.update()
        for item in self.items:
            item["target_scale"] = 1.03 if item["hover"] and not item["locked"] else 1.0
            item["scale"] += (item["target_scale"] - item["scale"]) * 0.15

    def draw(self, t):
        w, h = self.screen.get_width(), self.screen.get_height()

        if self._bg:
            dx = int((math.sin(t * 0.25) + 1) / 2 * self._bg_dx)
            dy = int((math.cos(t * 0.25) + 1) / 2 * self._bg_dy)
            self.screen.blit(self._bg, (-dx, -dy))
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((8, 12, 26, 170))
            self.screen.blit(overlay, (0, 0))
        else:
            draw_gradient_bg(self.screen)

        for p in self._particles:
            col = (180, 200, 255, p["alpha"])
            surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, col, (p["size"], p["size"]), p["size"])
            self.screen.blit(surf, p["pos"])

        for item in self.items:
            rect = item["rect"].move(0, -self.scroll_y)
            if rect.bottom < 0 or rect.top > h:
                continue

            scale = item["scale"]
            cx, cy = rect.center
            new_w = int(rect.width * scale)
            new_h = int(rect.height * scale)
            scaled_rect = pygame.Rect(cx - new_w//2, cy - new_h//2, new_w, new_h)

            shadow = scaled_rect.move(3, 3).inflate(6, 6)
            shadow_surf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
            shadow_surf.fill((0,0,0,90))
            self.screen.blit(shadow_surf, shadow.topleft)

            draw_panel(self.screen, scaled_rect, alpha=220,
                       border_color=C_ACCENT if item["hover"] and not item["locked"] else C_PANEL_BORDER,
                       radius=12)

            ch = item["chapter"]
            text_x = scaled_rect.left + 16
            text_y = scaled_rect.top + 12
            title_f = make_font(FS_BODY, bold=True)
            title_s = title_f.render(ch["title"], True, C_TEXT_PRIMARY)
            self.screen.blit(title_s, (text_x, text_y + 20))

            desc_f = make_font(FS_TINY)
            scenario_count = len(ch.get("scenarios", []))
            desc = f"{scenario_count} scenario{'s' if scenario_count>1 else ''}"
            desc_s = desc_f.render(desc, True, C_TEXT_SECONDARY)
            self.screen.blit(desc_s, (text_x, text_y + 50))

            # Stars earned for this chapter (if any)
            ch_id_str = str(ch["id"])
            completed_chapters = self.save.get("completed_chapters", {})
            if ch_id_str in completed_chapters:
                stars = completed_chapters[ch_id_str]["stars"]
                star_size = 44
                total_w = 3 * star_size + 4 * 2
                sx = scaled_rect.right - total_w
                sy = scaled_rect.centery - star_size//2
                draw_star_row(self.screen, self._star_img, sx, sy, stars, total=3, size=star_size, gap=-8)

            if item["locked"]:
                lock_overlay = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
                lock_overlay.fill((0,0,0,130))
                self.screen.blit(lock_overlay, scaled_rect.topleft)
                if self._lock_icon:
                    lx = scaled_rect.centerx - self._lock_icon.get_width()//2
                    ly = scaled_rect.centery - self._lock_icon.get_height()//2
                    self.screen.blit(self._lock_icon, (lx+275, ly-10))
                lock_f = make_font(FS_SMALL, bold=True)
                lock_s = lock_f.render("LOCKED", True, C_TEXT_PRIMARY)
                self.screen.blit(lock_s, (scaled_rect.centerx - lock_s.get_width()//2+275,
                                          scaled_rect.centery + 10))

        hdr = pygame.Rect(-10, 0, w + 20, 90)
        draw_panel(self.screen, hdr, alpha=255, border_color=C_PANEL_BORDER)
        title_font = make_font(FS_HEADING, bold=True)
        draw_text_centered(self.screen, "CHAPTERS", title_font, C_ACCENT, w//2, 45)

        self.back_btn.draw(self.screen, self.font)
        pygame.display.flip()


class LevelSelect:
    def __init__(self, screen, clock, font, scene_manager, config):
        self.screen = screen
        self.clock = clock
        self.font = font
        self.scene_manager = scene_manager
        self.config = config
        self.chapter_id = None
        self.chapter_title = ""

        # Background & particles
        self._bg, self._bg_dx, self._bg_dy = _load_menu_bg()
        self._particles = []
        self._particle_timer = 0.0

        # Vertical list layout
        self.items = []
        self.item_w = 700
        self.item_h = 100
        self.item_gap = 12
        self.start_y = 120
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0
        self.max_scroll_y = 0

        # Icons
        self._star_img = _load_star_icon((22, 22))
        self._return_icon = _load_icon("return.png", (22, 22), invert=True)
        self._lock_icon = _load_icon("lock.png", (24, 24), invert=True)

        self.back_btn = Button(
            (40, self.screen.get_height() - 78, 150, BTN_H_SM), "BACK",
            lambda: scene_manager.change("chapter_select"),
            color=C_BTN_BACK, hover_color=C_BTN_BACK_H,
            icon=self._return_icon)

    def enter(self, chapter_id, **_):
        self.chapter_id = chapter_id
        self.save = load_save()
        chapter = next(ch for ch in self.config["chapters"] if ch["id"] == chapter_id)
        self.chapter_title = chapter["title"]
        self._build_list(chapter)
        try: audio.play_music("menu")
        except Exception: pass

    def _build_list(self, chapter):
        self.items.clear()
        levels = chapter["levels"]
        item_w = self.item_w
        item_h = self.item_h
        gap = self.item_gap
        start_x = (self.screen.get_width() - item_w) // 2

        for i, lvl in enumerate(levels):
            x = start_x
            y = self.start_y + i * (item_h + gap)
            rect = pygame.Rect(x, y, item_w, item_h)

            lvl_id = lvl["id"]
            key = f"{self.chapter_id}-{lvl_id}"
            completed = key in self.save["completed_levels"]
            stars = self.save["completed_levels"][key]["stars"] if completed else 0

            if i == 0:
                locked = False
            else:
                prev_key = f"{self.chapter_id}-{chapter['levels'][i-1]['id']}"
                if prev_key not in self.save["completed_levels"]:
                    locked = True
                else:
                    prev_s = self.save["completed_levels"][prev_key]["stars"]
                    locked = prev_s < lvl.get("required_prev_stars", 0)

            if locked:
                cb = lambda: None
            else:
                cb = lambda lid=lvl_id: self.scene_manager.change(
                    "gameplay", chapter_id=self.chapter_id, level_id=lid
                )

            self.items.append({
                "rect": rect,
                "level": lvl,
                "stars": stars if completed else -1,
                "locked": locked,
                "cb": cb,
                "hover": False,
                "scale": 1.0,
                "target_scale": 1.0
            })

        total_height = self.start_y * 2 + len(levels) * item_h + (len(levels) - 1) * gap
        self.max_scroll_y = max(0, total_height - self.screen.get_height())
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0

    def handle_event(self, event):
        self.back_btn.handle_event(event)

        if event.type == MOUSEWHEEL:
            self.target_scroll_y -= event.y * 40
            self.target_scroll_y = max(0, min(self.target_scroll_y, self.max_scroll_y))

        for item in self.items:
            moved_rect = item["rect"].move(0, -self.scroll_y)
            if event.type == MOUSEMOTION:
                item["hover"] = moved_rect.collidepoint(event.pos)
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                if moved_rect.collidepoint(event.pos):
                    if not item["locked"]:
                        item["cb"]()
                    return   # consume event

    def update(self, t):
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * 0.12

        # Particles
        self._particle_timer += 0.016
        if self._particle_timer > 0.04:
            self._particle_timer = 0
            if len(self._particles) < 40:
                self._particles.append({
                    "pos": [random.randint(0, self.screen.get_width()), -10],
                    "speed": random.uniform(0.4, 1.0),
                    "size": random.randint(2, 4),
                    "alpha": random.randint(40, 130)
                })
        new_particles = []
        for p in self._particles:
            p["pos"][1] += p["speed"]
            if p["pos"][1] < self.screen.get_height() + 20:
                new_particles.append(p)
        self._particles = new_particles

        self.back_btn.update()
        for item in self.items:
            item["target_scale"] = 1.03 if item["hover"] and not item["locked"] else 1.0
            item["scale"] += (item["target_scale"] - item["scale"]) * 0.15

    def draw(self, t):
        w, h = self.screen.get_width(), self.screen.get_height()

        # Background
        if self._bg:
            dx = int((math.sin(t * 0.25) + 1) / 2 * self._bg_dx)
            dy = int((math.cos(t * 0.25) + 1) / 2 * self._bg_dy)
            self.screen.blit(self._bg, (-dx, -dy))
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill((8, 12, 26, 170))
            self.screen.blit(overlay, (0, 0))
        else:
            draw_gradient_bg(self.screen)

        # Particles
        for p in self._particles:
            col = (180, 200, 255, p["alpha"])
            surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, col, (p["size"], p["size"]), p["size"])
            self.screen.blit(surf, p["pos"])

        # Header
        hdr = pygame.Rect(0, 0, w, 90)
        draw_panel(self.screen, hdr, alpha=220, border_color=C_PANEL_BORDER)
        pygame.draw.rect(self.screen, C_ACCENT, (0, 0, 6, 90))
        title_font = make_font(FS_HEADING, bold=True)
        draw_text_centered(self.screen, self.chapter_title, title_font, C_ACCENT, w//2, 45)

        # Level list items
        for item in self.items:
            rect = item["rect"].move(0, -self.scroll_y)
            if rect.bottom < 0 or rect.top > h:
                continue

            scale = item["scale"]
            cx, cy = rect.center
            new_w = int(rect.width * scale)
            new_h = int(rect.height * scale)
            scaled_rect = pygame.Rect(cx - new_w//2, cy - new_h//2, new_w, new_h)

            # Shadow
            shadow = scaled_rect.move(3, 3).inflate(4, 4)
            shadow_surf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
            shadow_surf.fill((0,0,0,90))
            self.screen.blit(shadow_surf, shadow.topleft)

            # Card background
            draw_panel(self.screen, scaled_rect, alpha=210,
                       border_color=C_ACCENT if item["hover"] and not item["locked"] else C_PANEL_BORDER,
                       radius=12)

            lvl = item["level"]
            # Level number & title
            lvl_num_f = make_font(FS_SMALL, bold=True)
            lvl_num = f"Level {lvl['id']}"
            num_s = lvl_num_f.render(lvl_num, True, C_ACCENT_DIM)
            self.screen.blit(num_s, (scaled_rect.left + 16, scaled_rect.top + 12))

            title_f = make_font(FS_BODY, bold=True)
            title_s = title_f.render(lvl["title"], True, C_TEXT_PRIMARY)
            self.screen.blit(title_s, (scaled_rect.left + 16, scaled_rect.top + 36))

            # Required stars hint (only if locked)
            if item["locked"]:
                req = lvl.get("required_prev_stars", 0)
                hint_f = make_font(FS_TINY)
                hint_s = hint_f.render(f"Need {req} star{'s' if req>1 else ''} in previous", True, C_TEXT_SECONDARY)
                self.screen.blit(hint_s, (scaled_rect.left + 16, scaled_rect.top + 58))

            # Star rating (right side)
            if item["stars"] >= 0:
                star_size = 22
                gap = 4
                total_w = 3 * star_size + 2 * gap
                sx = scaled_rect.right - total_w - 20
                sy = scaled_rect.centery - star_size//2
                draw_star_row(self.screen, self._star_img,
                              sx, sy, item["stars"], total=3,
                              size=star_size, gap=gap)

            # Lock overlay
            if item["locked"]:
                lock_overlay = pygame.Surface(scaled_rect.size, pygame.SRCALPHA)
                lock_overlay.fill((0,0,0,110))
                self.screen.blit(lock_overlay, scaled_rect.topleft)
                if self._lock_icon:
                    lx = scaled_rect.centerx - self._lock_icon.get_width()//2
                    ly = scaled_rect.centery - self._lock_icon.get_height()//2 - 8
                    self.screen.blit(self._lock_icon, (lx, ly))
                    lock_f = make_font(FS_SMALL, bold=True)
                    lock_s = lock_f.render("LOCKED", True, C_TEXT_PRIMARY)
                    self.screen.blit(lock_s, (scaled_rect.centerx - lock_s.get_width()//2, ly + 28))

        self.back_btn.draw(self.screen, self.font)
        pygame.display.flip()
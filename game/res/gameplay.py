import os
import pygame
import random
import audio
from pygame.locals import MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from save import load_save, save_game
from menus import (Button, draw_gradient_bg, draw_panel,
                   draw_text_centered, make_font, draw_star_row,
                   _load_icon, _load_star_icon)
from theme import *

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets", "images")

PANEL_BOTTOM_MARGIN = 80
PANEL_HEIGHT        = 120
PANEL_H_PAD         = 40
PANEL_V_PAD         = 8
CHOICE_GAP          = 14
CHOICE_H            = BTN_H_SM


class IconButton:
    def __init__(self, rect, icon, callback,
                 color=None, hover_color=None):
        self.rect = pygame.Rect(rect)
        self.icon = icon
        self.callback = callback
        self.color = color or C_BTN_DEFAULT
        self.hover_color = hover_color or C_BTN_HOVER
        self.hovered = False
        self._scale = 1.0
        self._target = 1.0

    def handle_event(self, event):
        if event.type == MOUSEMOTION:
            prev = self.hovered
            self.hovered = self.rect.collidepoint(event.pos)
            self._target = 1.06 if self.hovered else 1.0
            if self.hovered and not prev:
                try:
                    audio.play_sfx('hover')
                except Exception:
                    pass
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._scale = 0.94
                try:
                    audio.play_sfx('click')
                except Exception:
                    pass
                self.callback()
        elif event.type == MOUSEBUTTONUP and event.button == 1:
            self._target = 1.06 if self.hovered else 1.0

    def update(self):
        self._scale += (self._target - self._scale) * 0.18

    def draw(self, surface, _=None):
        self.update()
        cx, cy = self.rect.center
        r = self.rect.inflate(
            self.rect.width * (self._scale - 1),
            self.rect.height * (self._scale - 1)
        )
        r.center = (cx, cy)

        shadow = r.move(2, 2)
        shadow_surf = pygame.Surface((shadow.width, shadow.height), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 60))
        surface.blit(shadow_surf, shadow.topleft)

        col = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, col, r, border_radius=BORDER_RADIUS)
        pygame.draw.rect(surface, C_PANEL_BORDER, r, 2, border_radius=BORDER_RADIUS)

        if self.icon:
            icon_size = min(r.width, r.height) - 10
            icon_w = int(self.icon.get_width() * icon_size / self.icon.get_height())
            icon_surf = pygame.transform.smoothscale(self.icon, (icon_w, icon_size))
            ix = r.centerx - icon_surf.get_width() // 2
            iy = r.centery - icon_surf.get_height() // 2
            surface.blit(icon_surf, (ix, iy))


class GameplayScene:
    def __init__(self, screen, clock, font, scene_manager, config):
        self.screen            = screen
        self.clock             = clock
        self.font              = font
        self.scene_manager     = scene_manager
        self.config            = config
        self.chapter_id        = None
        self.chapter_data      = None
        self.scenarios         = []
        self.scenario_index    = 0
        self.attempts          = 0
        self.sequence          = []
        self.sequence_index    = 0
        self.in_choices        = False
        self.typing_target     = ""
        self.typing_index      = 0
        self.typing_done       = True
        self.typing_speed      = 2
        self.choice_buttons    = []
        self.shuffled_choices  = []
        self.failure_text      = ""
        self.failure_timer     = 0
        self.state             = "playing"
        self.stars_earned      = 0
        self.arrow_visible     = True
        self.arrow_timer       = 0
        self.paused            = False
        self.pause_btn         = None
        self.play_btn          = None
        self.resume_btn        = None
        self.menu_btn          = None
        self.player_image      = None
        self.player_border     = False
        self.char_images       = {}
        self.char_borders      = {}
        self.char_text_colors  = {}
        self.background_image  = None
        self.panel_rect        = pygame.Rect(0, 0, 0, 0)
        self.fade_alpha        = 0
        self.fade_direction    = 0
        self.post_choice_type  = None
        self._pause_icon       = _load_icon("pause.png",  (24, 24), invert=True)
        self._play_icon        = _load_icon("play.png",   (24, 24), invert=True)
        self._return_icon      = _load_icon("return.png", (24, 24), invert=True)
        self._star_img         = _load_star_icon((22, 22))

    def enter(self, chapter_id):
        self.chapter_id = chapter_id
        chapter = next(ch for ch in self.config["chapters"] if ch["id"] == chapter_id)
        self.chapter_data = chapter
        self.scenarios = chapter["scenarios"]
        self.scenario_index = 0
        self.attempts = 0
        self.state = "playing"
        self.paused = False
        self.post_choice_type = None
        self.char_images = {}
        self.char_borders = {}
        self.char_text_colors = {}

        panel_w = int(SCREEN_W * 1.10)
        panel_x = (SCREEN_W - panel_w) // 2
        panel_y = SCREEN_H - PANEL_HEIGHT - PANEL_BOTTOM_MARGIN
        self.panel_rect = pygame.Rect(panel_x, panel_y, panel_w, PANEL_HEIGHT)

        self.fade_alpha = 0
        self.fade_direction = 0
        self._load_images(chapter)
        self._prepare_scenario()
        self._init_hud_buttons()

        try:
            audio.play_music("game")
        except Exception:
            pass

    def _load_images(self, chapter):
        img, border = self._load_or_placeholder("player.png", (300, 440))
        self.player_image = img
        self.player_border = border
        for cid, info in chapter.get("characters", {}).items():
            img, border = self._load_or_placeholder(info["image"], (300, 440))
            self.char_images[cid] = img
            self.char_borders[cid] = border
            self.char_text_colors[cid] = (
                tuple(info["text_color"]) if "text_color" in info
                else C_TEXT_PRIMARY)

    def _load_or_placeholder(self, filename, size):
        try:
            path = os.path.join(ASSET_DIR, filename)
            img  = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size), False
        except Exception:
            return None, False

    def _load_background(self, filename):
        if not filename:
            return None
        try:
            path = os.path.join(ASSET_DIR, filename)
            img  = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (SCREEN_W, SCREEN_H))
        except Exception:
            return None

    def _init_hud_buttons(self):
        btn_size = 44
        margin   = 14

        self.pause_btn = IconButton(
            (SCREEN_W - btn_size - margin, margin, btn_size, btn_size),
            self._pause_icon, self._toggle_pause,
            color=C_BTN_BACK, hover_color=C_BTN_BACK_H)

        cx, cy = SCREEN_W // 2, SCREEN_H // 2
        self.resume_btn = Button(
            (cx - 160, cy - 10, 320, BTN_H_LG), "RESUME",
            self._toggle_pause,
            color=C_BTN_SAFE, hover_color=C_BTN_SAFE_H,
            icon=self._play_icon)
        self.menu_btn = Button(
            (cx - 160, cy + 76, 320, BTN_H_LG), "MAIN MENU",
            lambda: self.scene_manager.change("main_menu"),
            color=C_BTN_DANGER, hover_color=C_BTN_DANGER_H)

    def _toggle_pause(self):
        self.paused = not self.paused

    def _prepare_scenario(self):
        scenario = self.scenarios[self.scenario_index]
        self.sequence = scenario.get("sequence", [])
        self.sequence_index = 0
        self.in_choices = (len(self.sequence) == 0)
        self.typing_target = ""
        self.typing_index = 0
        self.typing_done = True
        self.post_choice_type = None
        self.background_image = self._load_background(scenario.get("background_image"))
        if not self.in_choices:
            self._start_typing()
        else:
            self._build_choices()

    def _start_typing(self):
        if self.sequence_index < len(self.sequence):
            self.typing_target = self.sequence[self.sequence_index]["text"]
            self.typing_index = 0
            self.typing_done = False
        else:
            self.typing_target = ""
            self.typing_done = True

    def _build_choices(self):
        choices = list(self.scenarios[self.scenario_index]["choices"])
        random.shuffle(choices)
        self.shuffled_choices = choices
        self.choice_buttons = []
        n = len(choices)
        if n == 0:
            self.in_choices = True
            return
        self.in_choices = True
        max_w = self.panel_rect.width - PANEL_H_PAD * 2
        btn_w = max(180, min(320, (max_w - CHOICE_GAP * (n - 1)) // n))
        total = n * btn_w + CHOICE_GAP * (n - 1)
        sx = SCREEN_W // 2 - total // 2
        y = self.panel_rect.bottom + 16
        for i, ch in enumerate(choices):
            x = sx + i * (btn_w + CHOICE_GAP)
            self.choice_buttons.append(Button(
                (x, y, btn_w, CHOICE_H), ch["text"],
                self._make_choice_cb(i),
                color=C_CHOICE_DEFAULT, hover_color=C_CHOICE_HOVER))

    def _make_choice_cb(self, idx):
        def cb():
            if not self.in_choices or self.paused:
                return
            self.attempts += 1
            choice = self.shuffled_choices[idx]
            is_correct = choice.get("correct", False)

            if is_correct:
                seq = choice.get("pre_success_sequence")
                if seq:
                    self._start_post_choice_seq(seq, "success")
                else:
                    self.fade_direction = 1
            else:
                seq = choice.get("pre_failure_sequence")
                self.failure_text = choice.get("failure_text", "Wrong choice!")
                if seq:
                    self._start_post_choice_seq(seq, "failure")
                else:
                    self.state = "failure"
                    self.failure_timer = 130
        return cb

    def _start_post_choice_seq(self, seq, post_type):
        self.post_choice_type = post_type
        self.sequence = list(seq)
        self.sequence_index = 0
        self.in_choices = False
        self.typing_done = True
        self._start_typing()

    def _advance_sequence(self):
        if self.sequence_index + 1 < len(self.sequence):
            self.sequence_index += 1
            self._start_typing()
        else:
            if self.post_choice_type:
                self._handle_post_choice_end()
            else:
                self.in_choices = True
                self._build_choices()

    def _handle_post_choice_end(self):
        if self.post_choice_type == "success":
            self.post_choice_type = None
            self.fade_direction = 1
        elif self.post_choice_type == "failure":
            self.state = "failure"
            self.failure_timer = 130
            self.post_choice_type = None

    def _complete_chapter(self):
        self.post_choice_type = None
        n = len(self.scenarios)
        if   self.attempts <= n:          stars = 3
        elif self.attempts <= int(n*1.5): stars = 2
        elif self.attempts <= int(n*2.5): stars = 1
        else:                             stars = 0
        self.stars_earned = stars

        save = load_save()
        if "chapter_unlocked" not in save:
            save["chapter_unlocked"] = 1
        key = str(self.chapter_id)
        completed = save.get("completed_chapters", {})
        prev = completed.get(key)
        if not prev or stars > prev["stars"] or (
                stars == prev["stars"] and self.attempts < prev["best_attempts"]):
            completed[key] = {"stars": stars, "best_attempts": self.attempts}
            save["completed_chapters"] = completed

        next_ch = next((ch for ch in self.config["chapters"] if ch["id"] == self.chapter_id + 1), None)
        if next_ch:
            req = next_ch.get("required_prev_stars", 0)
            if stars >= req:
                save["chapter_unlocked"] = max(save["chapter_unlocked"], self.chapter_id + 1)

        save_game(save)
        self.state = "complete"

    def handle_event(self, event):
        if self.state == "complete":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.scene_manager.change("chapter_select")
            return

        self.pause_btn.handle_event(event)

        if self.paused:
            self.resume_btn.handle_event(event)
            self.menu_btn.handle_event(event)
            return
        if self.state == "failure":
            return
        if not self.in_choices:
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    or event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN):
                self._handle_dialogue_advance()
        else:
            for btn in self.choice_buttons:
                btn.handle_event(event)

    def _handle_dialogue_advance(self):
        if not self.typing_done:
            self.typing_index = len(self.typing_target)
            self.typing_done = True
        else:
            if self.in_choices:
                return
            self._advance_sequence()

    def update(self, t=0):
        if self.state == "failure":
            self.failure_timer -= 1
            if self.failure_timer <= 0:
                self.state = "playing"
                self.failure_text = ""
                self._build_choices()
                return

        if self.fade_direction == 1:
            self.fade_alpha += 8
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.post_choice_type = None
                if self.scenario_index + 1 < len(self.scenarios):
                    self.scenario_index += 1
                    self._prepare_scenario()
                else:
                    self._complete_chapter()
                self.fade_direction = -1
        elif self.fade_direction == -1:
            self.fade_alpha -= 8
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_direction = 0

        if (self.state == "playing" and not self.paused
                and not self.in_choices and not self.typing_done):
            self.typing_index += self.typing_speed
            if self.typing_index >= len(self.typing_target):
                self.typing_index = len(self.typing_target)
                self.typing_done = True

        self.arrow_timer += 1
        if self.arrow_timer >= 28:
            self.arrow_timer = 0
            self.arrow_visible = not self.arrow_visible

        self.pause_btn.update()
        self.resume_btn.update()
        self.menu_btn.update()
        for btn in self.choice_buttons:
            btn.update()

    def draw(self, t=0):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            draw_gradient_bg(self.screen)

        self._draw_progress_bar()
        self._draw_dialogue_panel()
        self._draw_portraits()
        self._draw_stats_display()

        if self.state != "complete":
            self.pause_btn.draw(self.screen)

        if self.state == "failure":
            self._draw_failure_overlay()
        elif self.state == "complete":
            self._draw_complete_overlay()
        if self.paused:
            self._draw_pause_overlay()
        if self.fade_alpha > 0:
            self._draw_fade()

        pygame.display.flip()

    def _draw_dialogue_panel(self):
        r = self.panel_rect

        draw_panel(self.screen, r, alpha=235, border_color=C_PANEL_BORDER)

        pygame.draw.rect(self.screen, C_ACCENT, (r.x, r.y + 2, 4, r.height - 4))

        if self.in_choices:
            self._draw_choice_prompt(r)
        else:
            self._draw_current_dialogue(r)

        if not self.in_choices and self.state == "playing":
            self._draw_continue_hint()

    def _draw_choice_prompt(self, r):
        prompt_font = make_font(FS_BODY)
        prompt = prompt_font.render("What will you do?", True, C_TEXT_SECONDARY)
        px = r.x + (r.width - prompt.get_width()) // 2
        py = r.y + (r.height - prompt.get_height()) // 2
        self.screen.blit(prompt, (px, py))
        for btn in self.choice_buttons:
            btn.draw(self.screen, self.font)

    def _draw_current_dialogue(self, r):
        if not self.sequence or self.sequence_index >= len(self.sequence):
            return

        step    = self.sequence[self.sequence_index]
        text    = self.typing_target[:self.typing_index]
        speaker = step["speaker"]
        npc_id  = step.get("npc_id")

        dlg_font  = make_font(FS_BODY)
        spk_font  = make_font(FS_SMALL, bold=True)
        tiny_font = make_font(FS_TINY)

        text_area_left  = r.x + PANEL_H_PAD + 8
        text_area_right = r.right - PANEL_H_PAD
        text_area_width = text_area_right - text_area_left
        center_x        = (text_area_left + text_area_right) // 2

        inner_y = r.y + PANEL_V_PAD
        max_y   = r.bottom - PANEL_V_PAD
        y       = inner_y

        if speaker == "player":
            spk_label = "YOU"
            spk_col   = C_TEXT_PLAYER
            txt_col   = C_TEXT_PLAYER
        elif speaker == "npc" and npc_id:
            npc_info  = self.chapter_data.get("characters", {}).get(npc_id, {})
            spk_label = npc_info.get("name", npc_id).upper()
            spk_col   = self.char_text_colors.get(npc_id, C_TEXT_NPC)
            txt_col   = spk_col
        elif speaker == "narrator":
            spk_label = "narrator"
            spk_col   = C_TEXT_NARRATOR
            txt_col   = C_TEXT_NARRATOR
            scenario_num = f"SCENARIO  [{self.scenario_index + 1}/{len(self.scenarios)}]"
            nar_lbl  = tiny_font.render(scenario_num, True, txt_col)
            if y + nar_lbl.get_height() <= max_y:
                self.screen.blit(nar_lbl,
                                (center_x - nar_lbl.get_width() // 2, y))
                y += nar_lbl.get_height() + 6
        else:
            return

        if speaker != "narrator" and spk_label:
            lbl_surf = spk_font.render(spk_label, True, spk_col)
            if y + lbl_surf.get_height() <= max_y:
                lbl_x = center_x - lbl_surf.get_width() // 2
                self.screen.blit(lbl_surf, (lbl_x, y))
                y += lbl_surf.get_height() + 6

                line_y = y - 2
                line_len = min(lbl_surf.get_width() + 20, text_area_width - 40)
                line_start_x = center_x - line_len // 2
                line_end_x   = center_x + line_len // 2
                pygame.draw.line(self.screen, spk_col,
                                 (line_start_x, line_y), (line_end_x, line_y), 1)
                y += 4

        effective_w = text_area_width
        lines = self._wrap(text, effective_w, dlg_font)
        for line in lines:
            if y >= max_y:
                break
            line_surf = dlg_font.render(line, True, txt_col)
            line_x = center_x - line_surf.get_width() // 2
            self.screen.blit(line_surf, (line_x, y))
            y += line_surf.get_height() + 3

    def _draw_continue_hint(self):
        if not self.arrow_visible:
            return
        hint_font = make_font(FS_TINY)
        hint = hint_font.render("Click or ENTER to continue  ▼",
                                True, C_TEXT_SECONDARY)
        x = SCREEN_W // 2 - hint.get_width() // 2
        y = self.panel_rect.bottom + 8
        self.screen.blit(hint, (x, y))

    def _draw_progress_bar(self):
        r       = self.panel_rect
        bar_y   = r.top - 8
        bar_h   = 4
        bar     = pygame.Rect(r.x, bar_y, r.width, bar_h)
        fill_w  = int(r.width * self.scenario_index / max(1, len(self.scenarios)))
        fill    = pygame.Rect(r.x, bar_y, fill_w, bar_h)
        pygame.draw.rect(self.screen, C_PANEL_BORDER_2, bar, border_radius=2)
        pygame.draw.rect(self.screen, C_ACCENT, fill, border_radius=2)

    def _draw_portraits(self):
        if self.state == "complete":
            return

        player_active = False
        npc_active    = False
        step          = None
        if (self.sequence and self.sequence_index < len(self.sequence)
                and not self.in_choices):
            step = self.sequence[self.sequence_index]
            speaker = step.get("speaker")
            player_active = (speaker == "player")
            npc_active    = (speaker == "npc" and step.get("npc_id") is not None)

        if player_active and self.player_image:
            x = 0
            y = SCREEN_H - self.player_image.get_height()
            self._blit_portrait(self.player_image, x, y, self.player_border)

        if npc_active and step:
            npc_id = step.get("npc_id")
            if npc_id and npc_id in self.char_images:
                img = self.char_images[npc_id]
                x = SCREEN_W - img.get_width()
                y = SCREEN_H - img.get_height()
                self._blit_portrait(img, x, y, self.char_borders.get(npc_id, False))

    def _blit_portrait(self, img, x, y, draw_border):
        if img is None:
            return
        self.screen.blit(img, (x, y))
        if draw_border:
            pygame.draw.rect(self.screen, C_PANEL_BORDER,
                             (x, y, img.get_width(), img.get_height()),
                             2, border_radius=4)

    def _draw_stats_display(self):
        if self.state == "complete":
            return
        hud_x, hud_y = 18, 14
        draw_star_row(self.screen, self._star_img,
                      hud_x, hud_y,
                      filled=self.stars_earned, total=3,
                      size=22, gap=4)
        att_font = make_font(FS_TINY)
        att_surf = att_font.render(f"Attempts: {self.attempts}",
                                   True, C_TEXT_SECONDARY)
        self.screen.blit(att_surf, (hud_x, hud_y + 28))

    def _draw_failure_overlay(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 175))
        self.screen.blit(ov, (0, 0))
        pop = pygame.Rect(SCREEN_W // 2 - 360, SCREEN_H // 2 - 110, 720, 220)
        draw_panel(self.screen, pop, alpha=248, border_color=C_FAILURE, radius=10)
        draw_text_centered(self.screen, "Wrong Choice",
                           make_font(FS_HEADING, bold=True), C_FAILURE,
                           SCREEN_W // 2, SCREEN_H // 2 - 50)
        draw_text_centered(self.screen, self.failure_text,
                           make_font(FS_BODY), C_TEXT_PRIMARY,
                           SCREEN_W // 2, SCREEN_H // 2 + 20)
        draw_text_centered(self.screen, "Retrying…",
                           make_font(FS_SMALL), C_TEXT_SECONDARY,
                           SCREEN_W // 2, SCREEN_H // 2 + 66)

    def _draw_complete_overlay(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 205))
        self.screen.blit(ov, (0, 0))
        pop = pygame.Rect(SCREEN_W // 2 - 390, SCREEN_H // 2 - 185, 780, 370)
        draw_panel(self.screen, pop, alpha=252, border_color=C_PANEL_BORDER, radius=12)
        pygame.draw.rect(self.screen, C_ACCENT,
                         (pop.x + 2, pop.y + 2, pop.width - 4, 5),
                         border_radius=12)

        draw_text_centered(self.screen, "CHAPTER COMPLETE",
                           make_font(FS_TITLE, bold=True), C_ACCENT,
                           SCREEN_W // 2, SCREEN_H // 2 - 100)

        star_size = 44
        gap       = 10
        total_w   = 3 * star_size + 2 * gap
        sx        = SCREEN_W // 2 - total_w // 2
        sy        = SCREEN_H // 2 - 24
        draw_star_row(self.screen, self._star_img,
                      sx, sy, self.stars_earned, total=3,
                      size=star_size, gap=gap)

        draw_text_centered(self.screen, f"Attempts: {self.attempts}",
                           make_font(FS_BODY), C_TEXT_SECONDARY,
                           SCREEN_W // 2, SCREEN_H // 2 + 78)
        draw_text_centered(self.screen, "Press ENTER or click to continue",
                           make_font(FS_SMALL), C_TEXT_SECONDARY,
                           SCREEN_W // 2, SCREEN_H // 2 + 128)

    def _draw_pause_overlay(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        self.screen.blit(ov, (0, 0))

        pw, ph = 460, 320
        pr = pygame.Rect(SCREEN_W // 2 - pw // 2,
                        SCREEN_H // 2 - ph // 2, pw, ph)
        draw_panel(self.screen, pr, alpha=248,
                border_color=C_PANEL_BORDER, radius=14)

        title_font = make_font(FS_HEADING, bold=True)
        title_surf = title_font.render("PAUSED", True, C_ACCENT)
        self.screen.blit(title_surf,
                        (SCREEN_W // 2 - title_surf.get_width() // 2,
                        pr.y + 46))

        line_y = pr.y + 104
        pygame.draw.line(self.screen, C_PANEL_BORDER_2,
                        (pr.x + 40, line_y),
                        (pr.right - 40, line_y), 2)

        btn_w, btn_h = 300, BTN_H_LG
        gap = 16
        total_h = btn_h * 2 + gap
        start_y = line_y + (pr.bottom - line_y - total_h) // 2

        self.resume_btn.rect = pygame.Rect(SCREEN_W // 2 - btn_w // 2,
                                        start_y, btn_w, btn_h)
        self.resume_btn.draw(self.screen, self.font)

        self.menu_btn.icon = self._return_icon
        self.menu_btn.rect = pygame.Rect(SCREEN_W // 2 - btn_w // 2,
                                        start_y + btn_h + gap, btn_w, btn_h)
        self.menu_btn.draw(self.screen, self.font)

    def _draw_fade(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, self.fade_alpha))
        self.screen.blit(ov, (0, 0))

    @staticmethod
    def _wrap(text, max_w, font):
        words, lines, cur = text.split(), [], ""
        for w in words:
            test = f"{cur} {w}".strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
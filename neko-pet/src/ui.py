"""
ui.py — Heads-up display: state badge, FPS counter, mood bar, tooltip.
"""

import pygame
from src.settings import WINDOW_WIDTH, WINDOW_HEIGHT, FPS

_MOOD_ICONS = {
    "idle":      ("😊", (160, 200, 255)),
    "walk":      ("🐾", (130, 255, 180)),
    "happy":     ("😻", (255, 200, 80)),
    "sleep":     ("😴", (180, 160, 255)),
    "surprised": ("😲", (255, 140, 60)),
}


class HUD:
    def __init__(self):
        pygame.font.init()
        self._font_big   = pygame.font.SysFont("segoeui", 20, bold=True)
        self._font_small = pygame.font.SysFont("segoeui", 14)
        self._font_emoji = pygame.font.SysFont("seguiemj", 22)
        self._fps_clock  = 0
        self._fps_val    = 0
        self._fps_tick   = 0

    def update(self, clock: pygame.time.Clock):
        self._fps_tick += 1
        if self._fps_tick >= 20:
            self._fps_tick = 0
            self._fps_val  = int(clock.get_fps())

    def draw(self, screen: pygame.Surface, cat_state: str,
             mouse_x: int, mouse_y: int):
        # ── state badge ───────────────────────────────────────────────────────
        icon, col = _MOOD_ICONS.get(cat_state, ("?", (200, 200, 200)))

        badge_surf = pygame.Surface((140, 36), pygame.SRCALPHA)
        badge_surf.fill((0, 0, 0, 90))
        pygame.draw.rect(badge_surf, (*col, 80), badge_surf.get_rect(),
                         border_radius=8)
        screen.blit(badge_surf, (12, 12))

        # emoji
        try:
            etxt = self._font_emoji.render(icon, True, col)
            screen.blit(etxt, (16, 15))
        except Exception:
            pass

        stxt = self._font_big.render(cat_state.upper(), True, col)
        screen.blit(stxt, (44, 20))

        # ── FPS ───────────────────────────────────────────────────────────────
        fps_txt = self._font_small.render(f"FPS {self._fps_val}", True,
                                          (150, 150, 180))
        screen.blit(fps_txt, (WINDOW_WIDTH - 70, 14))

        # ── tooltip strip at bottom ───────────────────────────────────────────
        tip = "Move cursor to guide Neko  •  Hover close for a reaction  •  [Esc] quit"
        tip_surf = pygame.Surface((WINDOW_WIDTH, 26), pygame.SRCALPHA)
        tip_surf.fill((0, 0, 0, 80))
        screen.blit(tip_surf, (0, WINDOW_HEIGHT - 26))
        ttxt = self._font_small.render(tip, True, (180, 160, 210))
        screen.blit(ttxt, ((WINDOW_WIDTH - ttxt.get_width()) // 2,
                            WINDOW_HEIGHT - 20))

        # ── cursor crosshair ─────────────────────────────────────────────────
        cx, cy = mouse_x, mouse_y
        col2   = (255, 105, 180, 160)
        s      = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(s, col2, (12, 12), 8, 2)
        pygame.draw.line(s, col2, (12, 0),  (12, 24), 1)
        pygame.draw.line(s, col2, (0, 12),  (24, 12), 1)
        screen.blit(s, (cx - 12, cy - 12))

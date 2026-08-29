"""
background.py — Animated gradient background with aurora shimmer and a
cosy floor/desk surface.
"""

import math
import random
import pygame
from src.settings import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COL_BG_TOP, COL_BG_BOT, COL_ACCENT, BG_SCROLL_SPEED,
)


def _lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


class Background:
    def __init__(self):
        self._w = WINDOW_WIDTH
        self._h = WINDOW_HEIGHT
        self._t = 0.0

        # pre-bake static gradient
        self._grad = pygame.Surface((self._w, self._h))
        for y in range(self._h):
            t   = y / self._h
            col = _lerp_color(COL_BG_TOP, COL_BG_BOT, t)
            pygame.draw.line(self._grad, col, (0, y), (self._w, y))

        # stars
        self._stars = [
            (random.randint(0, self._w),
             random.randint(0, int(self._h * 0.6)),
             random.uniform(0.6, 2.0),
             random.uniform(0, math.pi * 2))
            for _ in range(80)
        ]

        # aurora bands
        self._aurora = [
            {
                "y":     random.uniform(0.05, 0.40) * self._h,
                "phase": random.uniform(0, math.pi * 2),
                "speed": random.uniform(0.008, 0.018),
                "amp":   random.uniform(18, 50),
                "alpha": random.randint(18, 40),
                "col":   random.choice([
                    (80, 200, 180),
                    (120, 80, 220),
                    (200, 100, 180),
                    (60, 160, 255),
                ]),
            }
            for _ in range(5)
        ]

        # floor
        self._floor_y = int(self._h * 0.78)

    def update(self):
        self._t += BG_SCROLL_SPEED
        for a in self._aurora:
            a["phase"] += a["speed"]

    def draw(self, screen: pygame.Surface):
        # gradient
        screen.blit(self._grad, (0, 0))

        # aurora
        for a in self._aurora:
            pts = []
            steps = 60
            for i in range(steps + 1):
                x   = i / steps * self._w
                y   = a["y"] + math.sin(x * 0.012 + a["phase"]) * a["amp"]
                pts.append((x, y))
            # draw as thick translucent band
            surf = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
            for i in range(len(pts) - 1):
                x1, y1 = pts[i]
                x2, y2 = pts[i + 1]
                pygame.draw.line(surf, (*a["col"], a["alpha"]),
                                 (int(x1), int(y1)), (int(x2), int(y2)), 18)
            screen.blit(surf, (0, 0))

        # stars
        for sx, sy, sr, sphase in self._stars:
            brightness = int(180 + 75 * math.sin(self._t * 1.2 + sphase))
            col = (brightness, brightness, brightness)
            pygame.draw.circle(screen, col, (sx, sy), int(sr))

        # floor / desk surface
        floor_col  = (55, 38, 75)
        desk_surf  = pygame.Surface((self._w, self._h - self._floor_y),
                                    pygame.SRCALPHA)
        desk_surf.fill((*floor_col, 230))
        screen.blit(desk_surf, (0, self._floor_y))

        # desk highlight line
        pygame.draw.line(screen, (110, 80, 140),
                         (0, self._floor_y),
                         (self._w, self._floor_y), 2)

        # subtle desk grain pattern
        grain_surf = pygame.Surface((self._w, self._h - self._floor_y),
                                    pygame.SRCALPHA)
        for gx in range(0, self._w, 22):
            alpha = 8 + 6 * int(math.sin(gx * 0.04 + self._t * 0.1))
            pygame.draw.line(grain_surf, (255, 255, 255, alpha),
                             (gx, 0),
                             (gx + 4, self._h - self._floor_y), 1)
        screen.blit(grain_surf, (0, self._floor_y))

    def clamp_cat_y(self, y: float, cat_half: int) -> float:
        """Keep the cat from sinking below the desk."""
        return min(y, self._floor_y - cat_half)

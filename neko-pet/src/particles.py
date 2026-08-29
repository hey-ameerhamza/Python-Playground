"""
particles.py — Paw-print trail and background dust-mote particle systems.
"""

import math
import random
import pygame
from src.settings import (
    MAX_PAW_PRINTS, PAW_FADE_SPEED, PAW_INTERVAL,
    BG_PARTICLE_COUNT, WINDOW_WIDTH, WINDOW_HEIGHT,
    COL_ACCENT,
)


class PawPrint:
    def __init__(self, x, y, angle, paw_surf):
        self.x      = x
        self.y      = y
        self.angle  = angle
        self.alpha  = 180
        self.surf   = pygame.transform.rotate(paw_surf, -math.degrees(angle))
        self.rect   = self.surf.get_rect(center=(x, y))

    def update(self):
        self.alpha = max(0, self.alpha - PAW_FADE_SPEED)

    @property
    def alive(self):
        return self.alpha > 0

    def draw(self, screen):
        tmp = self.surf.copy()
        tmp.set_alpha(int(self.alpha))
        screen.blit(tmp, self.rect)


class PawTrail:
    def __init__(self, paw_surf):
        self._base_surf   = paw_surf
        self._prints: list[PawPrint] = []
        self._timer       = 0
        self._left        = True   # alternate left/right

    def update(self, cat_x, cat_y, moving, velocity_angle):
        self._timer += 1
        for p in self._prints:
            p.update()
        self._prints = [p for p in self._prints if p.alive]

        if moving and self._timer >= PAW_INTERVAL:
            self._timer = 0
            offset = 10 if self._left else -10
            side   = math.radians(math.degrees(velocity_angle) + 90)
            px     = cat_x + math.cos(side) * offset
            py     = cat_y + math.sin(side) * offset
            self._prints.append(PawPrint(px, py, velocity_angle, self._base_surf))
            self._left = not self._left
            if len(self._prints) > MAX_PAW_PRINTS:
                self._prints.pop(0)

    def draw(self, screen):
        for p in self._prints:
            p.draw(screen)


# ── background dust motes ─────────────────────────────────────────────────────

class DustMote:
    def __init__(self):
        self.reset(born=False)

    def reset(self, born=True):
        self.x     = random.uniform(0, WINDOW_WIDTH)
        self.y     = random.uniform(-20, WINDOW_HEIGHT) if born else random.uniform(0, WINDOW_HEIGHT)
        self.r     = random.uniform(1.5, 4.0)
        self.speed = random.uniform(0.15, 0.55)
        self.drift = random.uniform(-0.25, 0.25)
        self.alpha = random.randint(30, 100)
        self.da    = random.choice([-0.3, 0.3])
        hue        = random.choice([COL_ACCENT, (180, 220, 255), (255, 255, 200)])
        self.col   = hue

    def update(self):
        self.y     += self.speed
        self.x     += self.drift
        self.alpha += self.da
        self.alpha  = max(20, min(120, self.alpha))
        if self.y > WINDOW_HEIGHT + 10:
            self.reset()

    def draw(self, screen):
        s = pygame.Surface((int(self.r * 2 + 2), int(self.r * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, int(self.alpha)), (int(self.r + 1), int(self.r + 1)), int(self.r))
        screen.blit(s, (int(self.x - self.r), int(self.y - self.r)))


class DustSystem:
    def __init__(self):
        self._motes = [DustMote() for _ in range(BG_PARTICLE_COUNT)]

    def update(self):
        for m in self._motes:
            m.update()

    def draw(self, screen):
        for m in self._motes:
            m.draw(screen)


# ── burst particles (on happy/surprised) ─────────────────────────────────────

class BurstParticle:
    def __init__(self, x, y):
        self.x   = x
        self.y   = y
        angle    = random.uniform(0, math.pi * 2)
        speed    = random.uniform(2, 6)
        self.vx  = math.cos(angle) * speed
        self.vy  = math.sin(angle) * speed - 2
        self.r   = random.uniform(3, 7)
        self.col = random.choice([
            (255, 105, 180), (255, 220, 80), (130, 220, 255),
            (200, 255, 150), (255, 160, 60),
        ])
        self.life    = random.randint(20, 40)
        self.max_life = self.life

    def update(self):
        self.x   += self.vx
        self.y   += self.vy
        self.vy  += 0.18   # gravity
        self.vx  *= 0.97
        self.r    = max(0, self.r - 0.12)
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0 and self.r > 0

    def draw(self, screen):
        alpha = int(255 * self.life / self.max_life)
        s = pygame.Surface((int(self.r * 2 + 2), int(self.r * 2 + 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.col, alpha),
                           (int(self.r + 1), int(self.r + 1)), int(self.r))
        screen.blit(s, (int(self.x - self.r), int(self.y - self.r)))


class BurstSystem:
    def __init__(self):
        self._particles: list[BurstParticle] = []

    def burst(self, x, y, count=22):
        for _ in range(count):
            self._particles.append(BurstParticle(x, y))

    def update(self):
        for p in self._particles:
            p.update()
        self._particles = [p for p in self._particles if p.alive]

    def draw(self, screen):
        for p in self._particles:
            p.draw(screen)

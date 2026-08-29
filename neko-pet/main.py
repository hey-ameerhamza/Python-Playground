"""
main.py — Entry point for Neko Desktop Pet.

Run:
    python main.py

Optional desktop-pet mode (transparent, always-on-top):
    Set ALWAYS_ON_TOP = True in src/settings.py
"""

import sys
import os

# ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from src.settings import (
    WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, FPS, ALWAYS_ON_TOP,
    CLOSE_RADIUS,
)
from src.dragon_assets     import load_all
from src.dragon        import Dragon as Cat
from src.particles  import PawTrail, DustSystem, BurstSystem
from src.background import Background
from src.sound      import SoundManager
from src.ui         import HUD


def main():
    pygame.init()
    pygame.display.set_caption(WINDOW_TITLE)

    flags = 0
    if ALWAYS_ON_TOP:
        flags |= pygame.NOFRAME

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    clock  = pygame.time.Clock()

    # hide system cursor (we draw our own)
    pygame.mouse.set_visible(False)

    # ── subsystems ────────────────────────────────────────────────────────────
    frames  = load_all()
    sound   = SoundManager()
    cat     = Cat(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, frames, sound)
    bg      = Background()
    paw_sys = PawTrail(frames["paw"][0])
    dust    = DustSystem()
    burst   = BurstSystem()
    hud     = HUD()

    # ── main loop ─────────────────────────────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        mx, my = pygame.mouse.get_pos()
        # clamp cat to desk surface
        my_clamped = bg.clamp_cat_y(my, int(64 * cat._scale) // 2)

        # update
        cat.update(mx, my_clamped, dt)
        bg.update()
        paw_sys.update(cat.x, cat.y, cat.is_moving, cat.velocity_angle)
        dust.update()
        burst.update()
        hud.update(clock)

        # burst on happy/surprised
        if cat.burst_requested:
            cat.burst_requested = False
            burst.burst(int(cat.x), int(cat.y))

        # ── draw ─────────────────────────────────────────────────────────────
        bg.draw(screen)
        dust.draw(screen)
        paw_sys.draw(screen)
        cat.draw(screen)
        burst.draw(screen)
        hud.draw(screen, cat.state, mx, my)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

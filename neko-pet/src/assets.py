"""
assets.py — Procedural sprite generator for Neko.

All cat frames are drawn at runtime with pygame.draw primitives so the
project has zero external image files.  Every frame is a 64×64 Surface
with a transparent background.
"""

import math
import pygame
from pygame import Color

# ── palette ─────────────────────────────────────────────────────────────────
CAT_BODY   = (245, 220, 195)
CAT_DARK   = (200, 160, 120)
CAT_PINK   = (255, 182, 193)
CAT_EYE    = (60,  120, 220)
CAT_PUPIL  = (15,   15,  30)
CAT_NOSE   = (255, 100, 120)
CAT_STRIPE = (210, 175, 140)
CAT_WHITE  = (255, 255, 255)
CAT_SHADOW = (0, 0, 0, 70)


def _surf(w=64, h=64):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    return s


# ── low-level drawing helpers ────────────────────────────────────────────────

def _ellipse(surf, col, cx, cy, rx, ry, width=0):
    r = pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2)
    pygame.draw.ellipse(surf, col, r, width)


def _circle(surf, col, cx, cy, r, width=0):
    pygame.draw.circle(surf, col, (cx, cy), r, width)


def _draw_shadow(surf, cx, cy, rx, ry):
    shad = pygame.Surface((rx * 2, ry * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(shad, (0, 0, 0, 60), shad.get_rect())
    surf.blit(shad, (cx - rx, cy - ry))


def _draw_ear(surf, tip_x, tip_y, left=True):
    """Pointy cat ear."""
    sign = -1 if left else 1
    pts = [
        (tip_x,          tip_y),
        (tip_x - sign*8, tip_y + 18),
        (tip_x + sign*4, tip_y + 18),
    ]
    pygame.draw.polygon(surf, CAT_BODY, pts)
    # inner ear
    inner = [
        (tip_x,          tip_y + 4),
        (tip_x - sign*5, tip_y + 14),
        (tip_x + sign*2, tip_y + 14),
    ]
    pygame.draw.polygon(surf, CAT_PINK, inner)


def _draw_face(surf, cx, cy, blink=False, happy=False, sleepy=False, surprised=False):
    # Eyes
    eye_y = cy - 2
    for ex in (cx - 9, cx + 9):
        if blink or sleepy:
            # closed eye — a thin arc
            pygame.draw.arc(surf, CAT_PUPIL,
                            pygame.Rect(ex - 5, eye_y - 2, 10, 8),
                            math.pi * 0.1, math.pi * 0.9, 2)
        elif happy:
            pygame.draw.arc(surf, CAT_PUPIL,
                            pygame.Rect(ex - 5, eye_y - 3, 10, 8),
                            math.pi * 0.15, math.pi * 0.85, 2)
        elif surprised:
            _circle(surf, CAT_EYE,   ex, eye_y, 6)
            _circle(surf, CAT_PUPIL, ex, eye_y, 4)
            _circle(surf, CAT_WHITE, ex + 1, eye_y - 1, 1)
        else:
            _circle(surf, CAT_EYE,   ex, eye_y, 5)
            _circle(surf, CAT_PUPIL, ex, eye_y, 3)
            _circle(surf, CAT_WHITE, ex + 1, eye_y - 1, 1)

    # Nose
    nose_pts = [(cx, cy + 5), (cx - 3, cy + 2), (cx + 3, cy + 2)]
    pygame.draw.polygon(surf, CAT_NOSE, nose_pts)

    # Mouth
    if happy:
        pygame.draw.arc(surf, CAT_DARK,
                        pygame.Rect(cx - 7, cy + 4, 14, 8),
                        math.pi * 1.1, math.pi * 1.9, 2)
    elif sleepy:
        pygame.draw.line(surf, CAT_DARK, (cx - 4, cy + 7), (cx + 4, cy + 7), 2)
    else:
        pygame.draw.arc(surf, CAT_DARK,
                        pygame.Rect(cx - 5, cy + 4, 10, 6),
                        math.pi * 1.2, math.pi * 1.8, 2)

    # Whiskers
    wlen = 14
    for side, dy in [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]:
        x0 = cx + side * 4
        x1 = cx + side * (4 + wlen)
        y0 = cy + 5 + dy * 3
        y1 = cy + 5 + dy * 3 + dy
        pygame.draw.line(surf, CAT_DARK, (x0, y0), (x1, y1), 1)


def _draw_body(surf, cx, cy, stretch=0):
    """stretch: -1 squash, 0 normal, 1 stretch."""
    rx = 16 - stretch * 2
    ry = 14 + stretch * 3
    _ellipse(surf, CAT_BODY, cx, cy, rx, ry)
    # belly
    _ellipse(surf, CAT_WHITE, cx, cy + 3, rx - 5, ry - 5)
    # stripes
    for sx in (-5, 0, 5):
        pygame.draw.line(surf, CAT_STRIPE,
                         (cx + sx, cy - ry + 4),
                         (cx + sx + 2, cy + ry - 6), 2)


def _draw_tail(surf, bx, by, angle_deg, curl=0.0):
    """Draw a segmented tail from base (bx, by)."""
    segs   = 8
    length = 12
    a      = math.radians(angle_deg)
    px, py = bx, by
    for i in range(segs):
        t    = i / segs
        a2   = a + math.sin(t * math.pi + curl) * 0.9
        nx   = px + math.cos(a2) * length
        ny   = py + math.sin(a2) * length
        r    = max(1, int(4 * (1 - t)))
        col  = CAT_DARK if i % 2 == 0 else CAT_BODY
        pygame.draw.line(surf, col, (int(px), int(py)), (int(nx), int(ny)), r * 2)
        _circle(surf, col, int(nx), int(ny), r)
        px, py = nx, ny


def _draw_legs(surf, cx, cy, phase=0, sitting=False):
    """Four legs; phase drives walk cycle."""
    if sitting:
        # front paws sitting
        for sx in (-8, 8):
            _ellipse(surf, CAT_BODY, cx + sx, cy + 22, 5, 7)
            _circle(surf, CAT_PINK, cx + sx, cy + 26, 3)
        # back haunches
        _ellipse(surf, CAT_BODY, cx - 14, cy + 10, 6, 10)
        _ellipse(surf, CAT_BODY, cx + 14, cy + 10, 6, 10)
        return

    offsets = [
        (-10, math.sin(phase) * 5),
        ( 10, math.sin(phase + math.pi) * 5),
        ( -7, math.sin(phase + math.pi * 0.5) * 4),
        (  7, math.sin(phase + math.pi * 1.5) * 4),
    ]
    for ox, oy in offsets:
        lx = cx + ox
        ly = cy + 16 + oy
        pygame.draw.line(surf, CAT_BODY, (lx, cy + 12), (lx, ly), 5)
        _circle(surf, CAT_PINK, lx, ly + 3, 4)


# ── public frame builders ────────────────────────────────────────────────────

def make_walk_frames(n=8):
    """Return list of n walk-cycle surfaces."""
    frames = []
    for i in range(n):
        phase = (i / n) * math.pi * 2
        s = _surf()
        cx, cy = 32, 34

        _draw_shadow(s, cx, cy + 22, 18, 5)
        _draw_tail(s, cx + 15, cy + 4, 110 + math.sin(phase) * 25,
                   curl=math.sin(phase * 0.5))
        _draw_legs(s, cx, cy, phase)
        _draw_body(s, cx, cy)
        _draw_ear(s, cx - 10, cy - 26, left=True)
        _draw_ear(s, cx + 10, cy - 26, left=False)
        _draw_face(s, cx, cy - 16)
        frames.append(s)
    return frames


def make_idle_frames(n=4):
    frames = []
    for i in range(n):
        curl = math.sin(i / n * math.pi * 2) * 0.4
        s = _surf()
        cx, cy = 32, 36

        _draw_shadow(s, cx, cy + 18, 16, 4)
        _draw_tail(s, cx + 14, cy + 5, 100 + math.sin(curl) * 20, curl=curl)
        _draw_legs(s, cx, cy, phase=0, sitting=True)
        _draw_body(s, cx, cy, stretch=0)
        _draw_ear(s, cx - 10, cy - 24, left=True)
        _draw_ear(s, cx + 10, cy - 24, left=False)
        _draw_face(s, cx, cy - 14, blink=(i == 2))
        frames.append(s)
    return frames


def make_blink_frames():
    frames = []
    for blink in [False, False, True, True, True, False]:
        s = _surf()
        cx, cy = 32, 36
        _draw_shadow(s, cx, cy + 18, 16, 4)
        _draw_tail(s, cx + 14, cy + 5, 105, curl=0.2)
        _draw_legs(s, cx, cy, phase=0, sitting=True)
        _draw_body(s, cx, cy)
        _draw_ear(s, cx - 10, cy - 24, left=True)
        _draw_ear(s, cx + 10, cy - 24, left=False)
        _draw_face(s, cx, cy - 14, blink=blink)
        frames.append(s)
    return frames


def make_happy_frames(n=6):
    frames = []
    for i in range(n):
        bounce = abs(math.sin(i / n * math.pi)) * 6
        s = _surf()
        cx, cy = 32, int(34 - bounce)
        _draw_shadow(s, cx, 56 + bounce * 0.3, 18 - bounce * 0.2, 4)
        _draw_tail(s, cx + 15, cy + 4, 90 + math.sin(i * 0.8) * 40, curl=0.6)
        _draw_legs(s, cx, cy, phase=i * 0.8)
        _draw_body(s, cx, cy, stretch=int(bounce * 0.2))
        _draw_ear(s, cx - 10, cy - 26, left=True)
        _draw_ear(s, cx + 10, cy - 26, left=False)
        _draw_face(s, cx, cy - 16, happy=True)
        frames.append(s)
    return frames


def make_sleep_frames(n=4):
    frames = []
    for i in range(n):
        s = _surf()
        cx, cy = 32, 38
        # curled body
        _draw_shadow(s, cx, cy + 14, 20, 5)
        _ellipse(s, CAT_BODY, cx, cy + 4, 20, 12)
        _draw_tail(s, cx + 14, cy + 8, 160, curl=1.2)
        _draw_ear(s, cx - 6, cy - 8,  left=True)
        _draw_ear(s, cx + 6, cy - 8,  left=False)
        _draw_face(s, cx, cy - 2, blink=True, sleepy=True)
        # Z Z z
        zsize = 7
        for j, (zx, zy) in enumerate([(cx + 16, cy - 10 - j * 9)
                                       for j in range(3)]):
            alpha = 220 - j * 60
            zs = pygame.font.SysFont("arial", zsize + j * 2).render(
                "z" if j == 0 else "Z", True, (180, 200, 255, alpha))
            s.blit(zs, (zx, zy))
        frames.append(s)
    return frames


def make_surprised_frames(n=4):
    frames = []
    for i in range(n):
        s = _surf()
        cx, cy = 32, 30
        stretch = 2 if i < 2 else 0
        _draw_shadow(s, cx, 56, 16, 4)
        _draw_tail(s, cx + 15, cy + 8, 70, curl=1.0)
        _draw_legs(s, cx, cy, phase=0)
        _draw_body(s, cx, cy, stretch=stretch)
        _draw_ear(s, cx - 10, cy - 26 - stretch, left=True)
        _draw_ear(s, cx + 10, cy - 26 - stretch, left=False)
        _draw_face(s, cx, cy - 16 - stretch, surprised=True)
        frames.append(s)
    return frames


def make_paw_print():
    """Return a small paw-print surface."""
    s = pygame.Surface((20, 20), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    _circle(s, CAT_PINK, 10, 12, 5)   # main pad
    for dx, dy in [(-5, 3), (0, 0), (5, 3)]:
        _circle(s, CAT_PINK, 10 + dx, 4 + dy, 3)
    return s


def load_all():
    """Return a dict of all animation frame lists."""
    return {
        "walk":      make_walk_frames(8),
        "idle":      make_idle_frames(4),
        "blink":     make_blink_frames(),
        "happy":     make_happy_frames(6),
        "sleep":     make_sleep_frames(4),
        "surprised": make_surprised_frames(4),
        "paw":       [make_paw_print()],
    }

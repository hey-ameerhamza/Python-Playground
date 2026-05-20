"""
dragon_assets.py — Procedural sprite generator for the Dragon pet.

All frames are 80×80 SRCALPHA surfaces drawn entirely with pygame.draw
primitives — no image files needed.

Dragon anatomy
──────────────
  Head  : broad snout, two curved horns, slit pupils, nostrils, fangs
  Body  : stocky scaled torso with belly plates
  Wings : folded at rest, half-spread when walking, full-spread when happy
  Tail  : thick segmented tail with a spade tip
  Legs  : stubby clawed legs; walk cycle drives alternating offsets
  Fire  : small flame puff drawn at the snout for the "surprised" state
"""

import math
import pygame

# ── dragon palette ────────────────────────────────────────────────────────────
D_BODY    = (60,  130,  80)   # deep emerald green
D_SCALE   = (45,  105,  60)   # darker scale lines
D_BELLY   = (190, 220, 160)   # pale underside
D_HORN    = (210, 170,  60)   # amber horns
D_EYE     = (255, 220,   0)   # golden iris
D_PUPIL   = (10,   10,  20)   # slit pupil
D_WING    = (80,  160, 100)   # wing membrane
D_WING_D  = (40,   90,  55)   # wing veins / dark
D_CLAW    = (220, 200, 140)   # ivory claws
D_FIRE_A  = (255, 200,  50)   # fire inner
D_FIRE_B  = (255, 100,  20)   # fire outer
D_FIRE_C  = (255,  50,   0)   # fire tip
D_SPADE   = (35,   85,  50)   # tail spade


def _surf(w=80, h=80):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    return s


def _ellipse(surf, col, cx, cy, rx, ry, width=0):
    pygame.draw.ellipse(surf, col,
                        pygame.Rect(cx - rx, cy - ry, rx * 2, ry * 2), width)


def _circle(surf, col, cx, cy, r, width=0):
    if r <= 0:
        return
    pygame.draw.circle(surf, col, (int(cx), int(cy)), int(r), width)


def _poly(surf, col, pts, width=0):
    if len(pts) >= 3:
        pygame.draw.polygon(surf, col, [(int(x), int(y)) for x, y in pts], width)


def _shadow(surf, cx, cy, rx, ry):
    sh = pygame.Surface((rx * 2, ry * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0, 0, 0, 55), sh.get_rect())
    surf.blit(sh, (int(cx - rx), int(cy - ry)))


# ── component drawers ─────────────────────────────────────────────────────────

def _draw_horn(surf, tx, ty, lean):
    """Single curved horn.  lean: +1 right, -1 left."""
    pts = [
        (tx,           ty),
        (tx + lean * 6, ty + 14),
        (tx + lean * 2, ty + 16),
    ]
    _poly(surf, D_HORN, pts)
    # shine
    pygame.draw.line(surf, (240, 230, 130),
                     (int(tx + lean), int(ty + 2)),
                     (int(tx + lean * 4), int(ty + 10)), 1)


def _draw_eye(surf, cx, cy, closed=False, happy=False, surprised=False):
    if closed:
        pygame.draw.arc(surf, D_SCALE,
                        pygame.Rect(cx - 6, cy - 3, 12, 8),
                        math.pi * 0.05, math.pi * 0.95, 2)
        return
    # iris
    _circle(surf, D_EYE, cx, cy, 6)
    if surprised:
        _circle(surf, D_PUPIL, cx, cy, 4)  # round pupil when scared
    else:
        # vertical slit pupil
        _circle(surf, D_PUPIL, cx, cy, 2)
        pygame.draw.line(surf, D_PUPIL,
                         (cx, cy - 5), (cx, cy + 5), 2)
    _circle(surf, (255, 255, 255), cx + 2, cy - 2, 1)

    if happy:
        # sparkle dot
        _circle(surf, (255, 255, 200), cx - 2, cy - 3, 1)


def _draw_head(surf, cx, cy, blink=False, happy=False,
               sleepy=False, surprised=False):
    # broad snout
    _ellipse(surf, D_BODY, cx, cy, 16, 13)
    # forehead ridge
    _ellipse(surf, D_SCALE, cx, cy - 8, 10, 5)

    # horns
    _draw_horn(surf, cx - 8,  cy - 20, lean=-1)
    _draw_horn(surf, cx + 8,  cy - 20, lean=+1)

    # eyes
    _draw_eye(surf, cx - 7, cy - 4,
              closed=blink or sleepy, happy=happy, surprised=surprised)
    _draw_eye(surf, cx + 7, cy - 4,
              closed=blink or sleepy, happy=happy, surprised=surprised)

    # nostrils
    _circle(surf, D_SCALE, cx - 5, cy + 5, 2)
    _circle(surf, D_SCALE, cx + 5, cy + 5, 2)

    # fangs / teeth (peek below snout)
    for fx in (cx - 4, cx + 4):
        _poly(surf, (230, 230, 220), [
            (fx, cy + 10), (fx - 2, cy + 15), (fx + 2, cy + 15)
        ])

    # mouth line
    if happy:
        pygame.draw.arc(surf, D_SCALE,
                        pygame.Rect(cx - 9, cy + 5, 18, 10),
                        math.pi * 1.1, math.pi * 1.9, 2)
    elif sleepy:
        pygame.draw.line(surf, D_SCALE, (cx - 5, cy + 9), (cx + 5, cy + 9), 2)
    else:
        pygame.draw.line(surf, D_SCALE, (cx - 7, cy + 9), (cx + 7, cy + 9), 2)

    # scale texture on head
    for sx, sy in [(-7, -10), (0, -12), (7, -10), (-4, -6), (4, -6)]:
        _circle(surf, D_SCALE, cx + sx, cy + sy, 2, 1)


def _draw_body(surf, cx, cy, stretch=0):
    rx = 15
    ry = 18 + stretch * 2
    _ellipse(surf, D_BODY,  cx, cy, rx, ry)
    # belly plates
    for i, py in enumerate(range(cy - ry + 6, cy + ry - 4, 7)):
        pw = max(4, 10 - abs(i - 2) * 3)
        _ellipse(surf, D_BELLY, cx, py, pw, 3)
    # scale rows
    for row in range(-2, 3):
        ry2 = cy + row * 7
        for col in [-10, -3, 4]:
            _circle(surf, D_SCALE, cx + col, ry2, 3, 1)


def _draw_wing(surf, cx, cy, spread=0.0, phase=0.0):
    """
    spread  0.0 = folded tight against body
            0.5 = half open (walking)
            1.0 = fully spread (happy / gliding)
    phase   oscillation for flapping
    """
    flap = math.sin(phase) * 8 * spread
    for side in (-1, 1):
        bx = cx + side * 12          # wing root
        by = cy - 5

        if spread < 0.15:            # folded: just a membrane ridge
            pts = [
                (bx,            by),
                (bx + side * 6, by - 8),
                (bx + side * 4, by + 10),
            ]
            _poly(surf, D_WING_D, pts)
            continue

        # tip position depends on spread & flap
        tip_x = bx + side * (20 + spread * 25)
        tip_y = by - 18 - spread * 14 + flap
        mid_x = bx + side * (10 + spread * 12)
        mid_y = by - 10 - spread * 8

        # membrane fill
        mem = [
            (bx,    by),
            (bx,    by + 12),
            (mid_x, mid_y + 8),
            (tip_x, tip_y + 4),
            (tip_x, tip_y),
            (mid_x, mid_y),
        ]
        col_a = (*D_WING, int(200 + spread * 55))
        mem_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        _poly(mem_surf, col_a, mem)
        surf.blit(mem_surf, (0, 0))

        # veins
        for t in (0.33, 0.66):
            vx = int(bx + (tip_x - bx) * t)
            vy = int(by + (tip_y - by) * t)
            pygame.draw.line(surf, D_WING_D, (int(bx), int(by)), (vx, vy), 1)


def _draw_tail(surf, bx, by, angle_deg, wag=0.0):
    """Thick segmented tail with a diamond spade tip."""
    segs   = 9
    seg_l  = 9
    a      = math.radians(angle_deg)
    px, py = bx, by
    for i in range(segs):
        t  = i / segs
        a2 = a + math.sin(t * math.pi * 1.5 + wag) * 0.7
        nx = px + math.cos(a2) * seg_l
        ny = py + math.sin(a2) * seg_l
        r  = max(2, int(7 * (1 - t * 0.7)))
        _circle(surf, D_SCALE if i % 2 == 0 else D_BODY, nx, ny, r)
        pygame.draw.line(surf, D_BODY,
                         (int(px), int(py)), (int(nx), int(ny)), r * 2)
        px, py = nx, ny
    # spade tip
    tip_pts = [
        (px,                py - 7),
        (px + 5,            py + 3),
        (px,                py + 7),
        (px - 5,            py + 3),
    ]
    _poly(surf, D_SPADE, tip_pts)


def _draw_legs(surf, cx, cy, phase=0.0, sitting=False):
    if sitting:
        for sx in (-9, 9):
            # upper leg
            pygame.draw.line(surf, D_BODY, (cx + sx, cy + 8),
                             (cx + sx, cy + 24), 6)
            # foot
            _ellipse(surf, D_BODY, cx + sx, cy + 26, 6, 4)
            # claws
            for c in (-4, 0, 4):
                pygame.draw.line(surf, D_CLAW,
                                 (cx + sx + c, cy + 28),
                                 (cx + sx + c, cy + 32), 2)
        return

    offsets = [
        (-11, math.sin(phase) * 6),
        ( 11, math.sin(phase + math.pi) * 6),
        ( -7, math.sin(phase + math.pi * 0.5) * 4),
        (  7, math.sin(phase + math.pi * 1.5) * 4),
    ]
    for ox, oy in offsets:
        lx = cx + ox
        ly = cy + 18 + oy
        pygame.draw.line(surf, D_BODY, (lx, cy + 10), (lx, ly), 6)
        _ellipse(surf, D_BODY, lx, ly + 3, 6, 4)
        for c in (-3, 0, 3):
            pygame.draw.line(surf, D_CLAW,
                             (lx + c, ly + 5), (lx + c, ly + 9), 2)


def _draw_fire(surf, cx, cy, intensity=1.0):
    """Small fire puff at the snout tip."""
    for layer, (col, rad) in enumerate(
            [(D_FIRE_C, 10), (D_FIRE_B, 7), (D_FIRE_A, 4)]):
        alpha = int(200 * intensity)
        s2 = pygame.Surface((rad * 2 + 2, rad * 2 + 2), pygame.SRCALPHA)
        pygame.draw.ellipse(s2, (*col, alpha), s2.get_rect())
        surf.blit(s2, (int(cx - rad - 1 + layer * 6),
                       int(cy - rad // 2 - layer * 3 - 1)))


# ── public frame builders ─────────────────────────────────────────────────────

def make_walk_frames(n=8):
    frames = []
    for i in range(n):
        phase = (i / n) * math.pi * 2
        s = _surf()
        cx, cy = 40, 38

        _shadow(s, cx, cy + 26, 20, 5)
        _draw_tail(s, cx + 14, cy + 10, 110 + math.sin(phase) * 20,
                   wag=phase * 0.5)
        _draw_wing(s, cx, cy, spread=0.4, phase=phase)
        _draw_legs(s, cx, cy, phase)
        _draw_body(s, cx, cy)
        _draw_head(s, cx, cy - 22)
        frames.append(s)
    return frames


def make_idle_frames(n=4):
    frames = []
    for i in range(n):
        wag = math.sin(i / n * math.pi * 2) * 0.3
        s = _surf()
        cx, cy = 40, 40

        _shadow(s, cx, cy + 22, 18, 4)
        _draw_tail(s, cx + 14, cy + 12, 105, wag=wag)
        _draw_wing(s, cx, cy, spread=0.0)
        _draw_legs(s, cx, cy, sitting=True)
        _draw_body(s, cx, cy)
        _draw_head(s, cx, cy - 20)
        frames.append(s)
    return frames


def make_blink_frames():
    frames = []
    for blink in [False, False, True, True, True, False]:
        s = _surf()
        cx, cy = 40, 40
        _shadow(s, cx, cy + 22, 18, 4)
        _draw_tail(s, cx + 14, cy + 12, 105, wag=0.15)
        _draw_wing(s, cx, cy, spread=0.0)
        _draw_legs(s, cx, cy, sitting=True)
        _draw_body(s, cx, cy)
        _draw_head(s, cx, cy - 20, blink=blink)
        frames.append(s)
    return frames


def make_happy_frames(n=6):
    frames = []
    for i in range(n):
        bounce = abs(math.sin(i / n * math.pi)) * 8
        s = _surf()
        cx, cy = 40, int(36 - bounce)
        _shadow(s, cx, 66 + bounce * 0.3, 20 - bounce * 0.2, 5)
        _draw_tail(s, cx + 14, cy + 10, 85 + math.sin(i * 0.9) * 35,
                   wag=i * 0.7)
        _draw_wing(s, cx, cy, spread=0.9, phase=i * 0.7)
        _draw_legs(s, cx, cy, phase=i * 0.9)
        _draw_body(s, cx, cy, stretch=int(bounce * 0.15))
        _draw_head(s, cx, cy - 22, happy=True)
        frames.append(s)
    return frames


def make_sleep_frames(n=4):
    frames = []
    for i in range(n):
        s = _surf()
        cx, cy = 40, 44
        _shadow(s, cx, cy + 16, 22, 5)
        # curled body blob
        _ellipse(s, D_BODY, cx, cy + 4, 22, 13)
        _draw_belly_plates_curled(s, cx, cy + 4)
        _draw_tail(s, cx + 16, cy + 8, 155, wag=1.1)
        _draw_wing(s, cx, cy, spread=0.0)
        _draw_head(s, cx - 4, cy - 10, blink=True, sleepy=True)
        # Z z z
        for j in range(3):
            zfont = pygame.font.SysFont("arial", 8 + j * 3, bold=True)
            ztxt  = zfont.render("Z" if j > 0 else "z", True,
                                 (160, 220, 180, 200))
            s.blit(ztxt, (cx + 14 + j * 5, cy - 16 - j * 10))
        frames.append(s)
    return frames


def _draw_belly_plates_curled(surf, cx, cy):
    """Compact belly plates for the curled sleep pose."""
    for i, px in enumerate(range(cx - 10, cx + 12, 8)):
        _ellipse(surf, D_BELLY, px, cy + i % 2 * 4, 5, 3)


def make_surprised_frames(n=4):
    frames = []
    for i in range(n):
        s = _surf()
        cx, cy = 40, 34
        stretch = 3 if i < 2 else 0
        fire_i  = 1.0 if i < 3 else 0.4
        _shadow(s, cx, 68, 18, 4)
        _draw_tail(s, cx + 14, cy + 12, 65, wag=1.2)
        _draw_wing(s, cx, cy, spread=0.6, phase=i * 0.5)
        _draw_legs(s, cx, cy)
        _draw_body(s, cx, cy, stretch=stretch)
        _draw_head(s, cx, cy - 24 - stretch, surprised=True)
        # fire breath!
        _draw_fire(s, cx + 14, cy - 26 - stretch, intensity=fire_i)
        frames.append(s)
    return frames


def make_footprint():
    """Dragon claw-print (three talon marks) instead of a paw pad."""
    s = pygame.Surface((22, 22), pygame.SRCALPHA)
    s.fill((0, 0, 0, 0))
    # palm
    _ellipse(s, (*D_SCALE, 160), 11, 14, 6, 5)
    # three claw lines
    for cx2, angle in [(6, -30), (11, -90), (16, -150)]:
        ex = cx2 + int(math.cos(math.radians(angle)) * 7)
        ey = 4  + int(math.sin(math.radians(angle)) * 7)
        pygame.draw.line(s, (*D_CLAW, 180), (cx2, 10), (ex, ey), 2)
    return s


def load_all():
    """Return dict of animation frame lists — same interface as assets.load_all()."""
    return {
        "walk":      make_walk_frames(8),
        "idle":      make_idle_frames(4),
        "blink":     make_blink_frames(),
        "happy":     make_happy_frames(6),
        "sleep":     make_sleep_frames(4),
        "surprised": make_surprised_frames(4),
        "paw":       [make_footprint()],
    }
"""
dragon.py — Dragon desktop pet entity.

Drop-in replacement for cat.py.  Swap in main.py:
    from src.dragon import Dragon as Cat   # or just rename
    from src.dragon_assets import load_all

Differences from the cat
────────────────────────
* Larger sprite (80 px canvas, scale=2.2)
* Wings spread when walking, fully open when happy
* Breathes fire when surprised
* Roars instead of meowing (procedural sound via SoundManager.meow())
* Heavier physics: slightly slower acceleration, bigger close-radius feel
* Sleep: curls with smoke puffs rising from nostrils
* Tail uses the dragon_assets wag-spade tail instead of cat curl
"""

import math
import random
import pygame
from src.settings import (
    CAT_SPEED         as DRAGON_SPEED,
    CAT_ACCELERATION  as DRAGON_ACCEL,
    CLOSE_RADIUS,
    IDLE_TIMEOUT_SEC,
    SLEEP_TIMEOUT_SEC,
    FPS,
    WALK_FRAME_RATE,
    IDLE_FRAME_RATE,
    BLINK_INTERVAL_SEC,
    TAIL_SPEED,
    JUMP_HEIGHT,
    JUMP_DURATION,
    MEOW_CHANCE       as ROAR_CHANCE,
)


class State:
    IDLE      = "idle"
    WALK      = "walk"
    HAPPY     = "happy"
    SURPRISED = "surprised"
    SLEEP     = "sleep"


class Dragon:
    """
    Identical public interface to Cat so main.py needs zero changes.
    Just replace:
        from src.cat    import Cat
        from src.assets import load_all
    with:
        from src.dragon        import Dragon as Cat
        from src.dragon_assets import load_all
    """

    def __init__(self, x: float, y: float, frames: dict, sound_mgr):
        self.x   = float(x)
        self.y   = float(y)
        self.vx  = 0.0
        self.vy  = 0.0

        self._frames     = frames
        self._state      = State.IDLE
        self._frame_idx  = 0
        self._frame_tick = 0
        self._facing     = 1          # +1 right, -1 left
        self._scale      = 2.2        # slightly larger than the cat
        self._tail_phase = 0.0

        # jump / glide
        self._jump_t      = 0
        self._jump_active = False
        self._jump_base_y = y

        # timers
        self._idle_timer   = 0.0
        self._blink_timer  = 0.0
        self._blink_target = random.uniform(*BLINK_INTERVAL_SEC)
        self._is_blinking  = False
        self._blink_frames = frames["blink"]
        self._blink_f      = 0
        self._happy_timer  = 0
        self._surprised_t  = 0

        # smoke puffs for sleep (simple list of (x,y,alpha,dy))
        self._smoke: list[list] = []
        self._smoke_tick = 0

        # burst flag read & reset by main.py
        self.burst_requested = False

        self._sound = sound_mgr

    # ── public API (same as Cat) ──────────────────────────────────────────────

    @property
    def state(self) -> str:
        return self._state

    @property
    def rect(self) -> pygame.Rect:
        size = int(80 * self._scale)
        return pygame.Rect(int(self.x) - size // 2,
                           int(self.y) - size // 2, size, size)

    def update(self, mx: float, my: float, dt: float):
        dx   = mx - self.x
        dy   = my - self.y
        dist = math.hypot(dx, dy)

        self._update_physics(dx, dy, dist)
        self._update_state(dist)
        self._update_animation()
        self._tail_phase += TAIL_SPEED

        # roar chance while walking
        if self._state == State.WALK and random.random() < ROAR_CHANCE * 0.6:
            self._sound.meow()

        # smoke update (sleep state)
        self._update_smoke()

    def draw(self, screen: pygame.Surface):
        frame = self._get_current_frame()
        if frame is None:
            return

        size  = int(80 * self._scale)
        frame = pygame.transform.scale(frame, (size, size))

        if self._facing == -1:
            frame = pygame.transform.flip(frame, True, False)

        # drop shadow (larger for dragon)
        shw = int(size * 0.55)
        shh = int(size * 0.12)
        shad = pygame.Surface((shw, shh), pygame.SRCALPHA)
        pygame.draw.ellipse(shad, (0, 0, 0, 60), shad.get_rect())
        screen.blit(shad, (int(self.x) - shw // 2,
                           int(self.y) + size // 2 - shh))

        screen.blit(frame, (int(self.x) - size // 2,
                            int(self.y) - size // 2))

        # smoke puffs drawn above frame when sleeping
        if self._state == State.SLEEP:
            self._draw_smoke(screen)

    # ── physics ───────────────────────────────────────────────────────────────

    def _update_physics(self, dx, dy, dist):
        if self._state in (State.SLEEP, State.HAPPY, State.SURPRISED):
            self.vx *= 0.88
            self.vy *= 0.88
            self.x  += self.vx
            self.y  += self.vy
            return

        if dist > CLOSE_RADIUS:
            speed     = min(DRAGON_SPEED * 0.9, dist * 0.07)
            target_vx = (dx / dist) * speed if dist else 0
            target_vy = (dy / dist) * speed if dist else 0
            self.vx  += (target_vx - self.vx) * DRAGON_ACCEL * 0.85
            self.vy  += (target_vy - self.vy) * DRAGON_ACCEL * 0.85
        else:
            self.vx *= 0.78
            self.vy *= 0.78

        self.x += self.vx
        self.y += self.vy

        if abs(self.vx) > 0.4:
            self._facing = 1 if self.vx > 0 else -1

        # gliding jump arc
        if self._jump_active:
            t  = self._jump_t / JUMP_DURATION
            jy = -(JUMP_HEIGHT * 1.4) * math.sin(math.pi * t)
            self.y = self._jump_base_y + jy
            self._jump_t += 1
            if self._jump_t > JUMP_DURATION:
                self._jump_active = False
                self.y = self._jump_base_y

    # ── state machine ─────────────────────────────────────────────────────────

    def _update_state(self, dist):
        speed  = math.hypot(self.vx, self.vy)
        moving = speed > 0.5

        if self._state == State.SURPRISED:
            self._surprised_t -= 1
            if self._surprised_t <= 0:
                self._set_state(State.HAPPY)
                self._happy_timer    = int(FPS * 1.6)
                self.burst_requested = True
            return

        if self._state == State.HAPPY:
            self._happy_timer -= 1
            if self._happy_timer <= 0:
                self._set_state(State.IDLE)
            return

        if dist <= CLOSE_RADIUS:
            if self._state != State.HAPPY:
                self._trigger_happy()
            return

        if moving:
            if self._state != State.WALK:
                self._set_state(State.WALK)
            self._idle_timer = 0.0
        else:
            self._idle_timer += 1 / FPS
            if self._idle_timer > SLEEP_TIMEOUT_SEC:
                if self._state != State.SLEEP:
                    self._set_state(State.SLEEP)
                    self._sound.start_purr()     # dragons rumble when sleeping
            elif self._idle_timer > IDLE_TIMEOUT_SEC:
                if self._state == State.WALK:
                    self._set_state(State.IDLE)
            elif self._state == State.SLEEP:
                self._set_state(State.IDLE)
                self._sound.stop_purr()
                self._smoke.clear()

    def _trigger_happy(self):
        if self._state in (State.HAPPY, State.SURPRISED):
            return
        if self._state == State.SLEEP:
            self._sound.stop_purr()
            self._smoke.clear()
            self._set_state(State.SURPRISED)
            self._surprised_t = 22
        else:
            self._set_state(State.HAPPY)
            self._happy_timer    = int(FPS * 2.0)
            self._start_glide()
            self.burst_requested = True
            self._sound.meow()   # roar

    def _start_glide(self):
        self._jump_active = True
        self._jump_t      = 0
        self._jump_base_y = self.y

    def _set_state(self, state: str):
        self._state      = state
        self._frame_idx  = 0
        self._frame_tick = 0

    # ── animation ─────────────────────────────────────────────────────────────

    def _update_animation(self):
        state = self._state
        rate  = WALK_FRAME_RATE if state == State.WALK else IDLE_FRAME_RATE

        self._frame_tick += 1
        if self._frame_tick >= rate:
            self._frame_tick = 0
            key   = self._anim_key()
            flist = self._frames.get(key, self._frames["idle"])
            self._frame_idx = (self._frame_idx + 1) % len(flist)

        if state in (State.IDLE, State.WALK):
            self._blink_timer += 1 / FPS
            if self._is_blinking:
                self._blink_f += 1
                if self._blink_f >= len(self._blink_frames):
                    self._is_blinking  = False
                    self._blink_timer  = 0.0
                    self._blink_target = random.uniform(*BLINK_INTERVAL_SEC)
            elif self._blink_timer >= self._blink_target:
                self._is_blinking = True
                self._blink_f     = 0

    def _anim_key(self) -> str:
        return {
            State.IDLE:      "idle",
            State.WALK:      "walk",
            State.HAPPY:     "happy",
            State.SLEEP:     "sleep",
            State.SURPRISED: "surprised",
        }.get(self._state, "idle")

    def _get_current_frame(self):
        if self._is_blinking and self._state in (State.IDLE, State.WALK):
            idx = min(self._blink_f, len(self._blink_frames) - 1)
            return self._blink_frames[idx]
        key   = self._anim_key()
        flist = self._frames.get(key, self._frames["idle"])
        return flist[self._frame_idx % len(flist)]

    # ── smoke puffs (sleep) ───────────────────────────────────────────────────

    def _update_smoke(self):
        if self._state != State.SLEEP:
            return
        self._smoke_tick += 1
        if self._smoke_tick >= 18:
            self._smoke_tick = 0
            size = int(80 * self._scale)
            sx   = int(self.x) + (14 if self._facing == 1 else -14)
            sy   = int(self.y) - size // 4
            self._smoke.append([sx, sy, 120, -0.6, 0.0])
        for p in self._smoke:
            p[1] += p[3]            # rise
            p[2] -= 2.5             # fade
            p[4] += 0.03            # drift
            p[0] += math.sin(p[4]) * 0.6
        self._smoke = [p for p in self._smoke if p[2] > 0]

    def _draw_smoke(self, screen: pygame.Surface):
        for sx, sy, alpha, *_ in self._smoke:
            r  = 6
            sh = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(sh, (200, 210, 220, int(alpha)), (r, r), r)
            screen.blit(sh, (int(sx) - r, int(sy) - r))

    # ── helpers for main.py / PawTrail ───────────────────────────────────────

    @property
    def velocity_angle(self) -> float:
        return math.atan2(self.vy, self.vx)

    @property
    def is_moving(self) -> bool:
        return math.hypot(self.vx, self.vy) > 0.6
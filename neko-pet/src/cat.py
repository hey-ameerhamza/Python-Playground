"""
cat.py — The Neko cat entity.

State machine:
    IDLE → WALK → HAPPY → SURPRISED → SLEEP → IDLE …

Physics:
    Velocity-based movement with exponential easing toward the cursor.
    A small spring model adds a satisfying overshoot / bounce feel.
"""

import math
import random
import pygame
from src.settings import (
    CAT_SPEED, CAT_ACCELERATION, CLOSE_RADIUS,
    IDLE_TIMEOUT_SEC, SLEEP_TIMEOUT_SEC, FPS,
    WALK_FRAME_RATE, IDLE_FRAME_RATE,
    BLINK_INTERVAL_SEC, TAIL_SPEED, JUMP_HEIGHT, JUMP_DURATION,
    MEOW_CHANCE,
)


class State:
    IDLE      = "idle"
    WALK      = "walk"
    HAPPY     = "happy"
    SURPRISED = "surprised"
    SLEEP     = "sleep"


class Cat:
    def __init__(self, x: float, y: float, frames: dict, sound_mgr):
        self.x   = float(x)
        self.y   = float(y)
        self.vx  = 0.0
        self.vy  = 0.0

        # visual
        self._frames     = frames
        self._state      = State.IDLE
        self._frame_idx  = 0
        self._frame_tick = 0
        self._facing     = 1          # +1 = right, -1 = left
        self._scale      = 2.0
        self._tail_phase = 0.0

        # jump
        self._jump_t      = 0
        self._jump_active = False
        self._jump_base_y = y

        # timers
        self._idle_timer    = 0.0
        self._blink_timer   = 0.0
        self._blink_target  = random.uniform(*BLINK_INTERVAL_SEC)
        self._is_blinking   = False
        self._blink_frames  = frames["blink"]
        self._blink_f       = 0
        self._happy_timer   = 0
        self._surprised_t   = 0

        # burst flag (external caller checks & resets)
        self.burst_requested = False

        self._sound = sound_mgr

    # ── public ────────────────────────────────────────────────────────────────

    @property
    def state(self) -> str:
        return self._state

    @property
    def rect(self) -> pygame.Rect:
        size = int(64 * self._scale)
        return pygame.Rect(int(self.x) - size // 2,
                           int(self.y) - size // 2, size, size)

    def update(self, mx: float, my: float, dt: float):
        dx = mx - self.x
        dy = my - self.y
        dist = math.hypot(dx, dy)

        self._update_physics(dx, dy, dist)
        self._update_state(dist)
        self._update_animation(dist)
        self._update_tail()

        # meow chance while walking
        if self._state == State.WALK and random.random() < MEOW_CHANCE:
            self._sound.meow()

    def draw(self, screen: pygame.Surface):
        frame = self._get_current_frame()
        if frame is None:
            return

        size  = int(64 * self._scale)
        frame = pygame.transform.scale(frame, (size, size))

        if self._facing == -1:
            frame = pygame.transform.flip(frame, True, False)

        # soft drop shadow
        shad = pygame.Surface((size, size // 3), pygame.SRCALPHA)
        pygame.draw.ellipse(shad, (0, 0, 0, 55), shad.get_rect())
        screen.blit(shad, (int(self.x) - size // 2,
                           int(self.y) + size // 2 - size // 8))

        screen.blit(frame, (int(self.x) - size // 2,
                            int(self.y) - size // 2))

    # ── private ───────────────────────────────────────────────────────────────

    def _update_physics(self, dx, dy, dist):
        if self._state in (State.SLEEP, State.HAPPY, State.SURPRISED):
            # dampen while in special state
            self.vx *= 0.85
            self.vy *= 0.85
            self.x  += self.vx
            self.y  += self.vy
            return

        if dist > CLOSE_RADIUS:
            # spring-style attraction
            speed    = min(CAT_SPEED, dist * 0.08)
            target_vx = (dx / dist) * speed if dist else 0
            target_vy = (dy / dist) * speed if dist else 0
            self.vx  += (target_vx - self.vx) * CAT_ACCELERATION
            self.vy  += (target_vy - self.vy) * CAT_ACCELERATION
        else:
            # brake when close
            self.vx *= 0.80
            self.vy *= 0.80

        self.x += self.vx
        self.y += self.vy

        # face direction
        if abs(self.vx) > 0.4:
            self._facing = 1 if self.vx > 0 else -1

        # jump physics overlay
        if self._jump_active:
            t  = self._jump_t / JUMP_DURATION
            dy = -JUMP_HEIGHT * math.sin(math.pi * t)
            self.y = self._jump_base_y + dy
            self._jump_t += 1
            if self._jump_t > JUMP_DURATION:
                self._jump_active = False
                self.y = self._jump_base_y

    def _update_state(self, dist):
        speed = math.hypot(self.vx, self.vy)
        moving = speed > 0.5

        if self._state == State.SURPRISED:
            self._surprised_t -= 1
            if self._surprised_t <= 0:
                self._set_state(State.HAPPY)
                self._happy_timer = FPS * 1.5
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
                    self._sound.start_purr()
            elif self._idle_timer > IDLE_TIMEOUT_SEC:
                if self._state == State.WALK:
                    self._set_state(State.IDLE)
            elif self._state == State.SLEEP:
                # woke up
                self._set_state(State.IDLE)
                self._sound.stop_purr()

    def _trigger_happy(self):
        if self._state not in (State.HAPPY, State.SURPRISED):
            if self._state == State.SLEEP:
                self._sound.stop_purr()
                self._set_state(State.SURPRISED)
                self._surprised_t = 20
            else:
                self._set_state(State.HAPPY)
                self._happy_timer = int(FPS * 1.8)
                self._start_jump()
                self.burst_requested = True
                self._sound.meow()

    def _start_jump(self):
        self._jump_active = True
        self._jump_t      = 0
        self._jump_base_y = self.y

    def _set_state(self, state: str):
        self._state      = state
        self._frame_idx  = 0
        self._frame_tick = 0

    def _update_animation(self, dist):
        state = self._state
        rate  = WALK_FRAME_RATE if state == State.WALK else IDLE_FRAME_RATE

        self._frame_tick += 1
        if self._frame_tick >= rate:
            self._frame_tick = 0
            key   = self._anim_key()
            flist = self._frames.get(key, self._frames["idle"])
            self._frame_idx = (self._frame_idx + 1) % len(flist)

        # blink overlay (only in idle/walk, not special states)
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

    def _update_tail(self):
        self._tail_phase += TAIL_SPEED

    def _anim_key(self) -> str:
        mapping = {
            State.IDLE:      "idle",
            State.WALK:      "walk",
            State.HAPPY:     "happy",
            State.SLEEP:     "sleep",
            State.SURPRISED: "surprised",
        }
        return mapping.get(self._state, "idle")

    def _get_current_frame(self):
        # blink overlay wins in idle/walk
        if self._is_blinking and self._state in (State.IDLE, State.WALK):
            idx = min(self._blink_f, len(self._blink_frames) - 1)
            return self._blink_frames[idx]

        key   = self._anim_key()
        flist = self._frames.get(key, self._frames["idle"])
        idx   = self._frame_idx % len(flist)
        return flist[idx]

    # ── velocity angle helper (used by PawTrail) ──────────────────────────────
    @property
    def velocity_angle(self) -> float:
        return math.atan2(self.vy, self.vx)

    @property
    def is_moving(self) -> bool:
        return math.hypot(self.vx, self.vy) > 0.6

"""
sound.py — Procedural sound effects (no external audio files required).

Uses numpy + pygame.sndarray to synthesise short audio clips.
Falls back silently if numpy is unavailable.
"""

import random
import math
import pygame
from src.settings import SOUND_ENABLED, PURR_VOLUME

try:
    import numpy as np
    _HAS_NUMPY = True
except ImportError:
    _HAS_NUMPY = False


SAMPLE_RATE = 22050


def _make_sound(samples: "np.ndarray") -> pygame.mixer.Sound:
    """Convert a float32 [-1,1] array into a pygame Sound."""
    data = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
    stereo = np.column_stack([data, data])
    return pygame.sndarray.make_sound(stereo)


def _sine(freq, duration, sr=SAMPLE_RATE, fade=0.05):
    n   = int(sr * duration)
    t   = np.linspace(0, duration, n, endpoint=False)
    sig = np.sin(2 * math.pi * freq * t)
    # fade in/out
    fade_n = int(sr * fade)
    env    = np.ones(n)
    env[:fade_n]  = np.linspace(0, 1, fade_n)
    env[-fade_n:] = np.linspace(1, 0, fade_n)
    return sig * env


def _meow_signal():
    """Synthesise a quirky meow sweep."""
    dur = 0.35
    n   = int(SAMPLE_RATE * dur)
    t   = np.linspace(0, dur, n, endpoint=False)
    # frequency glide: 500 → 900 → 600 Hz
    freq = 500 + 800 * np.exp(-((t - 0.1) ** 2) / 0.004)
    sig  = 0.6 * np.sin(2 * math.pi * np.cumsum(freq) / SAMPLE_RATE)
    # add overtone
    sig += 0.2 * np.sin(4 * math.pi * np.cumsum(freq) / SAMPLE_RATE)
    # envelope
    env  = np.exp(-t / 0.12)
    env *= 1 - np.exp(-t / 0.02)
    return sig * env * 0.8


def _purr_signal():
    dur = 1.0
    n   = int(SAMPLE_RATE * dur)
    t   = np.linspace(0, dur, n, endpoint=False)
    # low rumble around 25–35 Hz modulating a carrier
    mod  = 0.5 + 0.5 * np.sin(2 * math.pi * 28 * t)
    sig  = mod * 0.4 * np.sin(2 * math.pi * 120 * t)
    sig += mod * 0.2 * np.sin(2 * math.pi * 240 * t)
    # fade
    env  = np.ones(n)
    f    = int(SAMPLE_RATE * 0.12)
    env[:f]  = np.linspace(0, 1, f)
    env[-f:] = np.linspace(1, 0, f)
    return sig * env


class SoundManager:
    def __init__(self):
        self._ready   = False
        self._meows   = []
        self._purr    = None
        self._purring = False

        if not SOUND_ENABLED or not _HAS_NUMPY:
            return

        try:
            pygame.mixer.init(SAMPLE_RATE, -16, 2, 512)
            # create a few meow variants
            for _ in range(3):
                sig = _meow_signal() * random.uniform(0.7, 1.0)
                self._meows.append(_make_sound(sig))
            purr = _purr_signal()
            self._purr = _make_sound(purr)
            self._purr.set_volume(PURR_VOLUME)
            self._ready = True
        except Exception:
            pass

    # ── public ───────────────────────────────────────────────────────────────

    def meow(self):
        if not self._ready or not self._meows:
            return
        random.choice(self._meows).play()

    def start_purr(self):
        if not self._ready or self._purring or self._purr is None:
            return
        self._purr.play(loops=-1)
        self._purring = True

    def stop_purr(self):
        if not self._ready or not self._purring or self._purr is None:
            return
        self._purr.stop()
        self._purring = False

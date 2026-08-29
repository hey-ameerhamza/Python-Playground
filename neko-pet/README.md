# 🐉 Dragon Desktop Pet

A fun little project I built in Python — an animated 2D dragon that follows your mouse cursor around the screen in real time. It has smooth physics-based movement, multiple animation states, particle effects, and procedurally generated sprites and sounds (no external assets needed).

Originally started as a dragon.

---

## Demo

> Move your cursor → the dragon glides after it with spring physics  
> Get close → it reacts, spreads its wings, and breathes fire  
> Leave it alone → it sits down, then curls up and falls asleep with smoke rising from its nostrils

---

## Features

- **Spring-physics movement** — smooth easing with a natural overshoot feel, not instant teleportation
- **5 personality states** — Walk, Idle, Happy, Surprised, Sleep — each with unique animations
- **Wings** — fold at rest, half-spread while walking, fully open when happy
- **Fire breath** — shoots from the snout when startled
- **Sleeping smoke puffs** — drifts up from the nostrils with a rumble sound
- **Claw-print trail** — leaves three-talon marks as it moves
- **Colour burst particles** — explode outward when the dragon gets excited
- **Animated background** — procedural aurora shimmer, twinkling stars, and a desk surface
- **Procedural sprites** — every frame is drawn with `pygame.draw` at runtime, zero image files
- **Procedural audio** — meow/roar and purr synthesised with numpy, zero audio files
- **HUD** — mood badge, live FPS counter, custom cursor

---

## Getting Started

**Requirements:** Python 3.9+

```bash
# Install dependencies
pip install pygame numpy

# numpy is optional — only needed for sound effects

# Run
python main.py
```

---

## Controls

| Input | What happens |
|---|---|
| Move mouse | Dragon follows with smooth spring physics |
| Hover within ~80px | Dragon reacts — jumps, spreads wings, colour burst |
| Stop moving (3.5s) | Dragon sits down in idle mode |
| Stop moving (7s) | Dragon curls up and sleeps, smoke rises, rumble starts |
| Move again | Dragon wakes up and starts tracking |
| `Esc` | Quit |

---

## Project Structure

```
dragon_pet/
├── main.py                 # entry point and game loop
└── src/
    ├── settings.py         # all configurable constants in one place
    ├── dragon.py           # dragon entity — state machine + physics
    ├── dragon_assets.py    # procedural sprite generator (no image files)
    ├── cat.py           # dragon entity — state machine + physics
    ├── assets.py    # procedural sprite generator (no image files)
    ├── particles.py        # claw trail, dust motes, burst FX
    ├── background.py       # aurora + stars + desk surface
    ├── sound.py            # numpy audio synthesis
    └── ui.py               # HUD overlay
```

> It has both dragon pet & cat, dragon is default. If you want cat just swap the imports in main.py

---

## Configuration

Everything tuneable lives in `src/settings.py`:

```python
CAT_SPEED         = 4.0    # max movement speed (pixels/frame)
CAT_ACCELERATION  = 0.18   # lerp factor — higher = snappier response
CLOSE_RADIUS      = 80     # distance (px) that triggers the happy reaction
IDLE_TIMEOUT_SEC  = 3.5    # seconds of stillness before sitting
SLEEP_TIMEOUT_SEC = 7.0    # seconds before falling asleep
FPS               = 60     # target frame rate
ALWAYS_ON_TOP     = False  # True = borderless desktop-pet overlay mode
SOUND_ENABLED     = True   # set False to mute (or if numpy isn't installed)
```

---

## Switching Between Dragon and Cat

Two lines in `main.py`:

```python
# Dragon
from src.dragon_assets import load_all
from src.dragon        import Dragon as Cat

# Cat (original)
from src.assets import load_all
from src.cat    import Cat
```

---

## Desktop Pet Mode

Set `ALWAYS_ON_TOP = True` in `src/settings.py` for a borderless window you can keep floating on your desktop.

On Linux/X11 you can pair this with `xdotool` to make the window transparent. On Windows, `win32api` layered windows gets you full overlay support.

---

## Dependencies

| Package | Required | Purpose |
|---|---|---|
| `pygame` | Yes | Window, rendering, input handling |
| `numpy` | Optional | Procedural sound synthesis |

```bash
pip install pygame numpy
```

---

## Why I built this

I wanted to experiment with sprite-less game dev — drawing everything procedurally with `pygame.draw` so there are literally zero asset files to manage. Also state machines for character behaviour are fun to think about. The dragon was a natural upgrade from the cat because it let me add wings, fire, and smoke which are all just math.

---

## Support me

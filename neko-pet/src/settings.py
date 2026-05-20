# ============================================================
#  Neko Desktop Pet — Settings
# ============================================================

# Window
WINDOW_TITLE   = "Neko — Desktop Pet"
WINDOW_WIDTH   = 900
WINDOW_HEIGHT  = 650
FPS            = 60
ALWAYS_ON_TOP  = False          # set True for desktop-pet overlay mode

# Cat physics
CAT_SPEED          = 4.0        # max pixels/frame
CAT_ACCELERATION   = 0.18       # lerp factor (0=frozen, 1=instant)
CLOSE_RADIUS       = 80         # pixels — "happy/react" zone
IDLE_TIMEOUT_SEC   = 3.5        # seconds until sleep animation starts
SLEEP_TIMEOUT_SEC  = 7.0        # seconds until deep-sleep

# Animation
WALK_FRAME_RATE    = 8          # frames per animation frame (walk cycle)
IDLE_FRAME_RATE    = 15
BLINK_INTERVAL_SEC = (2.5, 5.5) # random range between blinks
TAIL_SPEED         = 0.06       # tail wag oscillation speed
JUMP_HEIGHT        = 55         # pixels
JUMP_DURATION      = 28         # frames

# Particles
MAX_PAW_PRINTS     = 60
PAW_FADE_SPEED     = 4          # alpha dec per frame
PAW_INTERVAL       = 22         # frames between paw prints

# Background
BG_PARTICLE_COUNT  = 38         # floating dust motes
BG_SCROLL_SPEED    = 0.25

# Colours  (R, G, B)
COL_BG_TOP         = (20,  24,  48)
COL_BG_BOT         = (38,  18,  62)
COL_ACCENT         = (255, 105, 180)
COL_SHADOW         = (0,   0,   0,  80)   # RGBA

# Sound (optional — set False to mute)
SOUND_ENABLED      = True
MEOW_CHANCE        = 0.003      # probability per frame when walking
PURR_VOLUME        = 0.4

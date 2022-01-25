#SRC += altlocal_keys.c

OLED_ENABLE = no
#OLED_DRIVER = SSD1306   # Enables the use of OLED displays
ENCODER_ENABLE = no       # Enables the use of one or more encoders
RGBLIGHT_ENABLE = yes      # Enable keyboard RGB underglow
VIA_ENABLE = yes
VIAL_ENABLE = yes
VIAL_ENCODERS_ENABLE = no
VIAL_INSECURE = yes

#turn any of these on if needed
KEY_LOCK_ENABLE = no
SPACE_CADET_ENABLE = no
MAGIC_ENABLE = no
GRAVE_ESCAPE_ENABLE = no
COMBO_ENABLE = no
TAP_DANCE_ENABLE = no
AUDIO_ENABLE = no

LTO_ENABLE = yes
QMK_SETTINGS = no
NKRO_ENABLE = yes
KEY_OVERRIDE_ENABLE = yes

DEBOUNCE_TYPE = asym_eager_defer_pk #sym_eager_pk

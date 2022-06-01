/* Copyright 2019 Thomas Baart <thomas@splitkb.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

#pragma once

#define VIAL_KEYBOARD_UID {0xA6, 0x05, 0xA6, 0xA4, 0x05, 0xE0, 0x34, 0x37}
  
#define LAYER_STATE_8BIT
#define DYNAMIC_KEYMAP_LAYER_COUNT 6

#define HOLD_ON_OTHER_KEY_PRESS_PER_KEY
#define TAPPING_TERM 200
#define TAPPING_TERM_PER_KEY
//#define TAPPING_FORCE_HOLD
//#define RETRO_TAPPING
//#define PERMISSIVE_HOLD

//#define RETRO_SHIFT
// #define MOUSEKEY_INTERVAL 16

// #define MOUSEKEY_DELAY 0
// #define MOUSEKEY_TIME_TO_MAX 60S
// #define MOUSEKEY_MAX_SPEED 7
// #define MOUSEKEY_WHEEL_DELAY 0
 
#undef LOCKING_SUPPORT_ENABLE
#undef LOCKING_RESYNC_ENABLE

#ifdef RGBLIGHT_ENABLE
#    define RGBLIGHT_EFFECT_RAINBOW_MOOD
#    define RGBLIGHT_EFFECT_RAINBOW_SWIRL
#    define RGBLIGHT_EFFECT_STATIC_GRADIENT
//#    define RGBLIGHT_SPLIT //try out split rgb thing

#    define RGBLIGHT_HUE_STEP 8
#    define RGBLIGHT_SAT_STEP 8
#    define RGBLIGHT_VAL_STEP 8
#    define RGBLIGHT_LIMIT_VAL 150

#    define RGBLIGHT_LAYERS
#    define RGBLIGHT_LAYERS_OVERRIDE_RGB_OFF
#endif

#ifdef RGB_MATRIX_ENABLE
// rgb matrix modes. cycle these with RGB_MOD
#    define ENABLE_RGB_MATRIX_CYCLE_LEFT_RIGHT
#    define ENABLE_RGB_MATRIX_CYCLE_OUT_IN_DUAL
#    define ENABLE_RGB_MATRIX_CYCLE_OUT_IN

#    define SPLIT_LAYER_STATE_ENABLE
#    define SPLIT_LED_STATE_ENABLE
//#    undef SPLIT_TRANSPORT_MIRROR

#    define VIALRGB_NO_DIRECT
#endif

#define MASTER_LEFT
#define USB_POLLING_INTERVAL_MS 1
#undef DEBOUNCE
#define DEBOUNCE 3
#define FORCE_NKRO
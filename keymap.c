#include QMK_KEYBOARD_H
#include "my_slovak_keymap.h"

enum layers {
    _QWERTZ = 0,
    _ACCENTS,
    _NAV,
    _SYM,
    _FUNCTION,
    _ADJUST,
};

#define USER00 0x5F80  // this is important so vial can recognize these keys
#include "keymap.h"
enum custom_keycodes { 
  E_ACUTE = /*SAFE_RANGE*/ USER00, 
  R_ACUTE, 
  U_ACUTE, 
  I_ACUTE, 
  O_ACUTE, 
  A_ACUTE, 
  A_DIA, 
  L_ACUTE, 
  Y_ACUTE, 
  T_CARON, 
  Z_CARON, 
  O_CARON, 
  S_CARON, 
  D_CARON, 
  L_CARON, 
  C_CARON, 
  N_CARON, 
  U_UMLAU, 
  O_UMLAU, 
  O_CCIRC, 
  KC_DEEZ, 
  ALT_LOCAL_KEYS_END 
};

#define ALT_LOCAL_KEYS_START O_CCIRC

// put alt local (odd unshifted and shifted pairs.) keys in here.
// Aliases for readability
#define QWERTZ DF(_QWERTZ)
#define ACCENTS OSL(_ACCENTS)
#define SYM MO(_SYM)
#define NAV MO(_NAV)
#define FKEYS MO(_FUNCTION)
#define ADJUST MO(_ADJUST)

#define CTL_ESC MT(MOD_LCTL, KC_ESC)
#define CTL_QUOT MT(MOD_RCTL, SK_SECT)
#define ALT_ENT MT(MOD_LALT, KC_ENT)

//#define A_DIA SK_ADIA
#define O_CIRC SK_OCIR

// accent modifier aliases for eurkey/sk layout

//eurkey. requires you have https://eurkey.steffen.bruentjen.eu/layout.html (tested with eurkey 1.3)
#define A_DIA	RALT(KC_A)
#define SHARP_S RALT(KC_S)
#define AC_ACUT	RALT(KC_QUOTE)
#define AC_DIAE	RALT(S(KC_QUOTE))
#define AC_CARN RALT(S(KC_6))
#define AC_CIRC RALT(KC_6)

//for sk keymap. only have one of these uncommented at a time.
// #define A_DIA KC_RBRACKET
// #define SHARP_S RALT(KC_QUOTE)
// #define AC_ACUT KC_EQUAL
// #define AC_DIAE SK_DIAE
// #define AC_CARN S(KC_EQUAL)
// #define AC_CIRC SK_CIRC

// these layers don't really matter rn because i overwrite them in vial. check v14.vil for more info until i make a script to hardcode the layout here bc it's better than using EEPROM for layout

// Note: LAlt/Enter (ALT_ENT) is not the same thing as the keyboard shortcut Alt+Enter.
// The notation `mod/tap` denotes a key that activates the modifier `mod` when held down, and
// produces the key `tap` when tapped (i.e. pressed and released).

// clang-format off
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
/* ┌──────┬──────┬──────┬──────┬──────┬──────┐                              ┌──────┬──────┬──────┬──────┬──────┬──────┐
 * │ TAB  │  Q   │  W   │  E   │  R   │  T   │                              │  Z   │  U   │  I   │  O   │  P   │AltGr │
 * ├──────┼──────┼──────┼──────┼──────┼──────┤                              ├──────┼──────┼──────┼──────┼──────┼──────┤
 * │ESC/⎈ │  A   │  S   │  D   │  F   │  G   │                              │  H   │  J   │  K   │  L   │  Ô   │' "/⎈ │
 * ├──────┼──────┼──────┼──────┼──────┼──────┼──────┬──────┐  ┌──────┬──────┼──────┼──────┼──────┼──────┼──────┼──────┤
 * │LSFT ⇧│  Y   │  X   │  C   │  V   │  B   │  [   │ CAPS │  │FKEYS │  ]   │  N   │  M   │ , <  │ . >  │ - _  │RSFT ⇧│
 * └──────┴──────┴──────┼──────┼──────┼──────┼──────┼──────┤  ├──────┼──────┼──────┼──────┼──────┼──────┴──────┴──────┘
 *                      │ADJUST│LGUI ◆│ ⏎ /⎇ │ SPC  │ SYM  │  │ NAV  │ BSPC │ACCENT│RGUI ◆│ MENU │
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      └──────┴──────┴──────┴──────┴──────┘  └──────┴──────┴──────┴──────┴──────┘
 *                                                                               generated by [keymapviz] */
    [_QWERTZ] = LAYOUT(
     KC_TAB  , SK_Q  ,  SK_W   ,  SK_E  ,   SK_R ,   SK_T ,                                        SK_Z,   SK_U ,  SK_I ,   SK_O ,  SK_P , KC_RALT,
     CTL_ESC , SK_A  ,  SK_S   ,  SK_D  ,   SK_F ,   SK_G ,                                        SK_H,   SK_J ,  SK_K ,   SK_L , O_CIRC,CTL_QUOT,
     KC_LSFT , SK_Y  ,  SK_X   ,  SK_C  ,   SK_V ,   SK_B , SK_LBRC,KC_CAPS,     FKEYS  , SK_RBRC, SK_N,   SK_M ,SK_COMM, SK_DOT ,SK_MINS, KC_RSFT,
                                 ADJUST , KC_LGUI, ALT_ENT, KC_SPC , SYM   ,     NAV    , KC_BSPC,ACCENTS, KC_RGUI, KC_APP
    ),

/* ┌──────┬──────┬──────┬──────┬──────┬──────┐                              ┌──────┬──────┬──────┬──────┬──────┬──────┐
 * │      │  Ä   │      │  É   │  Ŕ   │  Ť   │                              │  Ž   │  Ú   │  Í   │  Ó   │  Ǒ   │      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┤                              ├──────┼──────┼──────┼──────┼──────┼──────┤
 * │      │  Á   │  Š   │  Ď   │  Ü   │      │                              │      │      │  Ľ   │  Ĺ   │  Ô   │      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┼──────┬──────┐  ┌──────┬──────┼──────┼──────┼──────┼──────┼──────┼──────┤
 * │      │  Ý   │  ß   │  Č   │  Ö   │      │      │      │  │      │      │  Ň   │      │      │      │      │      │
 * └──────┴──────┴──────┼──────┼──────┼──────┼──────┼──────┤  ├──────┼──────┼──────┼──────┼──────┼──────┴──────┴──────┘
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      └──────┴──────┴──────┴──────┴──────┘  └──────┴──────┴──────┴──────┴──────┘
 *                                                                               generated by [keymapviz] */
    [_ACCENTS] = LAYOUT(
     _______ , A_DIA , _______ , E_ACUTE, R_ACUTE, T_CARON,                                       Y_ACUTE, U_ACUTE,I_ACUTE, O_ACUTE,O_CARON, _______,
     _______ ,A_ACUTE, S_CARON , D_CARON, U_UMLAU, _______,                                       _______, _______,L_CARON, L_ACUTE,O_CCIRC, _______,
     _______ ,Z_CARON, SHARP_S , C_CARON, O_UMLAU, _______, _______,_______,     _______, _______,N_CARON, _______,_______, _______,_______, _______,
                                 _______, _______, _______, _______,_______,     _______, _______,_______, _______, _______
    ),


/* ┌──────┬──────┬──────┬──────┬──────┬──────┐                              ┌──────┬──────┬──────┬──────┬──────┬──────┐
 * │ DEL  │ VOLU │ END  │  UP  │ HOME │ PGUP │                              │      │      │      │      │      │      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┤                              ├──────┼──────┼──────┼──────┼──────┼──────┤
 * │ Ins  │ VOLD │ LEFT │ DOWN │RIGHT │ PGDN │                              │      │RSFT ⇧│RCTL ⎈│LALT ⎇│RGUI ◆│      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┼──────┬──────┐  ┌──────┬──────┼──────┼──────┼──────┼──────┼──────┼──────┤
 * │PrintS│ MUTE │ MPRV │ MPLY │ MNXT │PAUSE │      │ScrLoc│  │      │      │      │      │      │      │      │      │
 * └──────┴──────┴──────┼──────┼──────┼──────┼──────┼──────┤  ├──────┼──────┼──────┼──────┼──────┼──────┴──────┴──────┘
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      └──────┴──────┴──────┴──────┴──────┘  └──────┴──────┴──────┴──────┴──────┘
 *                                                                               generated by [keymapviz] */
    [_NAV] = LAYOUT(
      KC_DEL , KC_VOLU, KC_END  ,KC_UP  ,KC_HOME ,KC_PGUP ,                                     _______, _______, _______, _______, _______, _______,
      KC_INS , KC_VOLD, KC_LEFT ,KC_DOWN,KC_RIGHT,KC_PGDN ,                                     _______, KC_RSFT, KC_RCTL, KC_LALT, KC_RGUI, _______,
      KC_PSCR, KC_MUTE, KC_MPRV, KC_MPLY, KC_MNXT,KC_PAUSE, _______, KC_SLCK, _______, _______, _______, _______, _______, _______, _______, _______,
                                 _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
    ),

/* ┌──────┬──────┬──────┬──────┬──────┬──────┐                              ┌──────┬──────┬──────┬──────┬──────┬──────┐
 * │  `   │  1   │  2   │  3   │  4   │  5   │                              │  6   │  7   │  8   │  9   │  0   │  =   │
 * ├──────┼──────┼──────┼──────┼──────┼──────┤                              ├──────┼──────┼──────┼──────┼──────┼──────┤
 * │  ~   │  !   │  @   │  #   │  $   │  %   │                              │  ^   │  &   │  *   │  (   │  )   │  +   │
 * ├──────┼──────┼──────┼──────┼──────┼──────┼──────┬──────┐  ┌──────┬──────┼──────┼──────┼──────┼──────┼──────┼──────┤
 * │  |   │ \ |  │  :   │ : ;  │ - _  │  [   │  {   │      │  │      │  }   │  ]   │  _   │ , <  │ . >  │ / ?  │ ? !  │
 * └──────┴──────┴──────┼──────┼──────┼──────┼──────┼──────┤  ├──────┼──────┼──────┼──────┼──────┼──────┴──────┴──────┘
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      └──────┴──────┴──────┴──────┴──────┘  └──────┴──────┴──────┴──────┴──────┘
 *                                                                               generated by [keymapviz] */
    [_SYM] = LAYOUT(
      SK_GRV ,   SK_1 ,   SK_2 ,   SK_3 ,   SK_4 ,   SK_5 ,                                       SK_6 ,   SK_7 ,   SK_8 ,   SK_9 ,   SK_0 , SK_EQL ,
     SK_TILD , SK_EXLM,  SK_AT , SK_HASH,  SK_DLR, SK_PERC,                                     SK_CIRC, SK_AMPR, SK_ASTR, SK_LPRN, SK_RPRN, SK_PLUS,
     SK_PIPE , SK_BSLS, SK_COLN, SK_SCLN, SK_MINS, SK_LBRC, SK_LCBR, _______, _______, SK_RCBR, SK_RBRC, SK_UNDS, SK_COMM,  SK_DOT, SK_SLSH, SK_QUES,
                                 _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
    ),

/* ┌──────┬──────┬──────┬──────┬──────┬──────┐                              ┌──────┬──────┬──────┬──────┬──────┬──────┐
 * │      │  F9  │ F10  │ F11  │ F12  │      │                              │      │      │      │      │      │      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┤                              ├──────┼──────┼──────┼──────┼──────┼──────┤
 * │      │  F5  │  F6  │  F7  │  F8  │      │                              │      │RSFT ⇧│RCTL ⎈│LALT ⎇│RGUI ◆│      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┼──────┬──────┐  ┌──────┬──────┼──────┼──────┼──────┼──────┼──────┼──────┤
 * │      │  F1  │  F2  │  F3  │  F4  │      │      │      │  │      │      │      │      │      │      │      │      │
 * └──────┴──────┴──────┼──────┼──────┼──────┼──────┼──────┤  ├──────┼──────┼──────┼──────┼──────┼──────┴──────┴──────┘
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      └──────┴──────┴──────┴──────┴──────┘  └──────┴──────┴──────┴──────┴──────┘
 *                                                                               generated by [keymapviz] */
    [_FUNCTION] = LAYOUT(
      _______,  KC_F9 ,  KC_F10,  KC_F11,  KC_F12, _______,                                     _______, _______, _______, _______, _______, _______,
      _______,  KC_F5 ,  KC_F6 ,  KC_F7 ,  KC_F8 , _______,                                     _______, KC_RSFT, KC_RCTL, KC_LALT, KC_RGUI, _______,
      _______,  KC_F1 ,  KC_F2 ,  KC_F3 ,  KC_F4 , _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
                                 _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
    ),

/* ┌──────┬──────┬──────┬──────┬──────┬──────┐                              ┌──────┬──────┬──────┬──────┬──────┬──────┐
 * │      │      │      │      │      │      │                              │      │      │      │      │      │      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┤                              ├──────┼──────┼──────┼──────┼──────┼──────┤
 * │      │      │      │      │      │      │                              │RGB_TO│RGB_SA│RGB_HU│RGB_VA│RGB_MO│      │
 * ├──────┼──────┼──────┼──────┼──────┼──────┼──────┬──────┐  ┌──────┬──────┼──────┼──────┼──────┼──────┼──────┼──────┤
 * │      │      │      │      │      │      │      │      │  │      │      │      │RGB_SA│RGB_HU│RGB_VA│RGB_RM│      │
 * └──────┴──────┴──────┼──────┼──────┼──────┼──────┼──────┤  ├──────┼──────┼──────┼──────┼──────┼──────┴──────┴──────┘
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      │      │      │      │      │      │  │      │      │      │      │      │
 *                      └──────┴──────┴──────┴──────┴──────┘  └──────┴──────┴──────┴──────┴──────┘
 *                                                                               generated by [keymapviz] */
    [_ADJUST] = LAYOUT(
      _______, _______, _______, _______, _______, _______,                                     _______, _______, _______, _______,  _______, _______,
      _______, _______, _______, _______, _______, _______,                                     RGB_TOG, RGB_SAI, RGB_HUI, RGB_VAI,  RGB_MOD, _______,
      _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, RGB_SAD, RGB_HUD, RGB_VAD, RGB_RMOD, _______,
                                 _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
    ),

// /*
//  * Layer template
//  *
//  * ,-------------------------------------------.                              ,-------------------------------------------.
//  * |        |      |      |      |      |      |                              |      |      |      |      |      |        |
//  * |--------+------+------+------+------+------|                              |------+------+------+------+------+--------|
//  * |        |      |      |      |      |      |                              |      |      |      |      |      |        |
//  * |--------+------+------+------+------+------+-------------.  ,-------------+------+------+------+------+------+--------|
//  * |        |      |      |      |      |      |      |      |  |      |      |      |      |      |      |      |        |
//  * `----------------------+------+------+------+------+------|  |------+------+------+------+------+----------------------'
//  *                        |      |      |      |      |      |  |      |      |      |      |      |
//  *                        |      |      |      |      |      |  |      |      |      |      |      |
//  *                        `----------------------------------'  `----------------------------------'
//  */
//     [_LAYERINDEX] = LAYOUT(
//       _______, _______, _______, _______, _______, _______,                                     _______, _______, _______, _______, _______, _______,
//       _______, _______, _______, _______, _______, _______,                                     _______, _______, _______, _______, _______, _______,
//       _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______, _______,
//                                  _______, _______, _______, _______, _______, _______, _______, _______, _______, _______
//     ),
};

/*
uint8_t gr(uint16_t);
void send_keycode(uint16_t);
bool process_alt_local_key(uint16_t keycode, keyrecord_t* record);
*/

#define MOD_NONE 0x00

#define GR(x) (x-/*SAFE_RANGE*/0x5F80)
// indexs for the keycode translation table.


#define MK_KEY(KCNAME, KC1, MOD1, KC2, MOD2)    \
  [GR(KCNAME)] = {{KC1, MOD1}, {KC2, MOD2}},

const uint16_t key_translations[][2][2] = {
#include "altlocal_keys.def"
};

#define UNSHIFTED_KEY(key)  key_translations[gr(key)][0][0]
#define UNSHIFTED_MODS(key) key_translations[gr(key)][0][1]
#define SHIFTED_KEY(key)    key_translations[gr(key)][1][0]
#define SHIFTED_MODS(key)   key_translations[gr(key)][1][1]

uint8_t gr(uint16_t kc){
  return (kc - /*SAFE_RANGE*/0x5F80);
}

// update this value if we're using more than 255 altlocal keys
//bool key_tracker[0xFF] = 0

// send the right keycode for the right mod.
// remove the mods we are taking care of,
// send our keycodes then restore them.
// all so we can make dvorak keys from bepo keycodes.
static inline void send_keycode(uint16_t kc){
  uint8_t tmp_mods = get_mods();
  bool is_shifted = ( tmp_mods & (MOD_BIT(KC_LSFT)|MOD_BIT(KC_RSFT)) );

  // need to turn of the shift if it is on.
  unregister_mods((MOD_BIT(KC_LSFT)|MOD_BIT(KC_RSFT)));
  if(is_shifted){
    register_mods(SHIFTED_MODS(kc));
    register_code(SHIFTED_KEY(kc));
    unregister_code(SHIFTED_KEY(kc));
    unregister_mods(SHIFTED_MODS(kc));
  } else{
    register_mods(UNSHIFTED_MODS(kc));
    register_code(UNSHIFTED_KEY(kc));
    unregister_code(UNSHIFTED_KEY(kc));
    unregister_mods(UNSHIFTED_MODS(kc));
  }
  clear_mods();
  register_mods(tmp_mods);
}

static inline void tap_accented_letter(uint16_t letter, uint16_t dead_key) {
    uint8_t mod_state = get_mods();
    uint8_t oneshot_mod_state = get_oneshot_mods();
    del_mods(MOD_MASK_SHIFT);
    del_oneshot_mods(MOD_MASK_SHIFT);
    tap_code16(dead_key);
    set_mods(mod_state);
    set_oneshot_mods(oneshot_mod_state);
    tap_code(letter);
}


// functional equivalent to case.
/*bool process_alt_local_key(uint16_t keycode, keyrecord_t* record) {
  switch(keycode){
  case ALT_LOCAL_KEYS_START+1 ... ALT_LOCAL_KEYS_END-1:
    if(record->event.pressed)
      send_keycode(keycode);
    unregister_code(keycode);
    break;
  }
  return (true);
}*/

bool process_record_user(uint16_t keycode, keyrecord_t* record) {

  // if (!process_alt_local_key(keycode, record)) { return false; }

  switch (keycode) {

  case ALT_LOCAL_KEYS_START+1 ... ALT_LOCAL_KEYS_END-1:
    if(record->event.pressed){
      send_keycode(keycode);
    unregister_code(keycode);
    }
    return false;

  case E_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_E, AC_ACUT);
    }
    return false;

  case R_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_R, AC_ACUT);
    }
    return false;

  case U_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_U, AC_ACUT);
    }
    return false;

  case I_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_I, AC_ACUT);
    }
    return false;

  case O_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_O, AC_ACUT);
    }
    return false;

  case A_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_A, AC_ACUT);
    }
    return false;

  case L_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_L, AC_ACUT);
    }
    return false;

  case Y_ACUTE:
    if (record->event.pressed) {
      tap_accented_letter(SK_Z, AC_ACUT);
    }
    return false;

  case T_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_T, AC_CARN);
    }
    return false;

  case Z_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_Y, AC_CARN);
    }
    return false;

  case O_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_O, AC_CARN);
    }
    return false;

  case S_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_S, AC_CARN);
    }
    return false;

  case D_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_D, AC_CARN);
    }
    return false;

  case L_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_L, AC_CARN);
    }
    return false;

  case C_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_C, AC_CARN);
    }
    return false;

  case N_CARON:
    if (record->event.pressed) {
      tap_accented_letter(SK_N, AC_CARN);
    }
    return false;

  case U_UMLAU:
    if (record->event.pressed) {
      tap_accented_letter(SK_U, AC_DIAE);
    }
    return false;

  case O_UMLAU:
    if (record->event.pressed) {
      tap_accented_letter(SK_O, AC_DIAE);
    }
    return false;

  case A_DIA:
    if (record->event.pressed) {
      tap_accented_letter(SK_A, AC_DIAE);
    }
    return false;

  case O_CCIRC: // napis o s vokanom cez vokan rather than normalne aby sa dalo velke uo
    if (record->event.pressed) {
      tap_accented_letter(SK_O, AC_CIRC);
    }
    return false;

  }
  return true;
}

/* The default OLED and rotary encoder code can be found at the bottom of qmk_firmware/keyboards/splitkb/kyria/rev1/rev1.c
 * These default settings can be overriden by your own settings in your keymap.c
 * For your convenience, here's a copy of those settings so that you can uncomment them if you wish to apply your own modifications.
 * DO NOT edit the rev1.c file; instead override the weakly defined default functions by your own.
 */

#ifdef OLED_ENABLE
oled_rotation_t oled_init_user(oled_rotation_t rotation) { return OLED_ROTATION_180; }

bool oled_task_user(void) {
    if (is_keyboard_master()) {
        // QMK Logo and version information
        // clang-format off
        static const char PROGMEM qmk_logo[] = {
            0x80,0x81,0x82,0x83,0x84,0x85,0x86,0x87,0x88,0x89,0x8a,0x8b,0x8c,0x8d,0x8e,0x8f,0x90,0x91,0x92,0x93,0x94,
            0xa0,0xa1,0xa2,0xa3,0xa4,0xa5,0xa6,0xa7,0xa8,0xa9,0xaa,0xab,0xac,0xad,0xae,0xaf,0xb0,0xb1,0xb2,0xb3,0xb4,
            0xc0,0xc1,0xc2,0xc3,0xc4,0xc5,0xc6,0xc7,0xc8,0xc9,0xca,0xcb,0xcc,0xcd,0xce,0xcf,0xd0,0xd1,0xd2,0xd3,0xd4,0};
        // clang-format on

        oled_write_P(qmk_logo, false);
        oled_write_P(PSTR("Kyria rev2.0\n\n"), false);

        // Host Keyboard Layer Status
        oled_write_P(PSTR("Layer: "), false);
        switch (get_highest_layer(layer_state | default_layer_state)) {
            case _QWERTZ:
                oled_write_P(PSTR("QWERTZ\n"), false);
                break;
            case _ACCENTS:
                oled_write_P(PSTR("ACCENTS\n"), false);
                break;
            case _NAV:
                oled_write_P(PSTR("Nav\n"), false);
                break;
            case _SYM:
                oled_write_P(PSTR("Sym\n"), false);
                break;
            case _FUNCTION:
                oled_write_P(PSTR("Function\n"), false);
                break;
            case _ADJUST:
                oled_write_P(PSTR("Adjust\n"), false);
                break;
            default:
                oled_write_P(PSTR("Undefined\n"), false);
        }

        // Write host Keyboard LED Status to OLEDs
        led_t led_usb_state = host_keyboard_led_state();
        oled_write_P(led_usb_state.num_lock ? PSTR("NUMLCK ") : PSTR("       "), false);
        oled_write_P(led_usb_state.caps_lock ? PSTR("CAPLCK ") : PSTR("       "), false);
        oled_write_P(led_usb_state.scroll_lock ? PSTR("SCRLCK ") : PSTR("       "), false);
    } else {
        // clang-format off
        static const char PROGMEM kyria_logo[] = {
            0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,128,128,192,224,240,112,120, 56, 60, 28, 30, 14, 14, 14,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7,  7, 14, 14, 14, 30, 28, 60, 56,120,112,240,224,192,128,128,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            0,  0,  0,  0,  0,  0,  0,192,224,240,124, 62, 31, 15,  7,  3,  1,128,192,224,240,120, 56, 60, 28, 30, 14, 14,  7,  7,135,231,127, 31,255,255, 31,127,231,135,  7,  7, 14, 14, 30, 28, 60, 56,120,240,224,192,128,  1,  3,  7, 15, 31, 62,124,240,224,192,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            0,  0,  0,  0,240,252,255, 31,  7,  1,  0,  0,192,240,252,254,255,247,243,177,176, 48, 48, 48, 48, 48, 48, 48,120,254,135,  1,  0,  0,255,255,  0,  0,  1,135,254,120, 48, 48, 48, 48, 48, 48, 48,176,177,243,247,255,254,252,240,192,  0,  0,  1,  7, 31,255,252,240,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            0,  0,  0,255,255,255,  0,  0,  0,  0,  0,254,255,255,  1,  1,  7, 30,120,225,129,131,131,134,134,140,140,152,152,177,183,254,248,224,255,255,224,248,254,183,177,152,152,140,140,134,134,131,131,129,225,120, 30,  7,  1,  1,255,255,254,  0,  0,  0,  0,  0,255,255,255,  0,  0,  0,  0,255,255,  0,  0,192,192, 48, 48,  0,  0,240,240,  0,  0,  0,  0,  0,  0,240,240,  0,  0,240,240,192,192, 48, 48, 48, 48,192,192,  0,  0, 48, 48,243,243,  0,  0,  0,  0,  0,  0, 48, 48, 48, 48, 48, 48,192,192,  0,  0,  0,  0,  0,
            0,  0,  0,255,255,255,  0,  0,  0,  0,  0,127,255,255,128,128,224,120, 30,135,129,193,193, 97, 97, 49, 49, 25, 25,141,237,127, 31,  7,255,255,  7, 31,127,237,141, 25, 25, 49, 49, 97, 97,193,193,129,135, 30,120,224,128,128,255,255,127,  0,  0,  0,  0,  0,255,255,255,  0,  0,  0,  0, 63, 63,  3,  3, 12, 12, 48, 48,  0,  0,  0,  0, 51, 51, 51, 51, 51, 51, 15, 15,  0,  0, 63, 63,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 48, 48, 63, 63, 48, 48,  0,  0, 12, 12, 51, 51, 51, 51, 51, 51, 63, 63,  0,  0,  0,  0,  0,
            0,  0,  0,  0, 15, 63,255,248,224,128,  0,  0,  3, 15, 63,127,255,239,207,141, 13, 12, 12, 12, 12, 12, 12, 12, 30,127,225,128,  0,  0,255,255,  0,  0,128,225,127, 30, 12, 12, 12, 12, 12, 12, 12, 13,141,207,239,255,127, 63, 15,  3,  0,  0,128,224,248,255, 63, 15,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            0,  0,  0,  0,  0,  0,  0,  3,  7, 15, 62,124,248,240,224,192,128,  1,  3,  7, 15, 30, 28, 60, 56,120,112,112,224,224,225,231,254,248,255,255,248,254,231,225,224,224,112,112,120, 56, 60, 28, 30, 15,  7,  3,  1,128,192,224,240,248,124, 62, 15,  7,  3,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
            0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  3,  7, 15, 14, 30, 28, 60, 56,120,112,112,112,224,224,224,224,224,224,224,224,224,224,224,224,224,224,224,224,112,112,112,120, 56, 60, 28, 30, 14, 15,  7,  3,  1,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
        };
        // clang-format on
        oled_write_raw_P(kyria_logo, sizeof(kyria_logo));
    }
    return false;
}
#endif

#ifdef ENCODER_ENABLE
bool encoder_update_user(uint8_t index, bool clockwise) {
    if (index == 0) {
        // Volume control
        if (clockwise) {
            tap_code(KC_VOLU);
        } else {
            tap_code(KC_VOLD);
        }
    } else if (index == 1) {
        // Page up/Page down
        if (clockwise) {
            tap_code(KC_PGDN);
        } else {
            tap_code(KC_PGUP);
        }
    }
    return false;
}
#endif

// key overrides by kraXen
// const key_override_t delete_key_override = ko_make_basic(MOD_MASK_SHIFT, KC_BSPC, KC_DEL); //ctrl + backspace = delete
const key_override_t redo_key_override = ko_make_with_layers_and_negmods(MOD_MASK_CTRL, KC_ESCAPE, LCTL(KC_Y), ~0, MOD_MASK_SHIFT);  // ctrl + escape = ctrl + y for quick redo when editing something

// This globally defines all key overrides to be used
const key_override_t **key_overrides = (const key_override_t *[]){
    //&delete_key_override,
    &redo_key_override,
    NULL  // Null terminate the array of overrides!
};

#ifdef RGB_MATRIX_ENABLE
// wait until https://github.com/qmk/qmk_firmware/pull/15985 gets merged, then i can remove the is keyboard left checks
void rgb_matrix_indicators_user(void) {
    if (host_keyboard_led_state().caps_lock) {
        if (is_keyboard_left()) {
            rgb_matrix_set_color(8, RGB_WHITE);
        }
    }

    switch (get_highest_layer(layer_state | default_layer_state)) {
        case _NAV:
            if (is_keyboard_left()) {
                rgb_matrix_set_color(0, RGB_RED);
                rgb_matrix_set_color(1, RGB_RED);
            }
            break;
        case _SYM:
            if (!is_keyboard_left()) {
                rgb_matrix_set_color(10, RGB_GREEN);
                rgb_matrix_set_color(11, RGB_GREEN);
            }
            break;
        default:
            break;
    }
}
#endif

//tapping term: make the right enter be almost exclusively a lt
uint16_t get_tapping_term(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case LT(5, KC_ENTER):
            return 168;
        default:
            return TAPPING_TERM;
    }
}
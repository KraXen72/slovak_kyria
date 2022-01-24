/* Copyright 2020
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
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

// not sure where this was defined. keeping it
// because this is not mine.  - Eric.
#define USER00 SAFE_RANGE

#include "keymap.h"
enum custom_keycodes {
  E_ACUTE = /*SAFE_RANGE*/USER00,
  R_ACUTE,
  U_ACUTE,
  I_ACUTE,
  O_ACUTE,
  A_ACUTE,
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
  // put alt local (odd unshifted and shifted pairs.) keys in here.
  ALT_LOCAL_KEYS_START,
  SOME_KEY,
  ALT_LOCAL_KEYS_END
};

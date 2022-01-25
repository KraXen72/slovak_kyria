import json
from urllib.request import urlopen
from os.path import exists

# change this to match your keyboard. support for multiple keyboards soontm
keyboard_cols_per_half = 8
keyboard_rows_per_half = 4
keyboard_halves = 2

print("hello. this is KraXen's VIAL/QMK helper cli")
print("the commands are: ")

commands = [
    "genkey: generate vial customKeycodes from keymap.c",
    "viltokey: convert a .vil vial file into c code",
    "fetchkeys: fetch qmk's github to get aliases for keys",
    "--------------------",
    "quit: quit the app",
    "help: show this message"
]

longchar_defines = []

def find_keycodes(lines):
    start = -1
    end = -1
    for line in lines:
        if "custom_keycodes" in line:
            start = lines.index(line)
            break
    lines = lines[start:]
    for line in lines:
        if "}" in line:
            end = lines.index(line)
            break

    lines = lines[:end + 1][1:-1]
    keycodes = []
    for line in lines:
        keycode = line.replace(" ", "")
        if "=" in line:
            keycode = keycode.split("=")[0]
        else:
            keycode = line.split(",")[0]

        # {"name": "E./", "title": "E ACUTE", "shortName": "E_ACUTE"}
        # TODO when vial supports unicode, redo this into proper unicode characters
        name = keycode.replace(" ", "")
        if "ALT_LOCAL_KEYS" in name:
            continue
        elif "_ACUTE" in name:
            tempname = name.replace("_ACUTE", "")
            name = "/\n" + tempname
        elif "_CARON" in name:
            tempname = name.replace("_CARON", "")
            name = "v\n" + tempname
        elif "_UMLAU" in name:
            tempname = name.replace("_UMLAU", "")
            name = "..\n" + tempname
        elif "_CCIRC" in name:
            tempname = name.replace("_CCIRC", "")
            name = "^\n" + tempname

        formatted = {
            "name": name.replace(" ", ""),
            "title": keycode.replace(" ", "").replace("_", " "),
            "shortName": keycode.replace(" ", "")
        }
        keycodes.append(formatted)
    return keycodes

def filterFunc(x):
  if x == "":
    return False
  else:
    return True

def get_longchar_alias(keycode):
    longchar = f"CLIX{len(longchar_defines):03}"
    longchar_defines.append(f"#define {longchar} {keycode}")

    return longchar

def filter_bad_lines(raw_lines):
    good_lines = []
    for line in raw_lines:
        good = True
        
        if "#define" not in line:
            good = False
        if "//" in line or "/*" in line or "*/" in line:
            good = False
        if good:
            good_lines.append(line)
    return good_lines

def generate_keycode_aliases():
    #url = "https://raw.githack.com/qmk/qmk_firmware/master/quantum/keycode.h"
    url = "https://rawcdn.githack.com/qmk/qmk_firmware/ca10e4d07579ae85c6720fdd3db3a0bfb5ebff36/quantum/keycode.h"
    lib = {}

    with urlopen(url) as f:
        raw_lines = f.read().decode("utf8").split("\n")
    start = -1
    for line in raw_lines:
        if "Short names for ease of definition of keymap" in line:
            start = raw_lines.index(line)
    raw_lines = raw_lines[start:]
    print("raw lines: ", len(raw_lines))

    unimportant = ["//", "/*", "*/"]
    good_lines = filter_bad_lines(raw_lines)
    
    print("good lines: ", len(good_lines))

    # ADD YOUR MODTAP DEFINES HERE!!!! please no tabs before #defineS
    # last line should have them ending quotes
    # no extra spaces, for example: MT(MOD_LCTL,KC_ESC) not MT(MOD_LCTL, KC_ESC)
    # can also be layer taps etc
    
    modtaps = """
#define CTL_ESC MT(MOD_LCTL,KC_ESC)S
#define CTL_QUOT MT(MOD_RCTL,SK_SECT)
#define ALT_ENT MT(MOD_LALT,KC_ENT)"""

    mtlines = list(filter(filterFunc, modtaps.split("\n")))
    for mtline in mtlines:
        good_lines.append(mtline)
    print("added {} user defined aliases".format(len(mtlines)))

    for line in good_lines:
        prep = line[8:].split(" ")
        pair = list(filter(filterFunc, prep))
        #print(pair)
        lib[pair[1]] = pair[0]

    # add legacy keycodes bc for whatever reason vial uses them smh
    legacyurl = "https://rawcdn.githack.com/qmk/qmk_firmware/ca10e4d07579ae85c6720fdd3db3a0bfb5ebff36/quantum/keycode_legacy.h"
    with urlopen(legacyurl) as f:
        legacylines = f.read().decode("utf8").split("\n")

    good_leg_lines = filter_bad_lines(legacylines)
    for line in good_leg_lines:
        prep = line[8:].split(" ")
        pair = list(filter(filterFunc, prep))
        #print(pair)
        try:
            lib[pair[0]] = lib[pair[1]] # check the existing lib to straight up assign the short form to the legacy one
        except:
            continue
    print("assigned aliases to legacy keycodes")
        
    f = open("vial_saves/keycode_db.json", 'w', encoding='utf8')
    json.dump(lib, f, indent=4, ensure_ascii=False)
    f.close()

def array_to_keymap_row(arr, reverse, lib):
    if reverse:
        work = reversed(arr)
    else:
        work = arr
    string = ""

    for keycode in work:
        match keycode:
            case -1:
                string += "        "
            case "KC_TRNS":
                string += "_______,"
            case _:
                try:
                    # shorten long keycodes
                    keycode = lib[keycode]
                except:
                    # no alias found for this key
                    pass
                if len(str(keycode)) > 7:
                    keycode = get_longchar_alias(keycode)

                string += f"{keycode:7}"
                string += ","
        string += " "
    return string

def stitch_keymap_together(layer1, layerindex):
    keymap = []
    for i in range(0, len(layer1)):
        row = layer1[i]
        if i >= keyboard_rows_per_half:
            lol = int(i - (keyboard_rows_per_half / 2) - 2)
            keymap[lol] += array_to_keymap_row(row, False, lib)
        else:
            keymap.append(array_to_keymap_row(row, True, lib))

    keymap.insert(0, "[{}] = LAYOUT(".format(layerindex))
    keymap.append("),")
    return keymap

print("\n".join(commands))

command = ""
while command != "quit":
    command = input("> ")

    match command:
        case "genkey":
            f = open("custom_keys.h", 'r', encoding='utf8')
            lines = f.readlines()
            f.close()

            keycodes = find_keycodes(lines)
            print(keycodes)
            #json_obj = json.dumps(keycodes, indent=4)

            f = open("vial.json", 'r', encoding='utf8')
            obj = json.load(f)
            f.close()

            obj["customKeycodes"] = keycodes

            f = open("vial.json", 'w', encoding='utf8')
            json.dump(obj, f, indent=4, ensure_ascii=False)
            f.close()
        case "viltokey":
            if not exists("vial_saves/keycode_db.json"):
                print("no keycode db exists. run command 'fetchkeys' first")
                continue
            path = input("path to .vil file > ")
            layout = {
                "layers": []
            }

            f = open(path, 'r', encoding='utf8')
            obj = json.load(f)
            f.close()

            f = open("vial_saves/keycode_db.json", 'r', encoding='utf8')
            lib = json.load(f)
            f.close()
            
            layout["layers"] = obj["layout"]
            keymap_lines = []

            for i in range(0, len(layout["layers"])):
                layer1 = layout["layers"][i]
                keymap = stitch_keymap_together(layer1, i)
                keymap_lines.append(keymap)
                keymap_lines.append("")

            for lch in longchar_defines:
                print(lch)
            print()
            print("// clang-format off")
            print("const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {")
            indentation = "    "
            for i in keymap_lines:
                for line in i:
                    print(indentation + line)
            print("};")


            # TODO replace with short aliases
            #print(">", returned, "<")

        case "quit":
            quit()
        case "fetchkeys":
            print("note: please check this code for the 'modtaps' string and paste your defined aliases there to have a nicer keymap")
            generate_keycode_aliases()
        case "help":
            print("available commands:")
            for line in commands:
                print(line)
        case _:
            print("this command does not exist.")

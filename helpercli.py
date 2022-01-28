import json
from urllib.parse import quote_plus
from urllib.request import urlopen
from os.path import exists
import configparser
from PIL import Image

# change this to match your keyboard. support for multiple keyboards soontm
keyboard_cols_per_half = 8
keyboard_rows_per_half = 4
keyboard_halves = 2
important_layers = [0, 3, 2, 5] # important layer indexes in order: black, green(sym), blue(fn), darkred(misc)

print("hello. this is KraXen's VIAL/QMK helper cli")
print("the commands are: ")

commands = [
    "genkey: generate vial customKeycodes from keymap.c",
    "viltokey: convert a .vil vial file into c code",
    "viltokle: convert a .vil vial file into a kle-powered vizualizer",
    "fetchkeys: fetch qmk's github to get aliases for keys",
    "sandwichkle: layer the 4 images on top of eachother to make one final image",
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

    # add my customKeys i use in lwm and obs
    # overrides = [
    #     {
    #         "name": "lwm:\nhide all",
    #         "title": "C(LGUI(KC_KP_0))",
    #         "shortName": "2402" #0x962
    #     },
    #     {
    #         "name": "lwm:\ndiscord",
    #         "title": "C(LGUI(KC_KP_1))",
    #         "shortName": "2393" #0x959
    #     },
    #     {
    #         "name": "lwm:\ndisc+aimp",
    #         "title": "C(LGUI(KC_KP_2))",
    #         "shortName": "2394" #0x95A
    #     },
    #     {
    #         "name": "lwm:\nteams",
    #         "title": "C(LGUI(KC_KP_3))",
    #         "shortName": "2395" #0x95B
    #     },
    #     {
    #         "name": "obs:\nfreeze cam",
    #         "title": "C(LGUI(KC_KP_4))",
    #         "shortName": "2396" #0x95C
    #     }
    # ]
    # for over in overrides:
    #     keycodes.append(over)
    
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
            case "KC_NO":
                string += "XXXXXXX,"
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

def stitch_keymap_together(layer1, layerindex, lib):
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

def read_vil_savefile():
    if not exists("vial_saves/keycode_db.json"):
        print("no keycode db exists. run command 'fetchkeys' first")
        return False, False
    path = input("path to .vil file > ")

    f = open(path, 'r', encoding='utf8')
    obj = json.load(f)
    f.close()

    f = open("vial_saves/keycode_db.json", 'r', encoding='utf8')
    lib = json.load(f)
    f.close()

    return obj, lib

def read_config(config_file_path, add_extra_glyphs):
    legends = {
        'XXXXXXX': '',
        '_______': '',
        'KC_TRNS': '',
        'KC_NO': '',
        'LCTL(KC_Z)': 'UNDO',
        'LCTL(KC_Y)': 'REDO',
        'LCTL(KC_C)': 'COPY',
        'LCTL(KC_V)': 'PASTE',
        'LCTL(KC_X)': 'CUT',
        'KC_PSCREEN': 'PSc',

        'MO(LOWER)': 'LOWER',
        'MO(RAISE)': 'RAISE',
        'RSFT_T(KC_ENT)': 'ET/SFT',
        'LALT(KC_TAB)': 'ALT-TAB',
        'LCTL(KC_G)': 'Ctrl-G',
        'LSFT(KC_SPACE)': 'Sft-SPC',
    }

    if add_extra_glyphs: # nice glyph representations. rely on kle's build it glyphs, so they are useless for keymapviz
        legends["KC_MPLY"] = "<i class='kb kb-Multimedia-Play-Pause'></i>"
        legends["KC_MPRV"] = "<i class='kb kb-Multimedia-Rewind-Start'></i>"
        legends["KC_MNXT"] = "<i class='kb kb-Multimedia-FastForward-End'></i>"
        legends["KC_PGUP"] = "<i class='kb kb-Multimedia-Up'></i>"
        legends["KC_PGDN"] = "<i class='kb kb-Multimedia-Down'></i>"

        legends["KC_TAB"] = "<i class='kb kb-Tab-1'></i>"
        legends["KC_BSPC"] = "<i class='kb kb-Unicode-BackSpace-DeleteLeft-Big'></i>"
        legends["KC_DELETE"] = "<i class='kb kb-Unicode-DeleteRight-Big'></i>"
        legends["KC_NUBS"] = "<i class='fa fa-globe'></i> \\ |"
        legends["KC_NUHS"] = "<i class='fa fa-globe'></i> # ~"

        legends["KC_UP"] = "<i class='kb kb-Arrows-Up'></i>"
        legends["KC_DOWN"] = "<i class='kb kb-Arrows-Down'></i>"
        legends["KC_LEFT"] = "<i class='kb kb-Arrows-Left'></i>"
        legends["KC_RIGHT"] = "<i class='kb kb-Arrows-Right'></i>"

        legends["KC_VOLU"] = "<i class='kb kb-Multimedia-Volume-Up-1'></i>"
        legends["KC_VOLD"] = "<i class='kb kb-Multimedia-Volume-Down-2'></i>"
        legends["KC_MUTE"] = "<i class='kb kb-Multimedia-Mute-1'></i>"

        legends["KC_BRMD"] = "<i class='kb kb-Unicode-Scroll-1'></i><i class='kb kb-Unicode-Lock-Closed-1'></i>"
        legends["KC_BRMU"] = "<i class='mss mss-Unicode-Break-3'></i>"
        legends["KC_HOME"] = "<i class='fa fa-home'></i>"
        legends["KC_END"] = "<i class='kb kb-Line-End'></i>"
        legends["KC_PSCREEN"] = "<i class='fa fa-scissors'></i>"

        legends["2399"] = "<i class='fa fa-microphone-slash'></i>" # ctrl + lgui + numpad 7, my custom macro for mic in ahk

    if config_file_path:
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read_file(config_file_path)
        if 'legends' in config._sections:
            config_legends = config._sections.get("legends")
            legends.update(config_legends)
    return legends

def swap(s, i, j):
    return ''.join((s[:i], s[j], s[i+1:j], s[i], s[j+1:]))

def format_keycode_kle(key, lib, toml_lib):
    """format a given keycode to be visually pleasing in KLE"""
    if "LSFT(" in key:
        key = key.replace("LSFT(", "S(")
    try:
        key = toml_lib[key]
    except:
        pass
    try:
        key = lib[key]
    except:
        pass
    try:
        key = toml_lib[key]
    except:
        pass

    if "(" in key and ")" in key and "MO(" not in key and "RALT(" not in key: # keys with wrappers
        if "LT(" in key and "ALT" not in key: #LT(5, KC_ENTER)
            key = key.replace("LT(", "LT")
            key = key.replace(", ", "(")
        parts = key.split("(")
        parts[1] = parts[1][:-1:] #yeet the closing bracket
        try:
            parts[1] = toml_lib[parts[1]]
        except:
            pass
        fakenewline = "\\n"
        key = f"{parts[1]}{fakenewline * 4}{parts[0]}"

    # stupid dumb special snowflakes
    if '\\ ' in str(key):
        key = str(key).replace('\\ ','\\\\ ')
    if '"' in str(key):
        key = str(key).replace('"','\\"')
        
    key = str(key).replace("KC_", "")
    return key

def merge4images(folder, images):
    base = Image.open(f"{folder}/{images[0]}.png")
    sym = Image.open(f"{folder}/{images[1]}.png")
    nav = Image.open(f"{folder}/{images[2]}.png")
    accents = Image.open(f"{folder}/{images[3]}.png")

    base.paste(sym, (0,0), mask = sym)
    base.paste(nav, (0,0), mask = nav)
    base.paste(accents, (0,0), mask = accents)

    base.save("keymap.png")
    print("done, check keymap.png")

print("\n".join(commands))

command = ""
while command != "quit":
    command = input("> ")

    match command:
        case "genkey":
            f = open("keymap.c", 'r', encoding='utf8')
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
            
            layout = {
                "layers": []
            }
            
            obj, lib = read_vil_savefile()
            if obj == False:
                continue
            
            layout["layers"] = obj["layout"]
            keymap_lines = []

            for i in range(0, len(layout["layers"])):
                layer1 = layout["layers"][i]
                keymap = stitch_keymap_together(layer1, i, lib)
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

        case "viltokle":
            obj, lib = read_vil_savefile()
            if obj == False:
                continue
            layout = {
                "layers": []
            }
            
            layout["layers"] = obj["layout"]
            #layer1 = layout["layers"][0]
            for lay_index in range(0, len(important_layers)):
                layer1 = layout["layers"][important_layers[lay_index]]

                f = open(f"kle/kle{lay_index}.json", 'r', encoding='utf8')
                lay1 = f.read()
                f.close()

                f = open('keymapviz.toml', 'r', encoding='utf8')
                toml_lib = read_config(f, True)
                f.close()
                
                for i in range(0, len(layer1)):
                    row = layer1[i]
                    for j in range(0, len(row)):
                        needle = f"{i};{j};0"
                        key = format_keycode_kle(str(row[j]), lib, toml_lib)
                        
                        #print("replacing {} with {}".format(needle, key))
                        lay1 = lay1.replace(needle, str(key))
                #print(lay1)
                print("written layer ", lay_index)
                payload = json.dumps(lay1)
                #print("http://www.keyboard-layout-editor.com/" + payload)
                f = open(f"result{lay_index}.json", 'w', encoding='utf8')
                f.write(lay1)
                f.close()

        case "sandwichkle":
            merge4images("kle", [0,1,2,3])
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

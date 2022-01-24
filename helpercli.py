import json
from textwrap import indent



print("hello. this is KraXen's VIAL/QMK helper cli")
print("the commands are: ")

commands = [
    "genkey: generate vial customKeycodes from keymap.c"
]

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
    
    lines = lines[:end+1][1:-1]
    keycodes = []
    for line in lines:
        keycode = line.replace(" ", "")
        if "=" in line:
            keycode = keycode.split("=")[0]
        else:
            keycode = line.split(",")[0]

        # {"name": "E./", "title": "E ACUTE", "shortName": "E_ACUTE"}
        #TODO when vial supports unicode, redo this into proper unicode characters
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
        case _:
            print("this command does not exist.")
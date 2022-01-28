# Slovak Kyria Keymap & KraXen's qmk setup
![keymap](keymap.png) 
  
# Explanation of files:
- ``commands.txt`` just my personal commands for compiling.
- ``helpercli.py`` a python helper cli. uses below
- ``my_slovak_keymap.h`` patched version of the qmk slovak keymap that doesen't define one thing twice (soon to be merged into qmk)

# helpercli.py
a python script to automate do various manual tasks that have somethign to do with [vial](https://get.vial.today)  
<details>
<summary>genkey: generate vial customKeycodes from keymap.c</summary>
  
automatically find the ``custom_keycodes`` enum in your ``keymap.c`` and modifies vial.json to recognize the keys:  
![genkey](https://cdn.discordapp.com/attachments/538734863977676803/936572421476077598/Capture_2022_m01.d28_1144.png)  
</details>
  
<details>
<summary>viltokey: convert a .vil vial file into c code</summary>
  
reads a given ``.vil`` savefile and converts it into (hopefully) valid c code. some minor cleanup migh be necessary. expects you to paste it into your ``keymap.c`` 
![viltokey](https://cdn.discordapp.com/attachments/538734863977676803/936573150425145365/unknown.png)  
</details>
  
<details>
<summary>viltokle: convert a .vil vial file into a kle-powered vizualizer</summary>
  
provided a ``.vil`` it will generate 4 layer jsons (define which layers you want at the top of the code) 
- then drag and drop these jsons into [http://www.keyboard-layout-editor.com](http://www.keyboard-layout-editor.com) and save the layers as .png, named 0 to 3 in the ``kle`` folder    
- then run the **sandwichkle** command and check ``keymap.png``:
  
![keymap](https://cdn.discordapp.com/attachments/538734863977676803/936575081587552306/keymap.png)  
> the middle layer labels are not done, WIP
</details>

<details>
<summary>fetchkeys: fetch qmk's github to get aliases for keys</summary>
   
this will download latest qmk keycode alias definitions. useful when generating a keymap.c, it can find shorter valid keycodes, for example ``KC_SCROLLLOCK`` is also ``KC_BRMD`` and short keycodes look better in the keymap.
</details>
  

# Credits
this started as a proof-of-concept keymap for typing in Slovak on a Kyria.  
it was made by [**precondition**](https://github.com/precondition), who doesen't speak Slovak nor own a Kyria himself.  
Huge thanks to the people mentioned below:
- [**precondition**](https://github.com/precondition) for making a layer with accented characters & setting up it's macro system
- [**Eric Gebhart**](https://github.com/EricGebhart) for implementing his altlocal system into my existing enviroment, so i can have us keys on sk keymap
  
if anyone is interested here is a [typing test](https://www.youtube.com/watch?v=jbK86MmciDs)

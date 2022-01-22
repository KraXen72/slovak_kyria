# Slovak Kyria Keymap & KraXen's qmk setup

Proof-of-concept keymap for typing in Slovakian on a Kyria.

Precondition: I don't speak Slovakian nor do I own a Kyria myself.  
me: correction: I **do** speak Slovak and I **do** own a Kyria myself.

**thousand times thank you and a huge shoutout for precondition for making the whole accent letter system and layer**

# Explanation of files:
- ``commands.txt`` just my personal commands for compiling.
- ``helpercli.py`` a python helper cli. all commands explained in it. useful for generating keycodes for vial.json, etc.
- ``my_slovak_keymap.h`` patched version of the qmk slovak keymap that doesen't define one thing twice
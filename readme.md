# Slovak Kyria Keymap & KraXen's qmk setup

https://www.youtube.com/watch?v=jbK86MmciDs

Proof-of-concept keymap for typing in Slovakian on a Kyria.

Precondition: I don't speak Slovakian nor do I own a Kyria myself.  
me: correction: I **do** speak Slovak and I **do** own a Kyria myself.

# Explanation of files:
- ``commands.txt`` just my personal commands for compiling.
- ``helpercli.py`` a python helper cli. all commands explained in it. useful for generating keycodes for vial.json, etc.
- ``my_slovak_keymap.h`` patched version of the qmk slovak keymap that doesen't define one thing twice (soon to be merged into qmk)
- ``custom_keys.h`` defined custom keys

# Credits
Huge thanks to the people mentioned below:
- [**precondition**](https://github.com/precondition) for making a layer with accented characters & setting up it's macro system
- [**Eric Gebhart**](https://github.com/EricGebhart) for implementing his altlocal system into my existing enviroment, so i can have us keys on sk keymap
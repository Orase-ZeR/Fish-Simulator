import os
import json

SAVE_PATH = "save.json"

savedGame = {}

def load_save():
    """
    Loads the save file if it exists, otherwise creates an empty save file.
    The var savedGame is populated with save content; it is intended to be imported and used directly as the save
    Do not forget to write modification back to file when modifying, we're only loading it here with the
    intent of keeping it in memory for easy access and reduced I/O.
    """
    global savedGame
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            savedGame = json.load(f)
    else:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump({}, f)
        savedGame = {}

load_save()
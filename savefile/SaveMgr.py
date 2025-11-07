from . import SAVE_PATH, savedGame
import os
import json

def wipe_save():
    """
    Wipes the current save file by clearing its contents and deleting the file.
    Will also clear the in-memory version to avoid having to reload.
    """
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)
    savedGame.clear()
    os.remove(SAVE_PATH)
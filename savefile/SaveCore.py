from . import savedGame, SAVE_PATH
import os
import math
import shutil
import json
import base64
import tempfile

# An easy access system should be implemented later for ease of use in actual code, this is just a Core.

def encode_data(data):
    """
    Encodes data to be JSON serializable, handling tuples and NaN values.
    Encoded (unsupported) data such as tuples and NaNs are represented as a dictionary with a special __type__ key.
    using __name__ as key is reserved to these and will probably break save.
    """
    if isinstance(data, tuple):
        return {"__type__": "tuple", "items": [encode_data(i) for i in data]}
    if isinstance(data, float) and math.isnan(data):
        return {"__type__": "nan"}
    if isinstance(data, list):
        return [encode_data(i) for i in data]
    if isinstance(data, dict):
        return {key: encode_data(value) for key, value in data.items()}
    return data

def decode_data(data):
    """
    Decodes data that was encoded with encode_data back to its original form while restoring
    unsupported tuples and NaNs types.
    """
    if isinstance(data, dict) and data.get("__type__") == "tuple":
        return tuple(decode_data(i) for i in data["items"])
    if isinstance(data, dict) and data.get("__type__") == "nan":
        return float("nan")
    if isinstance(data, list):
        return [decode_data(i) for i in data]
    if isinstance(data, dict):
        return {key: decode_data(value) for key, value in data.items() if key != "__type__"}
    return data

def save_game_data(key: str, data):
    """
    Saves game data under a key after encoding it to handle unsupported types.
    The data is stored encoded in base64 for safe storage.
    A temporary file is used to avoid data loss, not sure about this systems efficiency.
    save_game_data("test key", "test_data") will store the "test_data" str under "test key"
    data can be any classic type such as : str, int, float, bool, list, tuple, dict, None and Nan float.
    """
    to_save = encode_data(data)
    str_data = json.dumps(to_save)
    encoded_data = base64.b64encode(str_data.encode("utf-8")).decode("utf-8")
    savedGame[key] = {
        "value": encoded_data,
    }
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
        json.dump(savedGame, f)
        tmp_path = f.name
    shutil.copyfile(tmp_path, SAVE_PATH)
    os.remove(tmp_path)

def load_game_data(key: str):
    """
    Loads game data stored under a key, restoring it and returning in the exact same way and type it was stored.
    uses the version stored in memory and loaded on startup, not the save file directly for the sake of ease and I/O.
    Returns None if the key does not exist.
    load_game_data("test key") will return the data stored under "test key".
    """
    data = savedGame.get(key)
    if data is None:
        return None
    datavalue = base64.b64decode(data.get("value")).decode("utf-8")
    loaded = json.loads(datavalue)
    return decode_data(loaded)

def remove_game_data(key: str):
    """
    Removes game data stored under a key.
    Does nothing if the key does not exist.
    remove_game_data("test key") will remove the data stored under "test key".
    """
    if key in savedGame:
        del savedGame[key]
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as f:
            json.dump(savedGame, f)
            tmp_path = f.name
        shutil.copyfile(tmp_path, SAVE_PATH)
        os.remove(tmp_path)
import json
import os

SAVE_FILE = "save.json"

def load_save():
    if not os.path.exists(SAVE_FILE):
        return {"completed_levels": {}, "chapter_unlocked": 1}
    with open(SAVE_FILE, "r") as f:
        return json.load(f)

def save_game(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)
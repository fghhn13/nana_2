import os
from Gui.config import gui_config

NOTES_FOLDER = "MyNotes"

# Ensure notes directory exists
NOTES_DIR = gui_config.NOTES_DIR

def ensure_notes_folder_exists():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

def get_note_path(note_name: str) -> str:
    return os.path.join(NOTES_DIR, f"{note_name}.txt")

def list_notes() -> list[str]:
    if not os.path.exists(NOTES_DIR):
        return []
    return sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(NOTES_DIR)
        if f.endswith(".txt")
    )

def create_note(note_name: str) -> bool:
    ensure_notes_folder_exists()
    note_path = get_note_path(note_name)
    if os.path.exists(note_path):
        return False
    with open(note_path, "w", encoding="utf-8"):
        pass
    return True

def delete_note(note_name: str) -> None:
    os.remove(get_note_path(note_name))

def read_note(note_name: str) -> str:
    with open(get_note_path(note_name), "r", encoding="utf-8") as f:
        return f.read()

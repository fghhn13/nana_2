
import os
from config import app_config
NOTES_FOLDER = "MyNotes"

def ensure_notes_folder_exists():
    if not os.path.exists(app_config.NOTES_DIR):
        os.makedirs(app_config.NOTES_DIR)

def get_note_path(note_name):
    return os.path.join(app_config.NOTES_DIR, f"{note_name}.txt")

def list_notes():
    if not os.path.exists(app_config.NOTES_DIR):
        return []
    return sorted([os.path.splitext(f)[0] for f in os.listdir(app_config.NOTES_DIR) if f.endswith(".txt")])


def create_note(note_name):
    """创建空的笔记文件，如果成功返回True，如果已存在返回False。"""
    note_path = get_note_path(note_name)
    if os.path.exists(note_path):
        return False
    with open(note_path, 'w', encoding='utf-8') as f:
        pass
    return True

def delete_note(note_name):
    os.remove(get_note_path(note_name))

def read_note(note_name):
    with open(get_note_path(note_name), 'r', encoding='utf-8') as f:
        return f.read()
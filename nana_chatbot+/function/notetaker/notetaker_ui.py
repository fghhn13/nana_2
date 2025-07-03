# function/notetaker/notetaker_ui.py
import tkinter as tk
from tkinter import scrolledtext, messagebox
from .notetaker_handle import get_note_path
from config import  app_config  # 确保 app_config 也被导入了


def open_note_editor(note_name, content="", master_window=None):
    editor_window = tk.Toplevel(master_window)
    editor_window.title(f"{app_config.NOTE_EDITOR_TITLE_PREFIX}{note_name}")
    editor_window.config(bg=app_config.BG_MAIN)

    text_area = scrolledtext.ScrolledText(
        editor_window, wrap=tk.WORD, width=80, height=25, font=("等线", 12),
        bg=app_config.BG_INPUT, fg=app_config.FG_TEXT, insertbackground=app_config.CURSOR_COLOR, bd=0
    )
    text_area.insert(tk.END, content)
    text_area.pack(padx=10, pady=10, fill="both", expand=True)

    def save_note():
        current_content = text_area.get(1.0, tk.END).strip()
        try:
            with open(get_note_path(note_name), "w", encoding="utf-8") as f:
                f.write(current_content)
            messagebox.showinfo(
                app_config.CONFIRM_SAVE_TITLE,
                app_config.CONFIRM_SAVE_MESSAGE.format(note_name=note_name),
                parent=editor_window
            )
        except Exception as e:
            messagebox.showerror(
                app_config.ERROR_SAVE_TITLE,
                app_config.ERROR_SAVE_MESSAGE.format(e=e),
                parent=editor_window
            )

    # --- 保存按钮 ---

    save_button = tk.Button(
        editor_window,
        text=app_config.SAVE_BUTTON_TEXT,  # 使用常量
        command=save_note,
        bg=app_config.BG_BUTTON,
        fg=app_config.FG_BUTTON
    )
    # 2. 把按钮显示出来
    save_button.pack(pady=5)
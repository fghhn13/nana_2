from plugins.base_plugin import BasePlugin
from core.log.logger_config import logger
from .notetaker_handle import (
    ensure_notes_folder_exists,
    create_note,
    read_note,
    delete_note,
    list_notes,
)
from .notetaker_ui import open_note_editor, open_notes_window


class NoteTakerPlugin(BasePlugin):
    def get_name(self) -> str:
        return "note_taker"

    def get_commands(self) -> list[str]:
        return ["create_note", "read_note", "delete_note", "list_notes"]

    def on_load(self):
        ensure_notes_folder_exists()

    def execute(self, command: str, args: dict, controller) -> None:
        title = args.get("title") if args else None
        if command == "create_note":
            if not title:
                return
            created = create_note(title)
            msg = f"新建笔记 '{title}' 成功。" if created else f"笔记 '{title}' 已存在。"
            controller.view.ui_queue.put(("APPEND_MESSAGE", ("Nana", msg, "nana_sender")))
            content = "" if created else read_note(title)
            open_note_editor(title, content, controller.view.master)
        elif command == "read_note":
            if not title:
                return
            try:
                content = read_note(title)
            except FileNotFoundError:
                err = f"笔记 '{title}' 不存在。"
                controller.view.ui_queue.put(("APPEND_MESSAGE", ("Nana酱", err, "error_sender")))
                return
            open_note_editor(title, content, controller.view.master)
        elif command == "delete_note":
            if not title:
                return
            try:
                delete_note(title)
                msg = f"已删除笔记 '{title}'。"
                controller.view.ui_queue.put(("APPEND_MESSAGE", ("Nana", msg, "nana_sender")))
            except FileNotFoundError:
                err = f"笔记 '{title}' 不存在。"
                controller.view.ui_queue.put(("APPEND_MESSAGE", ("Nana酱", err, "error_sender")))
        elif command == "list_notes":
            notes = list_notes()
            if notes:
                open_notes_window(notes, controller.view.master)
            else:
                controller.view.ui_queue.put(("APPEND_MESSAGE", ("Nana", "没有找到任何笔记。", "nana_sender")))
        else:
            logger.warning(f"未识别的命令: {command}")


def get_plugin():
    return NoteTakerPlugin()

"""Structured JSONL recorder for hook lifecycle and message history events."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .history_records import (
    HookHistoryEntry,
    HookHistoryRecord,
    MessageHistoryEntry,
    MessageHistoryRecord,
)

_JST = ZoneInfo("Asia/Tokyo")
_DEFAULT_HOOK_HISTORY_DIR = Path(".claude/.works/logs")
_DEFAULT_MESSAGE_HISTORY_DIR = Path(".claude/.works/histories")
_HOOK_HISTORY_FILE_NAME = "hooks.jsonl"


class HistoryRecorder:
    """Structured JSONL recorder for hook and message history events.

    Args:
        hook_history_dir: Directory path where the hooks JSONL file is written.
            Defaults to ``.claude/.works/logs``.
        message_history_dir: Directory path where message history JSONL files are
            written. Defaults to ``.claude/.works/histories``.

    """

    def __init__(
        self,
        hook_history_dir: str | Path = _DEFAULT_HOOK_HISTORY_DIR,
        message_history_dir: str | Path = _DEFAULT_MESSAGE_HISTORY_DIR,
    ) -> None:
        """Initialize HistoryRecorder with target history directories."""
        self._hook_history_dir = Path(hook_history_dir)
        self._message_history_dir = Path(message_history_dir)

    def append_hook_history(self, entry: HookHistoryEntry) -> None:
        """Append one structured hook event to the shared hook history file.

        Args:
            entry: Hook history entry containing all event metadata.

        Returns:
            None.

        Raises:
            No exceptions are raised intentionally. Logging failures are ignored.

        """
        record = HookHistoryRecord(
            timestamp=datetime.now(_JST).isoformat(),
            hook_event=entry.hook_event,
            script=entry.script,
            status=entry.status,
            exit_code=entry.exit_code,
            target_files=entry.target_files,
            message=entry.message,
            tool_name=entry.tool_name,
        ).to_dict()

        try:
            self._hook_history_dir.mkdir(parents=True, exist_ok=True)
            out_file = self._hook_history_dir / _HOOK_HISTORY_FILE_NAME
            with out_file.open("a", encoding="utf-8") as file_handle:
                file_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            return

    def append_message_history(self, entry: MessageHistoryEntry) -> None:
        """Append one structured message event to a message JSONL file.

        Args:
            entry: Message history entry containing message metadata.

        Returns:
            None.

        Raises:
            No exceptions are raised intentionally. Logging failures are ignored.

        """
        record = MessageHistoryRecord(
            timestamp=datetime.now(_JST).isoformat(),
            event=entry.event,
            session_id=entry.session_id,
            message=entry.message,
        ).to_dict()

        try:
            self._message_history_dir.mkdir(parents=True, exist_ok=True)
            out_file = self._message_history_dir / f"{entry.session_id}.jsonl"
            with out_file.open("a", encoding="utf-8") as file_handle:
                file_handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError:
            return

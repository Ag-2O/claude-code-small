"""Session transcript recorder that also writes hook lifecycle logs."""

import json
import sys
from pathlib import Path

from . import HistoryRecorder, HookHistoryEntry, MessageHistoryEntry

_history_recorder = HistoryRecorder()


def _load_transcript(transcript_path: str) -> list[dict]:
    """Load JSONL transcript records from a file path.

    Args:
        transcript_path: Path to transcript JSONL file.

    Returns:
        Parsed transcript records. Returns an empty list when the file is absent.

    """
    path = Path(transcript_path)
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _extract_latest_message(transcript: list[dict]) -> str | None:
    """Return the text content of the latest user or assistant record from transcript.

    Args:
        transcript: Parsed transcript records.

    Returns:
        Extracted plain text, or None when no matching record is found.

    """
    for record in reversed(transcript):
        if record.get("type") in ("user", "assistant"):
            inner = record.get("message")
            if not isinstance(inner, dict):
                return None
            content = inner.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                texts = [
                    block["text"]
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                return "\n".join(texts) or None
    return None


def main() -> int:
    """Read hook payload from stdin and append session and hook logs."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    session_id = data.get("session_id", "unknown")
    event = data.get("hook_event_name", "unknown")
    transcript_path = data.get("transcript_path", "")

    if event == "UserPromptSubmit":
        # The user's prompt is available directly in the payload.
        # The transcript does not yet contain the new message at this point.
        prompt = data.get("prompt")
        latest: str | None = prompt if prompt is not None else None
    else:
        transcript = _load_transcript(transcript_path)
        latest = _extract_latest_message(transcript)

    _history_recorder.append_message_history(
        MessageHistoryEntry(
            event=event,
            session_id=session_id,
            message=latest,
        ),
    )

    _history_recorder.append_hook_history(
        HookHistoryEntry(
            hook_event=event,
            script="record_messages.py",
            status="success",
            exit_code=0,
            message="message record appended",
        ),
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

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


def _extract_text_from_content(content: object) -> str | None:
    """Extract plain text from a message ``content`` field.

    Handles a raw string, a list of content blocks, and ``tool_result`` blocks
    whose payload nests further content blocks. The latter case carries a
    subagent's final report back into the main transcript, which is what the
    SubagentStop event needs to record.

    Args:
        content: The ``content`` value of a transcript message.

    Returns:
        Concatenated text, or None when no text is present.

    """
    if isinstance(content, str):
        return content or None
    if not isinstance(content, list):
        return None
    texts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text" and isinstance(block.get("text"), str):
            texts.append(block["text"])
        elif block_type == "tool_result":
            nested = _extract_text_from_content(block.get("content"))
            if nested:
                texts.append(nested)
    return "\n".join(texts) or None


def _extract_latest_message(transcript: list[dict]) -> str | None:
    """Return the text of the most recent user or assistant record with text.

    Scans records from newest to oldest and returns the first one that yields
    text. Records without extractable text (for example an assistant turn that
    contains only a ``tool_use`` block) are skipped rather than treated as the
    final answer, so a trailing tool call no longer produces an empty message.

    Args:
        transcript: Parsed transcript records.

    Returns:
        Extracted plain text, or None when no record yields text.

    """
    for record in reversed(transcript):
        if record.get("type") not in ("user", "assistant"):
            continue
        inner = record.get("message")
        if not isinstance(inner, dict):
            continue
        text = _extract_text_from_content(inner.get("content"))
        if text:
            return text
    return None


def _resolve_subagent_transcript(data: dict) -> str | None:
    """Return the path to the transcript of the subagent that just stopped.

    A SubagentStop payload's ``transcript_path`` points at the *main* session
    transcript, whose tail may already hold a later main-agent message. The
    payload also carries ``agent_transcript_path`` for the specific subagent, so
    that is preferred. When it is absent, fall back to the most recently
    modified file under ``<session>/subagents/agent-*.jsonl``. The payload key is
    authoritative and avoids picking the wrong file when subagents run in
    parallel, which the modification-time fallback cannot guarantee.

    Args:
        data: Parsed hook payload for the SubagentStop event.

    Returns:
        Path to the subagent transcript, or None when it cannot be determined.

    """
    agent_path = data.get("agent_transcript_path")
    if isinstance(agent_path, str) and Path(agent_path).exists():
        return agent_path

    main_path = Path(data.get("transcript_path", ""))
    subagents_dir = main_path.parent / main_path.stem / "subagents"
    if not subagents_dir.is_dir():
        return None
    candidates = list(subagents_dir.glob("agent-*.jsonl"))
    if not candidates:
        return None
    newest = max(candidates, key=lambda path: path.stat().st_mtime)
    return str(newest)


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
    elif event == "SubagentStop":
        # Read the subagent's own transcript so the recorded message is that
        # subagent's final report rather than a later main-agent message.
        source = _resolve_subagent_transcript(data) or transcript_path
        latest = _extract_latest_message(_load_transcript(source))
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

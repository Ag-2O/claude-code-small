"""Markdown formatter hook script with history recording."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from recorder import HistoryRecorder, HookHistoryEntry

_history_recorder = HistoryRecorder()


def _find_mdformat() -> list[str] | None:
    """Locate the mdformat executable in the virtual environment or system PATH.

    Returns:
        A list containing the path to the mdformat executable, or None if
        mdformat is not available.

    """
    venv_scripts = Path(".venv/Scripts/mdformat.exe")
    if venv_scripts.exists():
        return [str(venv_scripts)]
    venv_bin = Path(".venv/bin/mdformat")
    if venv_bin.exists():
        return [str(venv_bin)]
    if shutil.which("mdformat"):
        return ["mdformat"]
    return None


def _collect_markdown_paths(tool_input: dict[str, object]) -> list[str]:
    """Extract Markdown file paths targeted by a tool call from its input payload.

    Args:
        tool_input: The ``tool_input`` dict from the Claude Code hook payload.

    Returns:
        A deduplicated list of ``.md`` or ``.mdx`` file paths found in the payload.

    """
    direct_path = tool_input.get("file_path") or tool_input.get("filePath")
    if isinstance(direct_path, str) and direct_path.endswith((".md", ".mdx")):
        return [direct_path]

    patch_input = tool_input.get("input")
    if not isinstance(patch_input, str):
        return []

    matches = re.findall(
        r"^\*\*\* (?:Add|Update) File: (.+)$",
        patch_input,
        flags=re.MULTILINE,
    )
    markdown_paths: list[str] = []
    for match in matches:
        normalized_path = match.strip()
        if normalized_path.endswith((".md", ".mdx")):
            markdown_paths.append(normalized_path)

    return list(dict.fromkeys(markdown_paths))


def _format_markdown_file(file_path: str) -> None:
    """Run mdformat on a single Markdown file.

    Linting (``pymarkdown scan``) is intentionally not run here. Per-edit
    linting floods the agent context with diagnostics; lint is instead executed
    as a workflow gate (see ``.claude/skills/base-markdown`` and
    ``.claude/rules/markdown.md``). This hook only applies the deterministic,
    side-effect-free formatter.

    Args:
        file_path: Path to the Markdown file to format.

    """
    mdformat = _find_mdformat()
    if mdformat:
        subprocess.run(  # noqa: S603
            [*mdformat, file_path],
            capture_output=True,
            check=False,
        )


def main() -> int:
    """Read hook payload from stdin, format Markdown files, and record history."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_input = data.get("tool_input", {})
    hook_event = str(data.get("hook_event_name", "unknown"))
    tool_name = str(data.get("tool_name", "unknown"))
    if not isinstance(tool_input, dict):
        _history_recorder.append_hook_history(
            HookHistoryEntry(
                hook_event=hook_event,
                script="format_markdown.py",
                status="skipped",
                exit_code=0,
                message="tool_input was not a dict",
                tool_name=tool_name,
            ),
        )
        return 0

    file_paths = _collect_markdown_paths(tool_input)
    if not file_paths:
        _history_recorder.append_hook_history(
            HookHistoryEntry(
                hook_event=hook_event,
                script="format_markdown.py",
                status="skipped",
                exit_code=0,
                message="no markdown targets",
                tool_name=tool_name,
            ),
        )
        return 0

    existing_paths: list[str] = []
    for file_path in file_paths:
        if Path(file_path).exists():
            existing_paths.append(file_path)
            _format_markdown_file(file_path)

    _history_recorder.append_hook_history(
        HookHistoryEntry(
            hook_event=hook_event,
            script="format_markdown.py",
            status="success",
            exit_code=0,
            target_files=existing_paths,
            message="markdown format hook completed",
            tool_name=tool_name,
        ),
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

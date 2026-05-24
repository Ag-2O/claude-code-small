"""Python formatter hook script with history recording."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from recorder import HistoryRecorder, HookHistoryEntry

_history_recorder = HistoryRecorder()


def _find_ruff() -> list[str] | None:
    """Locate the ruff executable in the virtual environment or system PATH.

    Returns:
        A list containing the path to the ruff executable, or None if ruff
        is not available.

    """
    venv_scripts = Path(".venv/Scripts/ruff.exe")
    if venv_scripts.exists():
        return [str(venv_scripts)]
    venv_bin = Path(".venv/bin/ruff")
    if venv_bin.exists():
        return [str(venv_bin)]
    if shutil.which("ruff"):
        return ["ruff"]
    return None


def _collect_python_paths(tool_input: dict[str, object]) -> list[str]:
    """Extract Python file paths targeted by a tool call from its input payload.

    Args:
        tool_input: The ``tool_input`` dict from the Claude Code hook payload.

    Returns:
        A deduplicated list of ``.py`` or ``.pyi`` file paths found in the payload.

    """
    direct_path = tool_input.get("file_path") or tool_input.get("filePath")
    if isinstance(direct_path, str) and direct_path.endswith((".py", ".pyi")):
        return [direct_path]

    patch_input = tool_input.get("input")
    if not isinstance(patch_input, str):
        return []

    matches = re.findall(
        r"^\*\*\* (?:Add|Update) File: (.+)$",
        patch_input,
        flags=re.MULTILINE,
    )
    python_paths: list[str] = []
    for match in matches:
        normalized_path = match.strip()
        if normalized_path.endswith((".py", ".pyi")):
            python_paths.append(normalized_path)

    return list(dict.fromkeys(python_paths))


def _format_python_file(file_path: str, ruff: list[str]) -> tuple[int, str | None]:
    """Run ruff format and ruff check --fix on a single Python file.

    Args:
        file_path: Path to the Python file to format.
        ruff: Command prefix for the ruff executable.

    Returns:
        A tuple of (exit_code, error_message). exit_code is 0 on success or 2
        if ruff check reports remaining violations. error_message is None on
        success, or the ruff output string on failure.

    """
    subprocess.run([*ruff, "format", file_path], capture_output=True, check=False)  # noqa: S603
    subprocess.run(  # noqa: S603
        [*ruff, "check", file_path, "--fix"],
        capture_output=True,
        check=False,
    )

    result = subprocess.run(  # noqa: S603
        [*ruff, "check", file_path],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        message = result.stdout.strip() or result.stderr.strip() or "ruff check failed"
        return 2, message

    return 0, None


def main() -> int:
    """Read hook payload from stdin, format Python files, and record history."""
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
                script="format_python.py",
                status="skipped",
                exit_code=0,
                message="tool_input was not a dict",
                tool_name=tool_name,
            ),
        )
        return 0

    file_paths = _collect_python_paths(tool_input)
    if not file_paths:
        _history_recorder.append_hook_history(
            HookHistoryEntry(
                hook_event=hook_event,
                script="format_python.py",
                status="skipped",
                exit_code=0,
                message="no python target",
                tool_name=tool_name,
            ),
        )
        return 0

    ruff = _find_ruff()
    if ruff is None:
        _history_recorder.append_hook_history(
            HookHistoryEntry(
                hook_event=hook_event,
                script="format_python.py",
                status="skipped",
                exit_code=0,
                target_files=file_paths,
                message="ruff not available",
                tool_name=tool_name,
            ),
        )
        return 0

    exit_code = 0
    existing_paths: list[str] = []
    messages: list[str] = []
    for file_path in file_paths:
        if not Path(file_path).exists():
            continue

        existing_paths.append(file_path)
        file_exit_code, file_message = _format_python_file(file_path, ruff)
        exit_code = max(exit_code, file_exit_code)
        if file_message:
            messages.append(file_message)

    if messages:
        combined_message = "\n\n".join(messages)
        _history_recorder.append_hook_history(
            HookHistoryEntry(
                hook_event=hook_event,
                script="format_python.py",
                status="failed",
                exit_code=2,
                target_files=existing_paths,
                message=combined_message,
                tool_name=tool_name,
            ),
        )
        print(combined_message)
        return 2

    _history_recorder.append_hook_history(
        HookHistoryEntry(
            hook_event=hook_event,
            script="format_python.py",
            status="success" if exit_code == 0 else "failed",
            exit_code=exit_code,
            target_files=existing_paths,
            message="python hook completed",
            tool_name=tool_name,
        ),
    )

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

"""Deterministic CLI for managing per-feature STATE.md anchor files.

This tool owns all structured writes to ``STATE.md`` so that the probabilistic
LLM never edits the frontmatter directly. It parses only the constrained
frontmatter format that it writes itself, recomputes progress on every
mutation, and regenerates the human-readable body table.

STATE.md layout::

    ---
    feature: <name>
    current_phase: <phase>
    updated: <YYYY-MM-DD>
    progress: <int percent>
    tasks:
      TASK_1_1: done
      TASK_1_2: in_progress
      TASK_2_1: todo
    blockers:
      - first blocker
    ---

    # 進捗: <name>
    ... auto-generated body ...

Task IDs follow the ``TASK_<phase_num>_<task_num>`` convention (e.g. ``TASK_1_1``,
``TASK_2_3``). The tool itself treats task IDs as opaque strings, so any naming
convention is accepted, but new features should use the convention above.

Run ``uv run python state_tool.py --help`` for the available subcommands.
"""

import argparse
import datetime
import sys
from dataclasses import dataclass, field
from pathlib import Path

_VALID_STATUSES = ("todo", "in_progress", "blocked", "done")
_DEFAULT_ROOT = ".artifacts"
_AUTOGEN_NOTE = (
    "<!-- このセクションはスクリプトが自動生成します。手動編集しないでください。 -->"
)


@dataclass
class FeatureState:
    """In-memory representation of a feature's STATE.md content.

    Attributes:
        feature: Feature name (directory under the artifacts root).
        current_phase: Current phase identifier (e.g. ``phase_1``).
        updated: Last update date in ISO ``YYYY-MM-DD`` form.
        tasks: Mapping of task id to status (one of ``_VALID_STATUSES``).
        blockers: Free-form blocker descriptions currently open.

    """

    feature: str
    current_phase: str = "phase_1"
    updated: str = ""
    tasks: dict[str, str] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)

    def progress_percent(self) -> int:
        """Return completion percentage based on tasks marked ``done``.

        Returns:
            Integer percent in ``0..100``. Returns ``0`` when no tasks exist.

        """
        if not self.tasks:
            return 0
        done = sum(1 for status in self.tasks.values() if status == "done")
        return round(done * 100 / len(self.tasks))


def _today() -> str:
    """Return today's date as an ISO ``YYYY-MM-DD`` string.

    Returns:
        The current local date formatted as ``YYYY-MM-DD``.

    """
    return datetime.date.today().isoformat()


def _state_path(root: Path, feature: str) -> Path:
    """Build the STATE.md path for a feature.

    Args:
        root: Artifacts root directory.
        feature: Feature name.

    Returns:
        Path to ``<root>/features/<feature>/STATE.md``.

    """
    return root / "features" / feature / "STATE.md"


def _split_frontmatter(text: str) -> list[str]:
    """Extract the frontmatter lines from a STATE.md document.

    Args:
        text: Full file content.

    Returns:
        The lines between the opening and closing ``---`` markers.

    Raises:
        ValueError: If the document does not start with a frontmatter block.

    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("STATE.md is missing its opening frontmatter marker")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]
    raise ValueError("STATE.md is missing its closing frontmatter marker")


def _parse(text: str) -> FeatureState:
    """Parse a STATE.md document into a FeatureState.

    Only the constrained format produced by :func:`_render` is supported.

    Args:
        text: Full file content.

    Returns:
        The parsed feature state.

    Raises:
        ValueError: If required keys are missing or a status is invalid.

    """
    body = _split_frontmatter(text)
    scalars: dict[str, str] = {}
    tasks: dict[str, str] = {}
    blockers: list[str] = []
    section = ""
    for raw in body:
        if not raw.strip():
            continue
        if not raw.startswith((" ", "\t")):
            key, _, value = raw.partition(":")
            section = key.strip()
            value = value.strip()
            if value:
                scalars[section] = value
            continue
        item = raw.strip()
        if section == "tasks":
            task_id, _, status = item.partition(":")
            status = status.strip()
            if status not in _VALID_STATUSES:
                raise ValueError(f"invalid status '{status}' for {task_id.strip()}")
            tasks[task_id.strip()] = status
        elif section == "blockers" and item.startswith("- "):
            blockers.append(item[2:].strip())
    if "feature" not in scalars:
        raise ValueError("STATE.md frontmatter is missing 'feature'")
    return FeatureState(
        feature=scalars["feature"],
        current_phase=scalars.get("current_phase", "phase_1"),
        updated=scalars.get("updated", ""),
        tasks=tasks,
        blockers=blockers,
    )


def _render(state: FeatureState) -> str:
    """Serialize a FeatureState into STATE.md text.

    Args:
        state: Feature state to serialize.

    Returns:
        Full file content with frontmatter and an auto-generated body.

    """
    percent = state.progress_percent()
    done = sum(1 for status in state.tasks.values() if status == "done")
    total = len(state.tasks)

    head = ["---", f"feature: {state.feature}"]
    head.append(f"current_phase: {state.current_phase}")
    head.append(f"updated: {state.updated}")
    head.append(f"progress: {percent}")
    head.append("tasks:")
    for task_id, status in state.tasks.items():
        head.append(f"  {task_id}: {status}")
    head.append("blockers:")
    for blocker in state.blockers:
        head.append(f"  - {blocker}")
    head.append("---")

    body = [
        "",
        f"# 進捗: {state.feature}",
        "",
        _AUTOGEN_NOTE,
        "",
        f"- 現在フェーズ: {state.current_phase}",
        f"- 進捗: {done}/{total} ({percent}%)",
        "",
        "| タスク | 状態 |",
        "| --- | --- |",
    ]
    for task_id, status in state.tasks.items():
        body.append(f"| {task_id} | {status} |")
    body.append("")
    body.append("## ブロッカー")
    body.append("")
    if state.blockers:
        body.extend(f"- {blocker}" for blocker in state.blockers)
    else:
        body.append("- なし")
    body.append("")
    return "\n".join(head + body)


def _load(root: Path, feature: str) -> FeatureState:
    """Load and parse a feature's STATE.md.

    Args:
        root: Artifacts root directory.
        feature: Feature name.

    Returns:
        The parsed feature state.

    Raises:
        FileNotFoundError: If the STATE.md file does not exist.

    """
    path = _state_path(root, feature)
    if not path.exists():
        raise FileNotFoundError(f"STATE.md not found: {path}")
    return _parse(path.read_text(encoding="utf-8"))


def _save(root: Path, state: FeatureState) -> Path:
    """Write a feature's STATE.md, updating the timestamp.

    Args:
        root: Artifacts root directory.
        state: Feature state to persist.

    Returns:
        The path that was written.

    """
    state.updated = _today()
    path = _state_path(root, state.feature)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render(state), encoding="utf-8")
    return path


def _cmd_init(args: argparse.Namespace) -> int:
    """Create a new STATE.md for a feature if it does not already exist.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code.

    """
    root = Path(args.root)
    path = _state_path(root, args.feature)
    if path.exists():
        print(f"STATE.md already exists: {path}")
        return 0
    state = FeatureState(feature=args.feature, current_phase=args.phase)
    written = _save(root, state)
    print(f"created {written}")
    return 0


def _cmd_set_task(args: argparse.Namespace) -> int:
    """Set the status of a single task.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code.

    """
    if args.status not in _VALID_STATUSES:
        print(f"invalid status: {args.status}", file=sys.stderr)
        return 2
    root = Path(args.root)
    state = _load(root, args.feature)
    state.tasks[args.task] = args.status
    _save(root, state)
    print(f"{args.task} -> {args.status} (progress {state.progress_percent()}%)")
    return 0


def _cmd_set_phase(args: argparse.Namespace) -> int:
    """Update the current phase.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code.

    """
    root = Path(args.root)
    state = _load(root, args.feature)
    state.current_phase = args.phase
    _save(root, state)
    print(f"current_phase -> {args.phase}")
    return 0


def _cmd_add_blocker(args: argparse.Namespace) -> int:
    """Append a blocker description.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code.

    """
    root = Path(args.root)
    state = _load(root, args.feature)
    state.blockers.append(args.text)
    _save(root, state)
    print(f"blocker added ({len(state.blockers)} open)")
    return 0


def _cmd_clear_blockers(args: argparse.Namespace) -> int:
    """Remove all open blockers.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code.

    """
    root = Path(args.root)
    state = _load(root, args.feature)
    state.blockers.clear()
    _save(root, state)
    print("blockers cleared")
    return 0


def _cmd_show(args: argparse.Namespace) -> int:
    """Print the current STATE.md content.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code.

    """
    state = _load(Path(args.root), args.feature)
    print(_render(state))
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Validate the STATE.md schema for a feature.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code: ``0`` when valid, ``1`` otherwise.

    """
    try:
        _load(Path(args.root), args.feature)
    except (FileNotFoundError, ValueError) as error:
        print(f"invalid: {error}", file=sys.stderr)
        return 1
    print("valid")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands.

    Returns:
        The configured argument parser.

    """
    parser = argparse.ArgumentParser(description="Manage per-feature STATE.md files.")
    parser.add_argument(
        "--root",
        default=_DEFAULT_ROOT,
        help=f"artifacts root directory (default: {_DEFAULT_ROOT})",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a new STATE.md")
    init.add_argument("--feature", required=True)
    init.add_argument("--phase", default="phase_1")
    init.set_defaults(func=_cmd_init)

    set_task = sub.add_parser("set-task", help="set a task status")
    set_task.add_argument("--feature", required=True)
    set_task.add_argument("--task", required=True)
    set_task.add_argument("--status", required=True, choices=_VALID_STATUSES)
    set_task.set_defaults(func=_cmd_set_task)

    set_phase = sub.add_parser("set-phase", help="set the current phase")
    set_phase.add_argument("--feature", required=True)
    set_phase.add_argument("--phase", required=True)
    set_phase.set_defaults(func=_cmd_set_phase)

    add_blocker = sub.add_parser("add-blocker", help="append a blocker")
    add_blocker.add_argument("--feature", required=True)
    add_blocker.add_argument("--text", required=True)
    add_blocker.set_defaults(func=_cmd_add_blocker)

    clear_blockers = sub.add_parser("clear-blockers", help="remove all blockers")
    clear_blockers.add_argument("--feature", required=True)
    clear_blockers.set_defaults(func=_cmd_clear_blockers)

    show = sub.add_parser("show", help="print STATE.md")
    show.add_argument("--feature", required=True)
    show.set_defaults(func=_cmd_show)

    validate = sub.add_parser("validate", help="validate STATE.md schema")
    validate.add_argument("--feature", required=True)
    validate.set_defaults(func=_cmd_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the STATE.md management CLI.

    Args:
        argv: Optional argument vector. Defaults to ``sys.argv[1:]``.

    Returns:
        Process exit code.

    """
    _configure_stdio_encoding()
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


def _configure_stdio_encoding() -> None:
    """Force ``stdout`` / ``stderr`` to UTF-8 to avoid mojibake on Windows.

    On Windows the default console encoding is often cp932 (Shift_JIS), which
    cannot represent the Japanese characters used in STATE.md's auto-generated
    body. Re-configuring the streams to UTF-8 keeps the CLI output readable
    regardless of platform.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    sys.exit(main())

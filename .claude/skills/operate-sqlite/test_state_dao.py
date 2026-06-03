"""Tests for the ``state_dao`` workflow state database CLI."""

import sqlite3
from pathlib import Path

import pytest
import state_dao


@pytest.fixture
def root(tmp_path: Path) -> Path:
    """Return a temporary artifacts root for an isolated state database."""
    return tmp_path / ".artifacts"


def _run(root: Path, *args: str) -> int:
    """Invoke the CLI against ``root`` and return its exit code."""
    return state_dao.main(["--root", str(root), *args])


def test_parse_task_round_trips() -> None:
    assert state_dao.parse_task("task_1_2") == (1, 2)
    assert state_dao.parse_task("TASK_3_10") == (3, 10)
    assert state_dao.format_task(1, 2) == "task_1_2"


def test_parse_task_rejects_bad_token() -> None:
    with pytest.raises(ValueError, match="invalid task id"):
        state_dao.parse_task("task_1")


def test_parse_phase_accepts_both_forms() -> None:
    assert state_dao.parse_phase("phase_2") == 2
    assert state_dao.parse_phase("2") == 2
    assert state_dao.format_phase(2) == "phase_2"


def test_init_creates_database_and_feature(root: Path) -> None:
    assert _run(root, "init", "--feature", "auth") == 0
    assert (root / "state.db").exists()
    # init is idempotent
    assert _run(root, "init", "--feature", "auth") == 0


def test_set_task_requires_existing_feature(root: Path) -> None:
    assert (
        _run(
            root,
            "set-task",
            "--feature",
            "ghost",
            "--task",
            "task_1_1",
            "--status",
            "done",
        )
        == 2
    )


def test_progress_recomputed_on_set_task(
    root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(root, "init", "--feature", "auth")
    _run(
        root,
        "set-task",
        "--feature",
        "auth",
        "--task",
        "task_1_1",
        "--status",
        "done",
    )
    _run(
        root,
        "set-task",
        "--feature",
        "auth",
        "--task",
        "task_1_2",
        "--status",
        "todo",
    )
    capsys.readouterr()
    _run(root, "show", "--feature", "auth")
    out = capsys.readouterr().out
    assert "1/2 (50%)" in out
    assert "| task_1_1 | done |" in out


def test_set_task_upserts_status(
    root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(root, "init", "--feature", "auth")
    _run(
        root,
        "set-task",
        "--feature",
        "auth",
        "--task",
        "task_1_1",
        "--status",
        "todo",
    )
    _run(
        root,
        "set-task",
        "--feature",
        "auth",
        "--task",
        "task_1_1",
        "--status",
        "done",
    )
    capsys.readouterr()
    _run(root, "list-tasks", "--feature", "auth", "--status", "done")
    assert capsys.readouterr().out.strip() == "task_1_1"


def test_set_phase_updates_current_phase(
    root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(root, "init", "--feature", "auth")
    _run(root, "set-phase", "--feature", "auth", "--phase", "phase_2")
    capsys.readouterr()
    _run(root, "show", "--feature", "auth")
    assert "現在フェーズ: phase_2" in capsys.readouterr().out


def test_blockers_add_and_clear(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _run(root, "init", "--feature", "auth")
    _run(root, "add-blocker", "--feature", "auth", "--text", "需要待ち")
    capsys.readouterr()
    _run(root, "show", "--feature", "auth")
    assert "- 需要待ち" in capsys.readouterr().out
    _run(root, "clear-blockers", "--feature", "auth")
    capsys.readouterr()
    _run(root, "show", "--feature", "auth")
    assert "- なし" in capsys.readouterr().out


def test_list_tasks_filters_by_phase(
    root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(root, "init", "--feature", "auth")
    _run(
        root,
        "set-task",
        "--feature",
        "auth",
        "--task",
        "task_1_1",
        "--status",
        "done",
    )
    _run(
        root,
        "set-task",
        "--feature",
        "auth",
        "--task",
        "task_2_1",
        "--status",
        "todo",
    )
    capsys.readouterr()
    _run(root, "list-tasks", "--feature", "auth", "--phase", "phase_1")
    assert capsys.readouterr().out.strip() == "task_1_1"


def test_features_are_isolated_in_one_database(
    root: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    _run(root, "init", "--feature", "auth")
    _run(root, "init", "--feature", "billing")
    _run(
        root,
        "set-task",
        "--feature",
        "auth",
        "--task",
        "task_1_1",
        "--status",
        "done",
    )
    capsys.readouterr()
    _run(root, "list-tasks", "--feature", "billing", "--status", "done")
    assert capsys.readouterr().out.strip() == ""


def test_clear_blockers_cascades_with_feature(root: Path) -> None:
    _run(root, "init", "--feature", "auth")
    _run(root, "add-blocker", "--feature", "auth", "--text", "x")
    db = root / "state.db"
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM features WHERE feature = ?", ("auth",))
        conn.commit()
        remaining = conn.execute("SELECT COUNT(*) FROM blockers").fetchone()[0]
    assert remaining == 0


def test_validate_reports_missing_feature(root: Path) -> None:
    assert _run(root, "validate", "--feature", "ghost") == 1


def test_validate_passes_for_initialized_feature(root: Path) -> None:
    _run(root, "init", "--feature", "auth")
    assert _run(root, "validate", "--feature", "auth") == 0

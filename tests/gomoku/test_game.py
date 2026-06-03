"""Integration tests for GameController."""

from __future__ import annotations

import random
from unittest.mock import MagicMock

from gomoku.board import Board
from gomoku.constants import CPU_STONE, HUMAN_STONE, WIN_LENGTH
from gomoku.game import GameController
from gomoku.players import CPUPlayer, HumanPlayer


def _make_controller(
    board: Board | None = None,
    human: HumanPlayer | None = None,
    cpu: CPUPlayer | None = None,
    out: MagicMock | None = None,
) -> tuple:
    """Build a GameController with sensible defaults for testing."""
    if board is None:
        board = Board()
    if out is None:
        out = MagicMock()
    if human is None:
        human = HumanPlayer(stone=HUMAN_STONE, input_fn=lambda _: "0 0", out=out)
    if cpu is None:
        cpu = CPUPlayer(
            stone=CPU_STONE,
            opponent_stone=HUMAN_STONE,
            rng=random.Random(42),
        )
    gc = GameController(board=board, human=human, cpu=cpu, out=out)
    return gc, board, human, cpu, out


def _setup_four_in_row(board: Board, x_start: int, y: int, stone: str) -> None:
    """Place 4 consecutive stones starting at (x_start, y) horizontally."""
    for i in range(WIN_LENGTH - 1):
        board.place_stone(x_start + i, y, stone)


# region play_once tests


def test_play_once_human_wins() -> None:
    """Human completes 5 in a row on their first move."""
    board = Board()
    out = MagicMock()
    # Set up 4 consecutive human stones at (0,0)-(3,0), winning move is (4,0)
    _setup_four_in_row(board, 0, 0, HUMAN_STONE)

    human = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: "4 0",
        out=out,
    )
    cpu = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=random.Random(0))

    gc = GameController(board=board, human=human, cpu=cpu, out=out)
    gc.play_once()

    all_output = " ".join(str(c) for c in out.call_args_list)
    assert HUMAN_STONE in all_output


def test_play_once_cpu_wins() -> None:
    """CPU completes 5 in a row after Human's first move."""
    board = Board()
    out = MagicMock()

    # Set up 4 consecutive CPU stones at (0,1)-(3,1), CPU winning move is (4,1)
    for i in range(WIN_LENGTH - 1):
        board.place_stone(i, 1, CPU_STONE)

    # Human places at (0,0) (safe, not winning), CPU should detect win at (4,1)
    human = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: "0 0",
        out=out,
    )
    # CPU should pick (4,1) as winning move with any rng
    cpu = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=random.Random(0))

    gc = GameController(board=board, human=human, cpu=cpu, out=out)
    gc.play_once()

    all_output = " ".join(str(c) for c in out.call_args_list)
    assert CPU_STONE in all_output


def test_play_once_draw() -> None:
    """Board becomes full resulting in a draw."""
    board = Board(size=3)
    out = MagicMock()

    # Fill board except one cell (2,2)
    # Use alternating stones to avoid a winner
    # Layout: H C H / C H C / H C .
    stones = [
        (0, 0, HUMAN_STONE),
        (1, 0, CPU_STONE),
        (2, 0, HUMAN_STONE),
        (0, 1, CPU_STONE),
        (1, 1, HUMAN_STONE),
        (2, 1, CPU_STONE),
        (0, 2, HUMAN_STONE),
        (1, 2, CPU_STONE),
        # (2,2) left empty
    ]
    for x, y, stone in stones:
        board.place_stone(x, y, stone)

    # Human places at (2,2) to fill the board - no winner since size=3, WIN_LENGTH=5
    human = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: "2 2",
        out=out,
    )
    cpu = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=random.Random(0))

    gc = GameController(board=board, human=human, cpu=cpu, out=out)
    gc.play_once()

    all_output = " ".join(str(c) for c in out.call_args_list)
    assert "引き分け" in all_output


def test_play_once_turn_order() -> None:
    """Turn order follows Human -> CPU -> Human.

    Uses a real Board but wraps place_stone with a MagicMock spy to capture
    the stone argument for each call in order.

    Setup: Human stones at (1,0),(2,0),(3,0) pre-placed.
    Game moves (captured via spy):
      Move 1 (Human): (4,0) -> 4-in-a-row, no win.
      Move 2 (CPU):   somewhere (CPU has no winning move).
      Move 3 (Human): (0,0) -> 5-in-a-row, Human wins.

    Because the CPU will block (0,0) after Human places (4,0), the Human
    input iterator provides a fallback sequence that guarantees enough inputs.
    To avoid CPU interference we choose a row (y=7) far from any pre-placed
    stones so that CPU has no winning/blocking incentive there.
    """
    out = MagicMock()

    # Use row 7, far from edges: pre-place (1,7),(2,7),(3,7)
    board2 = Board()
    for i in range(1, 4):
        board2.place_stone(i, 7, HUMAN_STONE)

    # Spy on place_stone to record (stone,) for each call
    place_stone_spy = MagicMock(side_effect=board2.place_stone)
    board2.place_stone = place_stone_spy  # type: ignore[method-assign]

    # Human move 1: (4,7) -> 4-in-a-row in row 7 (no win yet).
    # CPU will block (0,7) or (5,7) as winning threats. Whichever it blocks,
    # Human completes 5-in-a-row on the other end.
    # Provide both possibilities: if (0,7) is taken by CPU, use (5,7); vice versa.
    remaining_ends = ["5 7", "0 7"]  # CPU blocks one; Human uses the other

    call_count = 0

    def human_input(_: str) -> str:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "4 7"
        # Move 3: try (5,7) first, then (0,7)
        for pos in remaining_ends:
            x_s, y_s = pos.split()
            x_i, y_i = int(x_s), int(y_s)
            if board2.is_valid_move(x_i, y_i):
                return pos
        return "0 14"  # ultimate fallback (should not be reached)

    human2 = HumanPlayer(stone=HUMAN_STONE, input_fn=human_input, out=out)
    cpu2 = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=random.Random(0))

    gc = GameController(board=board2, human=human2, cpu=cpu2, out=out)
    gc.play_once()

    stones_placed = [c.args[2] for c in place_stone_spy.call_args_list]
    # Verify at least 3 moves happened and the order is H, C, H
    assert len(stones_placed) >= 3
    assert stones_placed[0] == HUMAN_STONE
    assert stones_placed[1] == CPU_STONE
    assert stones_placed[2] == HUMAN_STONE


# endregion

# region run tests


def test_run_no_replay() -> None:
    """Run returns 0 when confirm_fn returns 'n' after one game.

    play_once is replaced with a stub because run() resets the board at the
    start of each game; driving a real game with constant input would loop
    forever (an occupied cell re-prompts indefinitely). Full-game behavior is
    covered by the test_play_once_* tests.
    """
    gc, _board, _human, _cpu, _out = _make_controller()
    gc.play_once = MagicMock()  # type: ignore[method-assign]

    result = gc.run(confirm_fn=lambda _: "n")

    assert result == 0
    assert gc.play_once.call_count == 1


def test_run_with_replay() -> None:
    """Run executes two games when confirm_fn returns 'y' then 'n'."""
    out = MagicMock()

    confirm_responses = iter(["y", "n"])

    reset_count = 0
    original_board = Board()
    original_reset = original_board.reset

    def tracking_reset() -> None:
        nonlocal reset_count
        reset_count += 1
        original_reset()

    original_board.reset = tracking_reset  # type: ignore[method-assign]

    # Provide enough moves: game 1 (human wins quickly), game 2 (human wins quickly)
    # After board.reset, 4 stones are gone so we re-place them via HumanPlayer
    # Use a simpler approach: monkeypatch play_once
    play_once_count = 0

    cpu = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=random.Random(0))
    human = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: "0 0",
        out=out,
    )
    gc = GameController(board=original_board, human=human, cpu=cpu, out=out)

    def spy_play_once() -> None:
        nonlocal play_once_count
        play_once_count += 1
        # Just pass; we don't want a full game, just count calls
        # We need to set board as "full" to avoid infinite loops
        gc._board.grid = [
            [
                HUMAN_STONE if (x + y) % 2 == 0 else CPU_STONE
                for x in range(gc._board.size)
            ]
            for y in range(gc._board.size)
        ]

    gc.play_once = spy_play_once  # type: ignore[method-assign]

    result = gc.run(confirm_fn=lambda _: next(confirm_responses))
    assert result == 0
    assert play_once_count == 2


def test_run_keyboard_interrupt() -> None:
    """Run returns 0 and shows exit message on KeyboardInterrupt.

    play_once is stubbed so the test exercises run()'s interrupt handling
    around the replay prompt without running a real game.
    """
    gc, _board, _human, _cpu, out = _make_controller()
    gc.play_once = MagicMock()  # type: ignore[method-assign]

    def confirm_raise(_: str) -> str:
        raise KeyboardInterrupt

    result = gc.run(confirm_fn=confirm_raise)

    assert result == 0
    all_output = " ".join(str(c) for c in out.call_args_list)
    assert "終了" in all_output


def test_run_eof_error() -> None:
    """Run returns 0 and shows exit message on EOFError.

    play_once is stubbed so the test exercises run()'s EOF handling around the
    replay prompt without running a real game.
    """
    gc, _board, _human, _cpu, out = _make_controller()
    gc.play_once = MagicMock()  # type: ignore[method-assign]

    def confirm_raise(_: str) -> str:
        raise EOFError

    result = gc.run(confirm_fn=confirm_raise)

    assert result == 0
    all_output = " ".join(str(c) for c in out.call_args_list)
    assert "終了" in all_output


def test_run_replay_invalid_then_quit() -> None:
    """Invalid replay input triggers re-prompt; 'n' then terminates.

    play_once is stubbed so the test focuses on run()'s replay re-prompt loop.
    """
    gc, _board, _human, _cpu, out = _make_controller()
    gc.play_once = MagicMock()  # type: ignore[method-assign]

    confirm_responses = iter(["x", "n"])
    result = gc.run(confirm_fn=lambda _: next(confirm_responses))

    assert result == 0
    assert gc.play_once.call_count == 1
    all_output = " ".join(str(c) for c in out.call_args_list)
    assert "y または n" in all_output


# endregion

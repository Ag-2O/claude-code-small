"""Unit tests for Player, HumanPlayer, and CPUPlayer classes."""

import copy
import random

import pytest

from gomoku.board import Board
from gomoku.constants import BOARD_SIZE, CPU_STONE, HUMAN_STONE
from gomoku.players import CPUPlayer, HumanPlayer, Player

# region HumanPlayer


def test_human_player_valid_input_direct() -> None:
    inputs = iter(["7 3"])
    board = Board()
    player = HumanPlayer(stone=HUMAN_STONE, input_fn=lambda _: next(inputs))
    result = player.get_move(board)
    assert result == (7, 3)


def test_human_player_format_error_then_valid() -> None:
    out_calls: list[str] = []
    inputs = iter(["7", "3 4"])
    board = Board()
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    result = player.get_move(board)
    assert result == (3, 4)
    assert len(out_calls) >= 1


def test_human_player_non_integer_then_valid() -> None:
    out_calls: list[str] = []
    inputs = iter(["a b", "2 5"])
    board = Board()
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    result = player.get_move(board)
    assert result == (2, 5)
    assert len(out_calls) >= 1


def test_human_player_out_of_range_negative_then_valid() -> None:
    out_calls: list[str] = []
    inputs = iter(["-1 3", "0 0"])
    board = Board()
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    result = player.get_move(board)
    assert result == (0, 0)
    assert len(out_calls) >= 1


def test_human_player_out_of_range_too_large_then_valid() -> None:
    out_calls: list[str] = []
    inputs = iter([f"{BOARD_SIZE} 0", "1 1"])
    board = Board()
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    result = player.get_move(board)
    assert result == (1, 1)
    assert len(out_calls) >= 1


def test_human_player_occupied_then_valid() -> None:
    out_calls: list[str] = []
    board = Board()
    board.place_stone(3, 3, CPU_STONE)
    inputs = iter(["3 3", "4 4"])
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    result = player.get_move(board)
    assert result == (4, 4)
    assert len(out_calls) >= 1


def test_human_player_format_error_message_displayed() -> None:
    out_calls: list[str] = []
    inputs = iter(["bad input", "0 0"])
    board = Board()
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    player.get_move(board)
    assert len(out_calls) >= 1


def test_human_player_range_error_message_displayed() -> None:
    out_calls: list[str] = []
    inputs = iter(["99 99", "0 0"])
    board = Board()
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    player.get_move(board)
    assert len(out_calls) >= 1


def test_human_player_occupied_error_message_displayed() -> None:
    out_calls: list[str] = []
    board = Board()
    board.place_stone(5, 5, HUMAN_STONE)
    inputs = iter(["5 5", "6 6"])
    player = HumanPlayer(
        stone=HUMAN_STONE,
        input_fn=lambda _: next(inputs),
        out=out_calls.append,
    )
    player.get_move(board)
    assert len(out_calls) >= 1


# endregion


# region CPUPlayer


def test_cpu_player_wins_horizontal() -> None:
    board = Board()
    # 自石を x=0..3, y=7 に配置（x=4 で 5 連完成）
    for x in range(4):
        board.place_stone(x, 7, CPU_STONE)
    rng = random.Random(0)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    move = player.get_move(board)
    assert move == (4, 7)


def test_cpu_player_wins_vertical() -> None:
    board = Board()
    for y in range(4):
        board.place_stone(7, y, CPU_STONE)
    rng = random.Random(0)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    move = player.get_move(board)
    assert move == (7, 4)


def test_cpu_player_wins_diagonal_down_right() -> None:
    board = Board()
    for i in range(4):
        board.place_stone(i, i, CPU_STONE)
    rng = random.Random(0)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    move = player.get_move(board)
    assert move == (4, 4)


def test_cpu_player_wins_diagonal_down_left() -> None:
    board = Board()
    for i in range(4):
        board.place_stone(4 - i, i, CPU_STONE)
    rng = random.Random(0)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    move = player.get_move(board)
    assert move == (0, 4)


def test_cpu_player_blocks_opponent() -> None:
    board = Board()
    # 相手が x=0..3, y=0 に 4 連（x=4 で勝利可能）
    for x in range(4):
        board.place_stone(x, 0, HUMAN_STONE)
    # CPU は自石なし（即勝利マスなし）
    rng = random.Random(0)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    move = player.get_move(board)
    assert move == (4, 0)


def test_cpu_player_prefers_neighbor_when_no_win_or_block() -> None:
    board = Board()
    # CPU の石を 1 個だけ置く（8 近傍に空きあり、勝利/ブロック不要）
    board.place_stone(7, 7, CPU_STONE)
    rng = random.Random(42)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    move = player.get_move(board)
    # 8 近傍のいずれか
    neighbors = {
        (7 + dx, 7 + dy)
        for dx in (-1, 0, 1)
        for dy in (-1, 0, 1)
        if (dx, dy) != (0, 0)
        if 0 <= 7 + dx < BOARD_SIZE and 0 <= 7 + dy < BOARD_SIZE
    }
    assert move in neighbors


def test_cpu_player_any_empty_when_no_neighbors() -> None:
    board = Board()
    rng = random.Random(0)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    move = player.get_move(board)
    assert board.is_valid_move(*move)


def test_cpu_player_deterministic_with_seed() -> None:
    board = Board()
    board.place_stone(7, 7, CPU_STONE)
    rng1 = random.Random(123)  # noqa: S311
    rng2 = random.Random(123)  # noqa: S311
    player1 = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng1)
    player2 = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng2)
    move1 = player1.get_move(board)
    move2 = player2.get_move(board)
    assert move1 == move2


def test_cpu_player_restores_board_after_get_move() -> None:
    board = Board()
    board.place_stone(7, 7, CPU_STONE)
    grid_before = copy.deepcopy(board.grid)
    rng = random.Random(0)  # noqa: S311
    player = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE, rng=rng)
    player.get_move(board)
    assert board.grid == grid_before


def test_player_is_abstract() -> None:
    with pytest.raises(TypeError):
        Player(stone=HUMAN_STONE)  # type: ignore[abstract]


# endregion

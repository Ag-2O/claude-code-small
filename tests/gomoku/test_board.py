"""Unit tests for Board class."""

from gomoku.board import Board
from gomoku.constants import EMPTY, HUMAN_STONE


def test_init_creates_empty_grid() -> None:
    board = Board()
    assert board.size == 15
    assert len(board.grid) == 15
    assert all(len(row) == 15 for row in board.grid)
    assert all(board.grid[y][x] == EMPTY for y in range(15) for x in range(15))


def test_init_custom_size() -> None:
    board = Board(size=5)
    assert board.size == 5
    assert len(board.grid) == 5
    assert all(len(row) == 5 for row in board.grid)


def test_is_valid_move_empty_cell() -> None:
    board = Board(size=5)
    assert board.is_valid_move(0, 0) is True
    assert board.is_valid_move(4, 4) is True
    assert board.is_valid_move(2, 3) is True


def test_is_valid_move_out_of_range() -> None:
    board = Board(size=5)
    assert board.is_valid_move(-1, 0) is False
    assert board.is_valid_move(5, 0) is False
    assert board.is_valid_move(0, -1) is False
    assert board.is_valid_move(0, 5) is False
    assert board.is_valid_move(-1, -1) is False
    assert board.is_valid_move(5, 5) is False


def test_is_valid_move_occupied() -> None:
    board = Board(size=5)
    board.place_stone(2, 2, HUMAN_STONE)
    assert board.is_valid_move(2, 2) is False


def test_place_stone() -> None:
    board = Board(size=5)
    board.place_stone(1, 2, HUMAN_STONE)
    assert board.grid[2][1] == HUMAN_STONE


def test_check_winner_horizontal() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    for x in range(5):
        board.place_stone(x, 0, stone)
    assert board.check_winner_from(4, 0, stone) is True


def test_check_winner_vertical() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    for y in range(5):
        board.place_stone(0, y, stone)
    assert board.check_winner_from(0, 4, stone) is True


def test_check_winner_diagonal_down_right() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    for i in range(5):
        board.place_stone(i, i, stone)
    assert board.check_winner_from(4, 4, stone) is True


def test_check_winner_diagonal_down_left() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    for i in range(5):
        board.place_stone(4 - i, i, stone)
    assert board.check_winner_from(0, 4, stone) is True


def test_check_winner_long_row() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    for x in range(6):
        board.place_stone(x, 0, stone)
    assert board.check_winner_from(5, 0, stone) is True


def test_check_winner_four_in_row() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    for x in range(4):
        board.place_stone(x, 0, stone)
    assert board.check_winner_from(3, 0, stone) is False


def test_check_winner_boundary_five() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    # Place 5 stones at the right edge: x=5..9
    for x in range(5, 10):
        board.place_stone(x, 0, stone)
    assert board.check_winner_from(9, 0, stone) is True


def test_check_winner_boundary_false() -> None:
    board = Board(size=10)
    stone = HUMAN_STONE
    # Place only 3 stones at right edge
    for x in range(7, 10):
        board.place_stone(x, 0, stone)
    assert board.check_winner_from(9, 0, stone) is False


def test_is_full_empty() -> None:
    board = Board(size=5)
    assert board.is_full() is False


def test_is_full_complete() -> None:
    board = Board(size=5)
    for y in range(5):
        for x in range(5):
            board.place_stone(x, y, HUMAN_STONE)
    assert board.is_full() is True


def test_is_full_one_empty() -> None:
    board = Board(size=5)
    for y in range(5):
        for x in range(5):
            board.place_stone(x, y, HUMAN_STONE)
    # Reset one cell manually to simulate one empty
    board.grid[4][4] = EMPTY
    assert board.is_full() is False


def test_get_empty_cells_initial() -> None:
    board = Board(size=5)
    cells = board.get_empty_cells()
    assert len(cells) == 25


def test_get_empty_cells_after_place() -> None:
    board = Board(size=5)
    board.place_stone(2, 3, HUMAN_STONE)
    cells = board.get_empty_cells()
    assert len(cells) == 24
    assert (2, 3) not in cells


def test_get_empty_cells_all_filled() -> None:
    board = Board(size=5)
    for y in range(5):
        for x in range(5):
            board.place_stone(x, y, HUMAN_STONE)
    assert board.get_empty_cells() == []


def test_reset() -> None:
    board = Board(size=5)
    board.place_stone(0, 0, HUMAN_STONE)
    board.place_stone(1, 1, HUMAN_STONE)
    board.reset()
    assert all(board.grid[y][x] == EMPTY for y in range(5) for x in range(5))


def test_reset_is_full_false() -> None:
    board = Board(size=5)
    for y in range(5):
        for x in range(5):
            board.place_stone(x, y, HUMAN_STONE)
    board.reset()
    assert board.is_full() is False


def test_display_column_headers() -> None:
    board = Board(size=15)
    lines: list[str] = []
    board.display(out=lines.append)
    # Total lines: 1 header + 15 rows = 16
    assert len(lines) == 16
    header = lines[0]
    # Column numbers should be 2-digit right-aligned
    assert " 0" in header
    assert "10" in header
    assert "14" in header


def test_display_row_count() -> None:
    board = Board(size=5)
    lines: list[str] = []
    board.display(out=lines.append)
    # 1 header + size rows
    assert len(lines) == 6


def test_display_small_board_format() -> None:
    board = Board(size=5)
    lines: list[str] = []
    board.display(out=lines.append)
    # First data line should start with row index right-aligned
    first_row = lines[1]
    assert first_row.startswith(" 0")

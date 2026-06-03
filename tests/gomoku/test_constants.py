from gomoku import BOARD_SIZE, CPU_STONE, EMPTY, HUMAN_STONE, WIN_LENGTH
from gomoku.constants import BOARD_SIZE as C_BOARD_SIZE
from gomoku.constants import CPU_STONE as C_CPU_STONE
from gomoku.constants import EMPTY as C_EMPTY
from gomoku.constants import HUMAN_STONE as C_HUMAN_STONE
from gomoku.constants import WIN_LENGTH as C_WIN_LENGTH


def test_board_size() -> None:
    assert BOARD_SIZE == 15
    assert isinstance(BOARD_SIZE, int)


def test_win_length() -> None:
    assert WIN_LENGTH == 5
    assert isinstance(WIN_LENGTH, int)


def test_empty() -> None:
    assert EMPTY == "."
    assert isinstance(EMPTY, str)


def test_human_stone() -> None:
    assert HUMAN_STONE == "○"
    assert isinstance(HUMAN_STONE, str)


def test_cpu_stone() -> None:
    assert CPU_STONE == "×"
    assert isinstance(CPU_STONE, str)


def test_constants_accessible_from_package() -> None:
    assert C_BOARD_SIZE == BOARD_SIZE
    assert C_WIN_LENGTH == WIN_LENGTH
    assert C_EMPTY == EMPTY
    assert C_HUMAN_STONE == HUMAN_STONE
    assert C_CPU_STONE == CPU_STONE

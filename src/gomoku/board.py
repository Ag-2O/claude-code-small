"""Board class for the gomoku game."""

from __future__ import annotations

from typing import TYPE_CHECKING

from gomoku.constants import BOARD_SIZE, EMPTY, WIN_LENGTH

if TYPE_CHECKING:
    from collections.abc import Callable


class Board:
    """Represents the gomoku game board.

    Attributes:
        size: The board dimension (size x size).
        grid: 2D list representing board state. Access via grid[y][x].

    """

    def __init__(self, size: int = BOARD_SIZE) -> None:
        """Initialize an empty board.

        Args:
            size: Board dimension. Defaults to BOARD_SIZE (15).

        """
        self.size = size
        self.grid: list[list[str]] = [[EMPTY] * size for _ in range(size)]

    def display(self, out: Callable[[str], None] = print) -> None:
        """Display the board with column headers and row indices.

        Args:
            out: Output callback. Defaults to print.

        """
        header = "    " + "  ".join(f"{i:2d}" for i in range(self.size))
        out(header)
        for y in range(self.size):
            row = f"{y:2d}  " + "  ".join(
                f" {self.grid[y][x]}" for x in range(self.size)
            )
            out(row)

    def is_valid_move(self, x: int, y: int) -> bool:
        """Check if placing a stone at (x, y) is a valid move.

        Args:
            x: Column index (0-based).
            y: Row index (0-based).

        Returns:
            True if the cell is within bounds and empty.

        """
        return 0 <= x < self.size and 0 <= y < self.size and self.grid[y][x] == EMPTY

    def place_stone(self, x: int, y: int, stone: str) -> None:
        """Place a stone at the given position.

        Precondition: is_valid_move(x, y) must be True (caller's responsibility).

        Args:
            x: Column index (0-based).
            y: Row index (0-based).
            stone: Stone character to place.

        """
        self.grid[y][x] = stone

    def check_winner_from(self, x: int, y: int, stone: str) -> bool:
        """Check if placing at (x, y) results in a win for the given stone.

        Counts consecutive stones in 4 directions. WIN_LENGTH or more is a win.

        Args:
            x: Column index of the last placed stone.
            y: Row index of the last placed stone.
            stone: Stone character to check.

        Returns:
            True if WIN_LENGTH or more consecutive stones exist through (x, y).

        """
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1
            for sign in (1, -1):
                nx, ny = x + dx * sign, y + dy * sign
                while (
                    0 <= nx < self.size
                    and 0 <= ny < self.size
                    and self.grid[ny][nx] == stone
                ):
                    count += 1
                    nx += dx * sign
                    ny += dy * sign
            if count >= WIN_LENGTH:
                return True
        return False

    def is_full(self) -> bool:
        """Check if the board is completely filled.

        Returns:
            True if no empty cells remain.

        """
        return all(
            self.grid[y][x] != EMPTY for y in range(self.size) for x in range(self.size)
        )

    def get_empty_cells(self) -> list[tuple[int, int]]:
        """Return a list of all empty cell coordinates.

        Returns:
            List of (x, y) tuples for all empty cells.

        """
        return [
            (x, y)
            for y in range(self.size)
            for x in range(self.size)
            if self.grid[y][x] == EMPTY
        ]

    def reset(self) -> None:
        """Reset the board to the initial empty state."""
        self.grid = [[EMPTY] * self.size for _ in range(self.size)]

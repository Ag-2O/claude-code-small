"""Player classes for the gomoku game."""

from __future__ import annotations

import abc
import random
from typing import TYPE_CHECKING

from gomoku.constants import BOARD_SIZE, EMPTY

if TYPE_CHECKING:
    from collections.abc import Callable

    from gomoku.board import Board

_ERR_FORMAT = "形式エラー: `x y` 形式で整数を入力してください。"
_ERR_RANGE = f"範囲エラー: 0 以上 {BOARD_SIZE - 1} 以下の整数を入力してください。"
_ERR_OCCUPIED = "重複エラー: そのマスはすでに着手済みです。"
_INPUT_PROMPT = "石を置く座標を入力してください（例: 7 3）: "


class Player(abc.ABC):
    """Abstract base class for gomoku players.

    Attributes:
        stone: The stone character this player uses.

    """

    stone: str

    def __init__(self, stone: str) -> None:
        """Initialize the player with the given stone.

        Args:
            stone: Stone character to use on the board.

        """
        self.stone = stone

    @abc.abstractmethod
    def get_move(self, board: Board) -> tuple[int, int]:
        """Determine the next move.

        Args:
            board: The current board state.

        Returns:
            A tuple (x, y) representing the chosen column and row.

        """


class HumanPlayer(Player):
    """Human player that reads moves from standard input.

    Attributes:
        stone: The stone character this player uses.

    """

    def __init__(
        self,
        stone: str,
        input_fn: Callable[[str], str] = input,
        out: Callable[[str], None] = print,
    ) -> None:
        """Initialize the human player.

        Args:
            stone: Stone character to use on the board.
            input_fn: Callable used to read user input. Defaults to built-in input.
            out: Callable used to write output messages. Defaults to built-in print.

        """
        super().__init__(stone)
        self._input_fn = input_fn
        self._out = out

    def _parse_tokens(self, raw: str) -> tuple[int, int] | None:
        """Parse raw input into an (x, y) integer pair, or return None on error.

        Args:
            raw: The raw string read from input.

        Returns:
            Parsed (x, y) tuple, or None if the format is invalid.

        """
        tokens = raw.split()
        if len(tokens) != 2:  # noqa: PLR2004
            return None
        try:
            return int(tokens[0]), int(tokens[1])
        except ValueError:
            return None

    def get_move(self, board: Board) -> tuple[int, int]:
        """Prompt the human player for a valid move.

        Loops until the player provides a valid (x, y) coordinate.
        Displays an error message for format errors, out-of-range values,
        and already-occupied cells.

        Args:
            board: The current board state.

        Returns:
            A valid (x, y) tuple accepted by the board.

        """
        while True:
            raw = self._input_fn(_INPUT_PROMPT)
            parsed = self._parse_tokens(raw)
            if parsed is None:
                self._out(_ERR_FORMAT)
                continue
            x, y = parsed
            if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                self._out(_ERR_RANGE)
                continue
            if not board.is_valid_move(x, y):
                self._out(_ERR_OCCUPIED)
                continue
            return x, y


class CPUPlayer(Player):
    """CPU player that selects moves using a priority-based rule strategy.

    Priority order:

    1. Winning move (places own stone to complete 5 in a row).
    2. Blocking move (prevents opponent from completing 5 in a row).
    3. Neighbor move (adjacent to an existing own stone).
    4. Any empty cell.

    Attributes:
        stone: The stone character this player uses.
        opponent_stone: The opponent's stone character.

    """

    def __init__(
        self,
        stone: str,
        opponent_stone: str,
        rng: random.Random | None = None,
    ) -> None:
        """Initialize the CPU player.

        Args:
            stone: Stone character for this player.
            opponent_stone: Stone character for the opponent.
            rng: Random number generator for reproducible behavior.
                 Defaults to a new random.Random() instance.

        """
        super().__init__(stone)
        self.opponent_stone = opponent_stone
        self.rng = rng if rng is not None else random.Random()  # noqa: S311

    def _collect_win_block_sets(
        self,
        board: Board,
        empty_cells: list[tuple[int, int]],
    ) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
        """Scan empty cells to find winning and blocking moves.

        Args:
            board: The current board state.
            empty_cells: List of all currently empty cell coordinates.

        Returns:
            A tuple (win_set, block_set) where each is a set of (x, y) coordinates.

        """
        win_set: set[tuple[int, int]] = set()
        block_set: set[tuple[int, int]] = set()
        for x, y in empty_cells:
            board.grid[y][x] = self.stone
            if board.check_winner_from(x, y, self.stone):
                win_set.add((x, y))
            board.grid[y][x] = EMPTY

            board.grid[y][x] = self.opponent_stone
            if board.check_winner_from(x, y, self.opponent_stone):
                block_set.add((x, y))
            board.grid[y][x] = EMPTY
        return win_set, block_set

    def _collect_neighbor_set(self, board: Board) -> set[tuple[int, int]]:
        """Find empty cells adjacent (8-directional) to own stones.

        Args:
            board: The current board state.

        Returns:
            Set of (x, y) coordinates that are valid and adjacent to own stones.

        """
        neighbor_set: set[tuple[int, int]] = set()
        for y in range(board.size):
            for x in range(board.size):
                if board.grid[y][x] == self.stone:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            if dx == 0 and dy == 0:
                                continue
                            if board.is_valid_move(x + dx, y + dy):
                                neighbor_set.add((x + dx, y + dy))
        return neighbor_set

    def get_move(self, board: Board) -> tuple[int, int]:
        """Select the best move according to the priority strategy.

        Evaluates win, block, neighbor, and any-cell candidate sets in order
        and picks randomly from the first non-empty set.

        Args:
            board: The current board state.

        Returns:
            A tuple (x, y) representing the selected move.

        """
        empty_cells = board.get_empty_cells()
        win_set, block_set = self._collect_win_block_sets(board, empty_cells)
        neighbor_set = self._collect_neighbor_set(board)
        any_set: set[tuple[int, int]] = set(empty_cells)

        for candidate_set in (win_set, block_set, neighbor_set, any_set):
            if candidate_set:
                return self.rng.choice(sorted(candidate_set))

        msg = "No valid move available"
        raise RuntimeError(msg)


__all__ = ["CPUPlayer", "HumanPlayer", "Player"]

"""Entry point for running the gomoku game as a module.

Execute with: uv run python -m gomoku
"""

from __future__ import annotations

import sys

from gomoku.board import Board
from gomoku.constants import CPU_STONE, HUMAN_STONE
from gomoku.game import GameController
from gomoku.players import CPUPlayer, HumanPlayer


def main() -> int:
    """Assemble the game components and start the game loop.

    Returns:
        Exit code returned by GameController.run().

    """
    board = Board()
    human = HumanPlayer(stone=HUMAN_STONE)
    cpu = CPUPlayer(stone=CPU_STONE, opponent_stone=HUMAN_STONE)
    controller = GameController(board=board, human=human, cpu=cpu)
    return controller.run()


if __name__ == "__main__":
    sys.exit(main())

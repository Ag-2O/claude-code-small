"""GameController for the gomoku game."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from gomoku.board import Board
    from gomoku.players import CPUPlayer, HumanPlayer

_TITLE = "=== 五目並べ (Human vs CPU) ==="
_MSG_EXIT = "ゲームを終了します。"
_MSG_DRAW = "引き分けです。"
_MSG_REPLAY_INVALID = "y または n を入力してください。"
_REPLAY_PROMPT = "もう一度プレイしますか？ (y/n): "


class GameController:
    """Manages the gomoku game lifecycle.

    Orchestrates the game loop, move processing, end-of-game handling,
    and replay confirmation.

    Attributes:
        _board: The game board.
        _human: The human player.
        _cpu: The CPU player.
        _out: Output callback.
        _current: Reference to the current player.

    """

    def __init__(
        self,
        board: Board,
        human: HumanPlayer,
        cpu: CPUPlayer,
        out: Callable[[str], None] = print,
    ) -> None:
        """Initialize the controller with the given components.

        Args:
            board: The game board instance.
            human: The human player instance.
            cpu: The CPU player instance.
            out: Output callback. Defaults to built-in print.

        """
        self._board = board
        self._human = human
        self._cpu = cpu
        self._out = out
        self._current: HumanPlayer | CPUPlayer = self._human

    def play_once(self) -> None:
        """Execute a single game from start to finish.

        Displays the title, loops through turns until a win or draw,
        then displays the result.
        """
        self._out(_TITLE)
        while True:
            self._board.display(self._out)

            if self._current is self._human:
                self._out(f"あなたの番です（石: {self._current.stone}）")

            x, y = self._current.get_move(self._board)

            if self._current is self._cpu:
                self._out(f"CPU が {x} {y} に着手しました。")

            self._board.place_stone(x, y, self._current.stone)

            # Win check
            if self._board.check_winner_from(x, y, self._current.stone):
                self._board.display(self._out)
                if self._current is self._human:
                    self._out(f"Human（{self._current.stone}）の勝ちです！")
                else:
                    self._out(f"CPU（{self._current.stone}）の勝ちです！")
                return

            # Draw check
            if self._board.is_full():
                self._out(_MSG_DRAW)
                return

            # Switch turns only when the game continues
            self._current = self._cpu if self._current is self._human else self._human

    def run(self, confirm_fn: Callable[[str], str] = input) -> int:
        """Run the game loop with replay support.

        Executes games in a loop, prompting the player to replay after
        each game. Handles KeyboardInterrupt and EOFError gracefully.

        Args:
            confirm_fn: Callable used to ask the replay question.
                        Defaults to built-in input.

        Returns:
            Exit code 0 on normal termination.

        """
        try:
            while True:
                self._board.reset()
                self._current = self._human
                self.play_once()

                # Replay confirmation loop
                while True:
                    answer = confirm_fn(_REPLAY_PROMPT).strip().lower()
                    if answer == "y":
                        break
                    if answer == "n":
                        return 0
                    self._out(_MSG_REPLAY_INVALID)
        except (KeyboardInterrupt, EOFError):
            self._out(_MSG_EXIT)
            return 0


__all__ = ["GameController"]

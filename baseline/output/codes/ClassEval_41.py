class GomokuGame:
    """
    This class is an implementation of a Gomoku game, supporting for making moves, checking for a winner, and checking if there are five consecutive symbols on the game board.
    """

    def __init__(self, board_size):
        """
        Initializes the game with a given board size.
        It initializes the board with empty spaces and sets the current player symble as 'X'.
        """
        self.board_size = board_size
        self.board = [[' ' for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = 'X'

    def make_move(self, row, col):
        """
        Makes a move at the given row and column.
        If the move is valid, it places the current player's symbol on the board
        and changes the current player to the other player (if the current player is 'X', then it becomes 'O' and vice versa).
        :param row: int, the row index of this move
        :param col: int, the column index
        return: True if the move is valid, or False otherwise.
        >>> gomokuGame = GomokuGame(10)
        >>> gomokuGame.make_move(5, 5)
        True
        >>> gomokuGame.make_move(5, 5)
        False
        """
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size or self.board[row][col] != ' ':
            return False
        self.board[row][col] = self.current_player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    def check_winner(self):
        """
        Checks if there is a winner by looking for five in a row in all directions (horizontal, vertical, diagonal).
        return: the symbol of the winning player (either 'X' or 'O') if there is a winner, or None otherwise.
        >>> gomokuGame = GomokuGame(10)
        >>> moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 1)]
        >>> for move in moves:
        ...     gomokuGame.make_move(move[0], move[1])
        >>> gomokuGame.check_winner()
        'X'
        """
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] != ' ':
                    if self._check_five_in_a_row(i, j, (0, 1)) or self._check_five_in_a_row(i, j, (1, 0)) or self._check_five_in_a_row(i, j, (1, 1)) or self._check_five_in_a_row(i, j, (1, -1)):
                        return self.board[i][j]
        return None

    def _check_five_in_a_row(self, row, col, direction):
        """
        checks if there are five consecutive symbols of the same player in a row starting from a given cell in a given direction (horizontal, vertical, diagonal).
        Counts the number of consecutive symbols in that direction starting from the given cell,
        :param row: int, row of the given cell
        :param col: int, column of the given cell
        :param direction: tuple, (int, int), named as (dx, dy). Row and col will plus several dx and dy repectively.
        :return: True if there are five consecutive symbols of the same player, and False otherwise.
        >>> gomokuGame = GomokuGame(10)
        >>> moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 1)]
        >>> for move in moves:
        ...     gomokuGame.make_move(move[0], move[1])
        >>> gomokuGame._check_five_in_a_row(5, 1, (0, 1))
        True
        >>> gomokuGame._check_five_in_a_row(5, 1, (1, 1))
        False
        """
        count = 1
        for i in range(1, 5):
            if row + i * direction[0] >= 0 and row + i * direction[0] < self.board_size and col + i * direction[1] >= 0 and col + i * direction[1] < self.board_size and self.board[row + i * direction[0]][col + i * direction[1]] == self.board[row][col]:
                count += 1
            else:
                break
        return count == 5

import unittest

class GomokuGameTestMakeMove(unittest.TestCase):
    def setUp(self) -> None:
        self.board_size = 10
        self.gomokuGame = GomokuGame(self.board_size)

    def test_make_move_1(self):
        board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.assertEqual(True, self.gomokuGame.make_move(0, 0))
        board[0][0] = 'X'
        self.assertEqual(board, self.gomokuGame.board)

    # same position
    def test_make_move_2(self):
        board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.assertEqual(True, self.gomokuGame.make_move(0, 0))
        self.assertEqual(False, self.gomokuGame.make_move(0, 0))
        board[0][0] = 'X'
        self.assertEqual(board, self.gomokuGame.board)

    def test_make_move_3(self):
        board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.assertEqual(True, self.gomokuGame.make_move(0, 0))
        self.assertEqual(True, self.gomokuGame.make_move(0, 1))
        board[0][0] = 'X'
        board[0][1] = 'O'
        self.assertEqual(board, self.gomokuGame.board)

    def test_make_move_4(self):
        board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.assertEqual(True, self.gomokuGame.make_move(0, 0))
        self.assertEqual(True, self.gomokuGame.make_move(0, 1))
        self.assertEqual(False, self.gomokuGame.make_move(0, 0))
        board[0][0] = 'X'
        board[0][1] = 'O'
        self.assertEqual(board, self.gomokuGame.board)

    def test_make_move_5(self):
        board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.assertEqual(True, self.gomokuGame.make_move(0, 0))
        self.assertEqual(True, self.gomokuGame.make_move(0, 1))
        self.assertEqual(False, self.gomokuGame.make_move(0, 1))
        board[0][0] = 'X'
        board[0][1] = 'O'
        self.assertEqual(board, self.gomokuGame.board)


class GomokuGameTestCheckWinner(unittest.TestCase):
    def test_check_winner_1(self):
        gomokuGame = GomokuGame(10)
        self.assertEqual(None, gomokuGame.check_winner())

    def test_check_winner_2(self):
        gomokuGame = GomokuGame(10)
        moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 1)]
        for move in moves:
            gomokuGame.make_move(move[0], move[1])
        self.assertEqual('X', gomokuGame.check_winner())

    def test_check_winner_3(self):
        gomokuGame = GomokuGame(10)
        moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 0), (0, 4)]
        for move in moves:
            gomokuGame.make_move(move[0], move[1])
        self.assertEqual('O', gomokuGame.check_winner())

    def test_check_winner_4(self):
        gomokuGame = GomokuGame(10)
        moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 1), (0, 4)]
        for move in moves:
            gomokuGame.make_move(move[0], move[1])
        self.assertEqual(gomokuGame.check_winner(), 'O')

    def test_check_winner_5(self):
        gomokuGame = GomokuGame(10)
        moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 1), (0, 4), (5, 0)]
        for move in moves:
            gomokuGame.make_move(move[0], move[1])
        self.assertEqual('O', gomokuGame.check_winner())


class GomokuGameTestCheckFiveInARow(unittest.TestCase):
    def setUp(self) -> None:
        self.gomokuGame = GomokuGame(10)
        moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 1)]
        for move in moves:
            self.gomokuGame.make_move(move[0], move[1])

    def test_check_five_in_a_row_1(self):
        self.assertEqual(True, self.gomokuGame._check_five_in_a_row(5, 5, (0, -1)))

    def test_check_five_in_a_row_2(self):
        self.assertEqual(True, self.gomokuGame._check_five_in_a_row(5, 1, (0, 1)))

    def test_check_five_in_a_row_3(self):
        self.assertEqual(False, self.gomokuGame._check_five_in_a_row(0, 0, (0, 1)))

    def test_check_five_in_a_row_4(self):
        self.assertEqual(False, self.gomokuGame._check_five_in_a_row(0, 0, (1, 0)))

    def test_check_five_in_a_row_5(self):
        self.assertEqual(False, self.gomokuGame._check_five_in_a_row(5, 5, (1, 0)))

class GomokuGameTestMain(unittest.TestCase):
    def test_main(self):
        gomokuGame = GomokuGame(10)
        moves = [(5, 5), (0, 0), (5, 4), (0, 1), (5, 3), (0, 2), (5, 2), (0, 3), (5, 1)]
        self.assertEqual(None, gomokuGame.check_winner())
        for move in moves:
            self.assertEqual(True, gomokuGame.make_move(move[0], move[1]))
        self.assertEqual(False, gomokuGame.make_move(0, 0))
        self.assertEqual(True, gomokuGame._check_five_in_a_row(5, 5, (0, -1)))
        self.assertEqual('X', gomokuGame.check_winner())
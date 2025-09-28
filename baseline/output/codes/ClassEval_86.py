class TicTacToe:
    """
    The class represents a game of Tic-Tac-Toe and its functions include making a move on the board, checking for a winner, and determining if the board is full.
    """

    def __init__(self, N=3):
        """
        Initialize a 3x3 game board with all empty spaces and current symble player, default is 'X'.
        """
        self.board = [[' ' for _ in range(N)] for _ in range(3)]
        self.current_player = 'X'

    def make_move(self, row, col):
        """
        Place the current player's mark at the specified position on the board and switch the mark.
        :param row: int, the row index of the position
        :param col: int, the column index of the position
        :return: bool, indicating whether the move was successful or not
        >>> ttt.current_player
        'X'
        >>> ttt.make_move(1, 1)
        >>> ttt.current_player
        'O'
        """
        if row < 0 or row >= 3 or col < 0 or col >= 3:
            return False
        if self.board[row][col] != ' ':
            return False
        self.board[row][col] = self.current_player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return True

    def check_winner(self):
        """
        Check if there is a winner on the board in rows, columns and diagonals three directions
        :return: str or None, the mark of the winner ('X' or 'O'), or None if there is no winner yet
        >>> moves = [(1, 0), (2, 0), (1, 1), (2, 1), (1, 2)]
        >>> for move in moves:
        ...     ttt.make_move(move[0], move[1])
        >>> ttt.check_winner()
        'X'
        """
        # Check rows
        for row in range(3):
            if self.board[row][0] == self.board[row][1] == self.board[row][2] != ' ':
                return self.board[row][0]
        # Check columns
        for col in range(3):
            if self.board[0][col] == self.board[1][col] == self.board[2][col] != ' ':
                return self.board[0][col]
        # Check diagonals
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != ' ':
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != ' ':
            return self.board[0][2]
        return None

    def is_board_full(self):
        """
        Check if the game board is completely filled.
        :return: bool, indicating whether the game board is full or not
        >>> ttt.is_board_full()
        False
        """
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == ' ':
                    return False
        return True

import unittest

class TicTacToeTestMakeMove(unittest.TestCase):
    def test_make_move_1(self):
        ttt = TicTacToe()
        self.assertEqual(ttt.current_player, 'X')
        self.assertTrue(ttt.make_move(0, 0))
        self.assertEqual(ttt.current_player, 'O')

    # move invalid
    def test_make_move_2(self):
        ttt = TicTacToe()
        self.assertEqual(ttt.current_player, 'X')
        self.assertTrue(ttt.make_move(0, 0))
        self.assertTrue(ttt.make_move(0, 1))
        self.assertFalse(ttt.make_move(0, 0))
        self.assertEqual(ttt.current_player, 'X')

    def test_make_move_3(self):
        ttt = TicTacToe()
        self.assertEqual(ttt.current_player, 'X')
        self.assertTrue(ttt.make_move(0, 0))
        self.assertTrue(ttt.make_move(0, 1))
        self.assertTrue(ttt.make_move(1, 1))
        self.assertEqual(ttt.current_player, 'O')

    def test_make_move_4(self):
        ttt = TicTacToe()
        self.assertEqual(ttt.current_player, 'X')
        self.assertTrue(ttt.make_move(0, 0))
        self.assertTrue(ttt.make_move(0, 1))
        self.assertTrue(ttt.make_move(1, 1))
        self.assertTrue(ttt.make_move(1, 2))
        self.assertEqual(ttt.current_player, 'X')

    def test_make_move_5(self):
        ttt = TicTacToe()
        self.assertEqual(ttt.current_player, 'X')
        self.assertTrue(ttt.make_move(0, 0))
        self.assertTrue(ttt.make_move(0, 1))
        self.assertTrue(ttt.make_move(1, 1))
        self.assertTrue(ttt.make_move(1, 2))
        self.assertTrue(ttt.make_move(2, 2))
        self.assertEqual(ttt.current_player, 'O')


class TicTacToeTestCheckWinner(unittest.TestCase):
    # rows
    def test_check_winner_1(self):
        ttt = TicTacToe()
        moves = [(1, 0), (2, 0), (1, 1), (2, 1), (1, 2)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertEqual(ttt.check_winner(), 'X')

    # columns
    def test_check_winner_2(self):
        ttt = TicTacToe()
        moves = [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertEqual(ttt.check_winner(), 'X')

    # main diagonals 
    def test_check_winner_3(self):
        ttt = TicTacToe()
        moves = [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertEqual(ttt.check_winner(), 'X')

    # secondary diagonals 
    def test_check_winner_4(self):
        ttt = TicTacToe()
        moves = [(0, 2), (0, 1), (1, 1), (1, 0), (2, 0)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertEqual(ttt.check_winner(), 'X')

    def test_check_winner_5(self):
        ttt = TicTacToe()
        moves = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertEqual(ttt.check_winner(), None)


class TicTacToeTestIsBoardFull(unittest.TestCase):
    # not full
    def test_is_board_full_1(self):
        ttt = TicTacToe()
        self.assertFalse(ttt.is_board_full())

    # full
    def test_is_board_full_2(self):
        ttt = TicTacToe()
        moves = [(1, 1), (0, 2), (2, 2), (0, 0), (0, 1), (2, 1), (1, 0), (1, 2), (2, 0)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertTrue(ttt.is_board_full())

    def test_is_board_full_3(self):
        ttt = TicTacToe()
        moves = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertFalse(ttt.is_board_full())

    def test_is_board_full_4(self):
        ttt = TicTacToe()
        moves = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0), (0, 2), (1, 2), (2, 1), (2, 2)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertTrue(ttt.is_board_full())

    def test_is_board_full_5(self):
        ttt = TicTacToe()
        moves = [(0, 0), (0, 1), (1, 1), (1, 0), (2, 0), (0, 2), (1, 2), (2, 1)]
        for move in moves:
            ttt.make_move(move[0], move[1])
        self.assertFalse(ttt.is_board_full())


class TicTacToeTestMain(unittest.TestCase):
    def test_main(self):
        # A draw down way
        ttt = TicTacToe()
        moves = [(1, 1), (0, 2), (2, 2), (0, 0), (0, 1), (2, 1), (1, 0), (1, 2), (2, 0)]
        for move in moves:
            self.assertTrue(ttt.make_move(move[0], move[1]))
            # no winner in this case
            self.assertFalse(ttt.check_winner())
            if move != (2, 0):
                self.assertFalse(ttt.is_board_full())
        self.assertTrue(ttt.is_board_full())
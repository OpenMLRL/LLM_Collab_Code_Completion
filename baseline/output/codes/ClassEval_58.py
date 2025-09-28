import random

class MinesweeperGame:
    """
    This is a class that implements mine sweeping games including minesweeping and winning judgment.
    """

    def __init__(self, n, k) -> None:
        """
        Initializes the MinesweeperGame class with the size of the board and the number of mines.
        :param n: The size of the board, int.
        :param k: The number of mines, int.
        """
        self.n = n
        self.k = k
        self.minesweeper_map = self.generate_mine_sweeper_map()
        self.player_map = self.generate_playerMap()
        self.score = 0

    def generate_mine_sweeper_map(self):
        """
        Generates a minesweeper map with the given size of the board and the number of mines,the given parameter n is the size of the board,the size of the board is n*n,the parameter k is the number of mines,'X' represents the mine,other numbers represent the number of mines around the position.
        :return: The minesweeper map, list.
        >>> minesweeper_game = MinesweeperGame(3, 1)
        >>> minesweeper_game.generate_mine_sweeper_map()
        [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        """
        board = [['' for _ in range(self.n)] for _ in range(self.n)]
        mines = random.sample(range(self.n * self.n), self.k)
        for idx in mines:
            x, y = divmod(idx, self.n)
            board[x][y] = 'X'
        for x in range(self.n):
            for y in range(self.n):
                if board[x][y] != 'X':
                    count = 0
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.n and 0 <= ny < self.n and board[nx][ny] == 'X':
                                count += 1
                    board[x][y] = count
        return board

    def generate_playerMap(self):
        """
        Generates a player map with the given size of the board, the given parameter n is the size of the board,the size of the board is n*n,the parameter k is the number of mines,'-' represents the unknown position.
        :return: The player map, list.
        >>> minesweeper_game = MinesweeperGame(3, 1)
        >>> minesweeper_game.generate_playerMap()
        [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        """
        return [['-' for _ in range(self.n)] for _ in range(self.n)]

    def check_won(self, map):
        """
        Checks whether the player has won the game,if there are just mines in the player map,return True,otherwise return False.
        :return: True if the player has won the game, False otherwise.
        >>> minesweeper_game = MinesweeperGame(3, 1)
        >>> minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        >>> minesweeper_game.player_map = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        >>> minesweeper_game.check_won(minesweeper_game.player_map)
        False
        """
        for x in range(self.n):
            for y in range(self.n):
                if map[x][y] != 'X' and map[x][y] != '-':
                    return False
        return True

    def sweep(self, x, y):
        """
        Sweeps the given position.
        :param x: The x coordinate of the position, int.
        :param y: The y coordinate of the position, int.
        :return: True if the player has won the game, False otherwise,if the game still continues, return the player map, list.
        >>> minesweeper_game = MinesweeperGame(3, 1)
        >>> minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        >>> minesweeper_game.player_map = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        >>> minesweeper_game.sweep(1, 1)
        [['-', '-', '-'], ['-', 1, '-'], ['-', '-', '-']]
        """
        if self.player_map[x][y] != '-':
            return self.player_map
        self.player_map[x][y] = self.minesweeper_map[x][y]
        if self.minesweeper_map[x][y] == 'X':
            return False
        if self.check_won(self.player_map):
            return True
        return self.player_map

import unittest

class MinesweeperGameTestGenerateMineSweeperMap(unittest.TestCase):
    def test_generate_mine_sweeper_map(self):
        minesweeper_game = MinesweeperGame(3, 2)
        length = len(minesweeper_game.minesweeper_map)
        mine_num = 0
        for row in minesweeper_game.minesweeper_map:
            for cell in row:
                if cell == 'X':
                    mine_num += 1
        self.assertEqual(3, length)
        self.assertEqual(2, mine_num)

    def test_generate_mine_sweeper_map_2(self):
        minesweeper_game = MinesweeperGame(3, 1)
        length = len(minesweeper_game.minesweeper_map)
        mine_num = 0
        for row in minesweeper_game.minesweeper_map:
            for cell in row:
                if cell == 'X':
                    mine_num += 1
        self.assertEqual(3, length)
        self.assertEqual(1, mine_num)

    def test_generate_mine_sweeper_map_3(self):
        minesweeper_game = MinesweeperGame(3, 0)
        length = len(minesweeper_game.minesweeper_map)
        mine_num = 0
        for row in minesweeper_game.minesweeper_map:
            for cell in row:
                if cell == 'X':
                    mine_num += 1
        self.assertEqual(3, length)
        self.assertEqual(0, mine_num)

    def test_generate_mine_sweeper_map_4(self):
        minesweeper_game = MinesweeperGame(5, 1)
        length = len(minesweeper_game.minesweeper_map)
        mine_num = 0
        for row in minesweeper_game.minesweeper_map:
            for cell in row:
                if cell == 'X':
                    mine_num += 1
        self.assertEqual(length,5)
        self.assertEqual(mine_num, 1)

    def test_generate_mine_sweeper_map_5(self):
        minesweeper_game = MinesweeperGame(4, 1)
        length = len(minesweeper_game.minesweeper_map)
        mine_num = 0
        for row in minesweeper_game.minesweeper_map:
            for cell in row:
                if cell == 'X':
                    mine_num += 1
        self.assertEqual(length, 4)
        self.assertEqual(mine_num, 1)

class MinesweeperGameTestGeneratePlayerMap(unittest.TestCase):
    def test_generate_playerMap(self):
        minesweeper_game = MinesweeperGame(3, 2)
        self.assertEqual(minesweeper_game.generate_playerMap(), [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']])

    def test_generate_playerMap_2(self):
        minesweeper_game = MinesweeperGame(3, 1)
        self.assertEqual(minesweeper_game.generate_playerMap(), [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']])

    def test_generate_playerMap_3(self):
        minesweeper_game = MinesweeperGame(4, 2)
        self.assertEqual(minesweeper_game.generate_playerMap(),[['-', '-', '-', '-'],['-', '-', '-', '-'],['-', '-', '-', '-'],['-', '-', '-', '-']])

    def test_generate_playerMap_4(self):
        minesweeper_game = MinesweeperGame(1, 4)
        self.assertEqual(minesweeper_game.generate_playerMap(), [['-']])

    def test_generate_playerMap_5(self):
        minesweeper_game = MinesweeperGame(2, 5)
        self.assertEqual(minesweeper_game.generate_playerMap(), [['-', '-'], ['-', '-']])

class MinesweeperGameTestCheckWon(unittest.TestCase):
    def test_check_won(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        self.assertEqual(minesweeper_game.check_won(minesweeper_game.player_map), False)

    def test_check_won_2(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '-'], ['-', 1, '-'], ['-', '-', '-']]
        self.assertEqual(minesweeper_game.check_won(minesweeper_game.player_map), False)

    def test_check_won_3(self):
        minesweeper_game = MinesweeperGame(3, 0)
        minesweeper_game.minesweeper_map = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '-'], ['-', 1, '-'], ['-', '-', '-']]
        self.assertEqual(minesweeper_game.check_won(minesweeper_game.player_map), False)

    def test_check_won_4(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '1', '0'], ['1', 1, '0'], ['0', '0', '0']]
        self.assertEqual(minesweeper_game.check_won(minesweeper_game.player_map), True)

    def test_check_won_5(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['X', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        self.assertEqual(minesweeper_game.check_won(minesweeper_game.player_map), False)

class MinesweeperGameTestSweep(unittest.TestCase):
    def test_sweep(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        self.assertEqual(minesweeper_game.sweep(1,1), [['-', '-', '-'], ['-', 1, '-'], ['-', '-', '-']])
        self.assertEqual(minesweeper_game.score, 1)

    def test_sweep_2(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        self.assertEqual(minesweeper_game.sweep(0,0), False)
        self.assertEqual(minesweeper_game.score, 0)

    def test_sweep_3(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '0'], ['1', '1', '0'], ['0', '0', '0']]
        self.assertEqual(minesweeper_game.sweep(0,1), True)
        self.assertEqual(minesweeper_game.score, 1)

    def test_sweep_4(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '-'], ['-', '-', '0'], ['0', '0', '0']]
        self.assertEqual(minesweeper_game.sweep(0,2), [['-', '-', 0], ['-', '-', '0'], ['0', '0', '0']])
        self.assertEqual(minesweeper_game.score, 1)

    def test_sweep_5(self):
        minesweeper_game = MinesweeperGame(3, 1)
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '0'], ['-', '1', '0'], ['0', '0', '0']]
        self.assertEqual(minesweeper_game.sweep(1,0), [['-', '-', '0'], [1, '1', '0'], ['0', '0', '0']])
        self.assertEqual(minesweeper_game.score, 1)

class MinesweeperGameTestMain(unittest.TestCase):
    def test_minesweeper_main(self):
        minesweeper_game = MinesweeperGame(3, 1)
        length = len(minesweeper_game.minesweeper_map)
        mine_num = 0
        for row in minesweeper_game.minesweeper_map:
            for cell in row:
                if cell == 'X':
                    mine_num += 1
        self.assertEqual(3, length)
        self.assertEqual(1, mine_num)
        self.assertEqual(minesweeper_game.generate_playerMap(), [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']])
        minesweeper_game.minesweeper_map = [['X', 1, 0], [1, 1, 0], [0, 0, 0]]
        minesweeper_game.player_map = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]
        self.assertEqual(minesweeper_game.check_won(minesweeper_game.player_map), False)
        self.assertEqual(minesweeper_game.sweep(1,1), [['-', '-', '-'], ['-', 1, '-'], ['-', '-', '-']])
        self.assertEqual(minesweeper_game.score, 1)

    def test_minesweeper_main_2(self):
        minesweeper_game = MinesweeperGame(3, 2)
        length = len(minesweeper_game.minesweeper_map)
        mine_num = 0
        for row in minesweeper_game.minesweeper_map:
            for cell in row:
                if cell == 'X':
                    mine_num += 1
        self.assertEqual(3, length)
        self.assertEqual(2, mine_num)
        self.assertEqual(minesweeper_game.generate_playerMap(), [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']])
        minesweeper_game.minesweeper_map = [['X', 1, 1], [1, 'X', 1], [1, 1, 1]]
        self.assertEqual(minesweeper_game.check_won(minesweeper_game.player_map), False)
        self.assertEqual(minesweeper_game.sweep(0, 1), [['-', 1, '-'], ['-','-', '-'], ['-', '-', '-']])
        self.assertEqual(minesweeper_game.score, 1)
        self.assertEqual(minesweeper_game.sweep(0, 2), [['-', 1, 1], ['-', '-', '-'], ['-', '-', '-']])
        self.assertEqual(minesweeper_game.score, 2)
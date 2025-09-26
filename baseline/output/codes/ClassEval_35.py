class EightPuzzle:
    """
    This class is an implementation of the classic 8-puzzle game, including methods for finding the blank tile, making moves, getting possible moves, and solving the puzzle using a breadth-first search algorithm.
    """

    def __init__(self, initial_state):
        """
        Initializing the initial state of Eight Puzzle Game, stores in attribute self.initial_state.
        And set the goal state of this game, stores in self.goal_state. In this case, set the size as 3*3
        :param initial_state: a 3*3 size list of Integer, stores the initial state
        """
        self.initial_state = initial_state
        self.goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    def find_blank(self, state):
        """
        Find the blank position of current state, which is the 0 element.
        :param state: a 3*3 size list of Integer, stores the current state.
        :return i, j: two Integers, represent the coordinate of the blank block.
        >>> eightPuzzle = EightPuzzle([[2, 3, 4], [5, 8, 1], [6, 0, 7]])
        >>> eightPuzzle.find_blank([[2, 3, 4], [5, 8, 1], [6, 0, 7]])
        (2, 1)
        """
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return i, j

    def move(self, state, direction):
        """
        Find the blank block, then makes the board moves forward the given direction.
        :param state: a 3*3 size list of Integer, stores the state before moving.
        :param direction: str, only has 4 direction 'up', 'down', 'left', 'right'
        :return new_state: a 3*3 size list of Integer, stores the state after moving.
        >>> eightPuzzle.move([[2, 3, 4], [5, 8, 1], [6, 0, 7]], 'left')
        [[2, 3, 4], [5, 8, 1], [0, 6, 7]]
        """
        i, j = self.find_blank(state)
        if direction == 'up':
            new_state = [[0] * 3 for _ in range(3)]
            for k in range(3):
                for l in range(3):
                    new_state[k][l] = state[k][l]
            new_state[i][j], new_state[i-1][j] = new_state[i-1][j], new_state[i][j]
            return new_state
        elif direction == 'down':
            new_state = [[0] * 3 for _ in range(3)]
            for k in range(3):
                for l in range(3):
                    new_state[k][l] = state[k][l]
            new_state[i][j], new_state[i+1][j] = new_state[i+1][j], new_state[i][j]
            return new_state
        elif direction == 'left':
            new_state = [[0] * 3 for _ in range(3)]
            for k in range(3):
                for l in range(3):
                    new_state[k][l] = state[k][l]
            new_state[i][j], new_state[i][j-1] = new_state[i][j-1], new_state[i][j]
            return new_state
        elif direction == 'right':
            new_state = [[0] * 3 for _ in range(3)]
            for k in range(3):
                for l in range(3):
                    new_state[k][l] = state[k][l]
            new_state[i][j], new_state[i][j+1] = new_state[i][j+1], new_state[i][j]
            return new_state

    def get_possible_moves(self, state):
        """
        According the current state, find all the possible moving directions. Only has 4 direction 'up', 'down', 'left', 'right'.
        :param state: a 3*3 size list of Integer, stores the current state.
        :return moves: a list of str, store all the possible moving directions according to the current state.
        >>> eightPuzzle.get_possible_moves([[2, 3, 4], [5, 8, 1], [6, 0, 7]])
        ['up', 'left', 'right']
        """
        moves = []
        i, j = self.find_blank(state)
        if i > 0:
            moves.append('up')
        if i < 2:
            moves.append('down')
        if j > 0:
            moves.append('left')
        if j < 2:
            moves.append('right')
        return moves

    def solve(self):
        """
        Use BFS algorithm to find the path solution which makes the initial state to the goal method.
        Maintain a list as a queue, named as open_list, append the initial state.
        Always visit and pop the 0 index element, invoke get_possible_moves method find all the possible directions.
        Traversal the possible_moves list and invoke move method to get several new states.Then append them.
        redo the above steps until the open_list is empty or the state has changed to the goal state.
        :return path: list of str, the solution to the goal state.
        >>> eightPuzzle = EightPuzzle([[1, 2, 3], [4, 5, 6], [7, 0, 8]])
        >>> eightPuzzle.solve()
        ['right']
        """
        open_list = [self.initial_state]
        while open_list:
            current_state = open_list.pop(0)
            if current_state == self.goal_state:
                path = []
                while current_state != self.initial_state:
                    current_state, move = self.move(current_state, path[-1])
                    path.append(move)
                path.reverse()
                return path
            for move in self.get_possible_moves(current_state):
                new_state = self.move(current_state, move)
                if new_state not in open_list:
                    open_list.append(new_state)
        return []

import unittest

class EightPuzzleTestFindBlank(unittest.TestCase):
    def test_find_blank_1(self):
        state = [[2, 3, 4], [5, 8, 1], [6, 0, 7]]
        eightPuzzle = EightPuzzle(state)
        self.assertEqual(eightPuzzle.find_blank(state), (2, 1))

    def test_find_blank_2(self):
        state = [[2, 3, 4], [5, 0, 1], [6, 8, 7]]
        eightPuzzle = EightPuzzle(state)
        self.assertEqual(eightPuzzle.find_blank(state), (1, 1))

    def test_find_blank_3(self):
        state = [[2, 3, 4], [5, 8, 1], [6, 8, 7]]
        eightPuzzle = EightPuzzle(state)
        self.assertEqual(eightPuzzle.find_blank(state), None)

    def test_find_blank_4(self):
        state = [[2, 3, 4], [5, 8, 1], [6, 8, 7]]
        eightPuzzle = EightPuzzle(state)
        self.assertEqual(eightPuzzle.find_blank(state), None)

    def test_find_blank_5(self):
        state = [[2, 3, 4], [5, 8, 1], [6, 8, 7]]
        eightPuzzle = EightPuzzle(state)
        self.assertEqual(eightPuzzle.find_blank(state), None)


class EightPuzzleTestMove(unittest.TestCase):
    def setUp(self):
        self.initial_state = [[2, 3, 4], [5, 0, 1], [6, 8, 7]]
        self.eightPuzzle = EightPuzzle(self.initial_state)

    def test_move_1(self):
        result = self.eightPuzzle.move(self.initial_state, 'up')
        expected = [[2, 0, 4], [5, 3, 1], [6, 8, 7]]
        self.assertEqual(result, expected)

    def test_move_2(self):
        result = self.eightPuzzle.move(self.initial_state, 'down')
        expected = [[2, 3, 4], [5, 8, 1], [6, 0, 7]]
        self.assertEqual(result, expected)

    def test_move_3(self):
        result = self.eightPuzzle.move(self.initial_state, 'left')
        expected = [[2, 3, 4], [0, 5, 1], [6, 8, 7]]
        self.assertEqual(result, expected)

    def test_move_4(self):
        result = self.eightPuzzle.move(self.initial_state, 'right')
        expected = [[2, 3, 4], [5, 1, 0], [6, 8, 7]]
        self.assertEqual(result, expected)

    def test_move_5(self):
        result = self.eightPuzzle.move(self.initial_state, '???')
        expected = [[2, 3, 4], [5, 0, 1], [6, 8, 7]]
        self.assertEqual(result, expected)


class EightPuzzleTestGetPossibleMoves(unittest.TestCase):
    def test_get_possible_moves_1(self):
        eightPuzzle = EightPuzzle(None)
        state = [[2, 3, 4], [5, 0, 1], [6, 8, 7]]
        result = eightPuzzle.get_possible_moves(state)
        expected = ['up', 'down', 'left', 'right']
        for direction in result:
            self.assertIn(direction, expected)

    def test_get_possible_moves_2(self):
        eightPuzzle = EightPuzzle(None)
        state = [[2, 3, 4], [5, 8, 1], [6, 0, 7]]
        result = eightPuzzle.get_possible_moves(state)
        expected = ['up', 'left', 'right']
        for direction in result:
            self.assertIn(direction, expected)

    def test_get_possible_moves_3(self):
        eightPuzzle = EightPuzzle(None)
        state = [[2, 0, 4], [5, 3, 1], [6, 8, 7]]
        result = eightPuzzle.get_possible_moves(state)
        expected = ['down', 'left', 'right']
        for direction in result:
            self.assertIn(direction, expected)

    def test_get_possible_moves_4(self):
        eightPuzzle = EightPuzzle(None)
        state = [[2, 3, 4], [5, 1, 0], [6, 8, 7]]
        result = eightPuzzle.get_possible_moves(state)
        expected = ['up', 'down', 'left']
        for direction in result:
            self.assertIn(direction, expected)

    def test_get_possible_moves_5(self):
        eightPuzzle = EightPuzzle(None)
        state = [[2, 3, 4], [0, 5, 1], [6, 8, 7]]
        result = eightPuzzle.get_possible_moves(state)
        expected = ['up', 'down', 'right']
        for direction in result:
            self.assertIn(direction, expected)


class EightPuzzleTestSolve(unittest.TestCase):
    def test_solve_1(self):
        eightPuzzle = EightPuzzle([[1, 2, 3], [4, 5, 6], [7, 0, 8]])
        result = eightPuzzle.solve()
        expected = ['right']
        self.assertEqual(result, expected)

    def test_solve_2(self):
        eightPuzzle = EightPuzzle([[1, 2, 3], [4, 0, 6], [7, 5, 8]])
        result = eightPuzzle.solve()
        expected = ['down', 'right']
        self.assertEqual(result, expected)

    def test_solve_3(self):
        eightPuzzle = EightPuzzle([[1, 2, 3], [0, 4, 5], [6, 7, 8]])
        result = eightPuzzle.solve()
        expected = ['right', 'right', 'down', 'left', 'left', 'up', 'right', 'down', 'right', 'up', 'left', 'left', 'down', 'right', 'right']
        self.assertEqual(result, expected)

    def test_solve_4(self):
        eightPuzzle = EightPuzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        result = eightPuzzle.solve()
        expected = []
        self.assertEqual(result, expected)

    def test_solve_5(self):
        eightPuzzle = EightPuzzle([[1, 2, 3], [4, 5, 6], [0, 7, 8]])
        result = eightPuzzle.solve()
        expected = ['right', 'right']
        self.assertEqual(result, expected)

    def test_solve_6(self):
        eightPuzzle = EightPuzzle([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        result = eightPuzzle.solve()
        expected = None
        self.assertEqual(result, expected)
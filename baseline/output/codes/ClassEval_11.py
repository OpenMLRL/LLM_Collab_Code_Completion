class BitStatusUtil:
    """
    This is a utility class that provides methods for manipulating and checking status using bitwise operations.
    """

    @staticmethod
    def add(states, stat):
        """
        Add a status to the current status,and check the parameters wheather they are legal.
        :param states: Current status,int.
        :param stat: Status to be added,int.
        :return: The status after adding the status,int.
        >>> bit_status_util = BitStatusUtil()
        >>> bit_status_util.add(2,4)
        6

        """
        BitStatusUtil.check([states, stat])
        return states | stat

    @staticmethod
    def has(states, stat):
        """
        Check if the current status contains the specified status,and check the parameters wheather they are legal.
        :param states: Current status,int.
        :param stat: Specified status,int.
        :return: True if the current status contains the specified status,otherwise False,bool.
        >>> bit_status_util = BitStatusUtil()
        >>> bit_status_util.has(6,2)
        True

        """
        BitStatusUtil.check([states, stat])
        return (states & stat) != 0

    @staticmethod
    def remove(states, stat):
        """
        Remove the specified status from the current status,and check the parameters wheather they are legal.
        :param states: Current status,int.
        :param stat: Specified status,int.
        :return: The status after removing the specified status,int.
        >>> bit_status_util = BitStatusUtil()
        >>> bit_status_util.remove(6,2)
        4

        """
        BitStatusUtil.check([states, stat])
        return states & ~stat

    @staticmethod
    def check(args):
        """
        Check if the parameters are legal, args must be greater than or equal to 0 and must be even,if not,raise ValueError.
        :param args: Parameters to be checked,list.
        :return: None.
        >>> bit_status_util = BitStatusUtil()
        >>> bit_status_util.check([2,3,4])
        Traceback (most recent call last):
        ...
        ValueError: 3 not even
        """
        for arg in args:
            if arg < 0:
                raise ValueError(f"{arg} is negative")
            if arg % 2 != 0:
                raise ValueError(f"{arg} not even")

import unittest


class BitStatusUtilTestAdd(unittest.TestCase):
    def test_add(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.add(2, 4), 6)

    def test_add_2(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.add(2, 0), 2)

    def test_add_3(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.add(0, 0), 0)

    def test_add_4(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.add(0, 2), 2)

    def test_add_5(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.add(2, 2), 2)


class BitStatusUtilTestHas(unittest.TestCase):
    def test_has(self):
        bit_status_util = BitStatusUtil()
        self.assertTrue(bit_status_util.has(6, 2))

    def test_has_2(self):
        bit_status_util = BitStatusUtil()
        self.assertFalse(bit_status_util.has(8, 2))

    def test_has_3(self):
        bit_status_util = BitStatusUtil()
        self.assertTrue(bit_status_util.has(6, 4))

    def test_has_4(self):
        bit_status_util = BitStatusUtil()
        self.assertFalse(bit_status_util.has(8, 6))

    def test_has_5(self):
        bit_status_util = BitStatusUtil()
        self.assertTrue(bit_status_util.has(6, 6))


class BitStatusUtilTestRemove(unittest.TestCase):
    def test_remove(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.remove(6, 2), 4)

    def test_remove_2(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.remove(8, 2), 8)

    def test_remove_3(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.remove(6, 4), 2)

    def test_remove_4(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.remove(8, 6), 8)

    def test_remove_5(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.remove(6, 6), 0)


class BitStatusUtilTestCheck(unittest.TestCase):
    def test_check(self):
        bit_status_util = BitStatusUtil()
        bit_status_util.check([2])

    def test_check_2(self):
        bit_status_util = BitStatusUtil()
        with self.assertRaises(ValueError):
            bit_status_util.check([3])

    def test_check_3(self):
        bit_status_util = BitStatusUtil()
        with self.assertRaises(ValueError):
            bit_status_util.check([-1])

    def test_check_4(self):
        bit_status_util = BitStatusUtil()
        with self.assertRaises(ValueError):
            bit_status_util.check([2, 3, 4])

    def test_check_5(self):
        bit_status_util = BitStatusUtil()
        with self.assertRaises(ValueError):
            bit_status_util.check([2, 3, 4, 5])


class BitStatusUtilTestMain(unittest.TestCase):
    def test_main(self):
        bit_status_util = BitStatusUtil()
        self.assertEqual(bit_status_util.add(2, 4), 6)
        self.assertTrue(bit_status_util.has(6, 2))
        self.assertEqual(bit_status_util.remove(6, 2), 4)
        with self.assertRaises(ValueError):
            bit_status_util.check([2, 3, 4])
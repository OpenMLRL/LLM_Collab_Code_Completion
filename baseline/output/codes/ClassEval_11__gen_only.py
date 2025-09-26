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
        if not isinstance(states, int) or not isinstance(stat, int):
            raise TypeError("Both states and stat must be integers.")
        if stat < 0:
            raise ValueError("Stat must be non-negative.")
        if stat % 2 != 0:
            raise ValueError("Stat must be even.")
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
        if not isinstance(states, int) or not isinstance(stat, int):
            raise TypeError("Both states and stat must be integers.")
        if stat < 0:
            raise ValueError("Stat must be non-negative.")
        if stat % 2 != 0:
            raise ValueError("Stat must be even.")
        return bool(states & stat)

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
        if not isinstance(states, int) or not isinstance(stat, int):
            raise TypeError("Both states and stat must be integers.")
        if stat < 0:
            raise ValueError("Stat must be non-negative.")
        if stat % 2 != 0:
            raise ValueError("Stat must be even.")
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
        if not all(isinstance(arg, int) for arg in args):
            raise TypeError("All elements in args must be integers.")
        if any(arg < 0 for arg in args):
            raise ValueError("All elements in args must be non-negative.")
        if any(arg % 2 != 0 for arg in args):
            raise ValueError("All elements in args must be even.")
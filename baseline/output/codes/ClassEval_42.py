class Hotel:
    """
    This is a class as hotel management system, managing the booking, check-in, check-out, and availability of rooms in a hotel with different room types.
    """

    def __init__(self, name, rooms):
        """
        Initialize the three fields in Hotel System.
        name is the hotel name.
        available_rooms stores the remaining rooms in the hotel
        booked_rooms stores the rooms that have been booked and the person's name who booked rooms.
        >>> hotel.name
        'peace hotel'
        >>> hotel.available_rooms
        available_rooms = {'single': 5, 'double': 3}
        >>> hotel.booked_rooms
        {'single': {'guest 1': 2, 'guest 2':1}, 'double': {'guest1': 1}}
        """
        self.name = name
        self.available_rooms = rooms
        self.booked_rooms = {}

    def book_room(self, room_type, room_number, name):
        """
        Check if there are any rooms of the specified type available.
        if rooms are adequate, modify available_rooms and booked_rooms and finish booking, or fail to book otherwise.
        :param room_type: str
        :param room_number: int, the expected number of specified type rooms to be booked
        :param name: str, guest name
        :return: if number of rooms about to be booked doesn't exceed the remaining rooms, return str 'Success!'
                if exceeds but quantity of available rooms is not equal to zero, return int(the remaining quantity of this room type).
                if exceeds and quantity is zero or the room_type isn't in available_room, return False.
        >>> hotel = Hotel('peace hotel', {'single': 5, 'double': 3})
        >>> hotel.book_room('single', 1, 'guest 1')
        'Success!'
        >>> hotel.book_room('single', 5, 'guest 1')
        4
        >>> hotel.book_room('single', 4, 'guest 1')
        'Success!'
        >>> hotel.book_room('single', 1, 'guest 1')
        False
        >>> hotel.book_room('triple', 1, 'guest 1')
        False
        """
        if room_type not in self.available_rooms:
            return False
        available = self.available_rooms[room_type]
        if room_number <= available:
            self.available_rooms[room_type] -= room_number
            if room_type not in self.booked_rooms:
                self.booked_rooms[room_type] = {}
            self.booked_rooms[room_type][name] = room_number
            return 'Success!'
        else:
            remaining = available - room_number
            if available > 0:
                return remaining
            else:
                return False

    def check_in(self, room_type, room_number, name):
        """
        Check if the room of the specified type and number is booked by the person named name.
        Remove this name when check in successfully (room_number is equal to specific person's booked_rooms. When the actual check in quantity (room_number) is less than the booked quantity, number in booked_rooms will be booked quantity minus actual quantity
        :param room_type: str, check in room type
        :param room_number: int, check in room number
        :param name: str, person name
        :return False: only if the room_type is not in the booked_rooms or room_number is higher than quantity in booked rooms.
        >>> hotel = Hotel('peace hotel', {'single': 5, 'double': 3})
        >>> hotel.book_room('single', 1, 'guest 1')
        'Success!'
        >>> hotel.check_in('single', 2, 'guest 1')
        False
        >>> hotel.check_in('single', 1, 'guest 1')
        >>> hotel.booked_rooms
        {'single': {}}
        """
        if room_type not in self.booked_rooms or name not in self.booked_rooms[room_type]:
            return False
        booked_quantity = self.booked_rooms[room_type][name]
        if room_number > booked_quantity:
            return False
        self.booked_rooms[room_type][name] -= room_number
        if self.booked_rooms[room_type][name] == 0:
            del self.booked_rooms[room_type][name]
        self.available_rooms[room_type] += room_number
        return True

    def check_out(self, room_type, room_number):
        """
        Check out rooms, add number for specific type in available_rooms.
        If room_type is new, add new type in available_rooms.
        :param room_type: str, check out room type
        :param room_number: int, check out room number
        >>> hotel = Hotel('peace hotel', {'single': 5, 'double': 3})
        >>> hotel.check_out('single', 2)
        >>> hotel.available_rooms
        {'single': 7, 'double': 3}
        >>> hotel.check_out('triple', 2)
        >>> hotel.available_rooms
        {'single': 7, 'double': 3, 'triple': 2}
        """
        if room_type not in self.available_rooms:
            self.available_rooms[room_type] = 0
        self.available_rooms[room_type] += room_number

    def get_available_rooms(self, room_type):
        """
        Get the number of specific type of available rooms.
        :param room_type: str, the room type that want to know
        :return: int, the remaining number of this type rooms.
        >>> hotel = Hotel('peace hotel', {'single': 5, 'double': 3})
        >>> hotel.get_available_rooms('single')
        5
        """
        return self.available_rooms.get(room_type, 0)

import unittest


class HotelTestBookRoom(unittest.TestCase):
    def setUp(self):
        self.hotel = Hotel('peace hotel', {'single': 3, 'double': 2})

    def test_book_room_1(self):
        result = self.hotel.book_room('single', 2, 'guest 1')
        self.assertEqual(result, 'Success!')
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}})
        self.assertEqual(self.hotel.available_rooms, {'single': 1, 'double': 2})

    def test_book_room_2(self):
        result = self.hotel.book_room('triple', 2, 'guest 1')
        self.assertFalse(result)
        self.assertEqual(self.hotel.booked_rooms, {})
        self.assertEqual(self.hotel.available_rooms, {'single': 3, 'double': 2})

    def test_book_room_3(self):
        self.hotel.book_room('single', 2, 'guest 1')
        result = self.hotel.book_room('single', 2, 'guest 2')
        self.assertEqual(result, 1)
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}})
        self.assertEqual(self.hotel.available_rooms, {'single': 1, 'double': 2})

    def test_book_room_4(self):
        self.hotel.book_room('single', 2, 'guest 1')
        result = self.hotel.book_room('single', 1, 'guest 2')
        self.assertEqual(result, 'Success!')
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2, 'guest 2': 1}})
        self.assertEqual(self.hotel.available_rooms, {'double': 2, 'single': 0})

    def test_book_room_5(self):
        self.hotel.book_room('single', 2, 'guest 1')
        result = self.hotel.book_room('single', 3, 'guest 2')
        self.assertEqual(result, 1)
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}})
        self.assertEqual(self.hotel.available_rooms, {'single': 1, 'double': 2})

    def test_book_room_6(self):
        self.hotel.book_room('single', 3, 'guest 1')
        result = self.hotel.book_room('single', 100, 'guest 1')
        self.assertFalse(result)


class HotelTestCheckIn(unittest.TestCase):
    def setUp(self):
        self.hotel = Hotel('Test Hotel', {'single': 3, 'double': 2})
        self.hotel.booked_rooms = {'single': {'guest 1': 2}, 'double': {'guest 2': 1}}

    def test_check_in_1(self):
        self.hotel.check_in('single', 1, 'guest 1')
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 1}, 'double': {'guest 2': 1}})

    def test_check_in_2(self):
        self.assertFalse(self.hotel.check_in('single', 3, 'guest 1'))
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}, 'double': {'guest 2': 1}})

    def test_check_in_3(self):
        self.assertFalse(self.hotel.check_in('double', 1, 'guest 1'))
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}, 'double': {'guest 2': 1}})

    def test_check_in_4(self):
        self.hotel.check_in('double', 1, 'guest 2')
        self.assertEqual(self.hotel.booked_rooms, {'double': {}, 'single': {'guest 1': 2}})

    def test_check_in_5(self):
        self.hotel.check_in('double', 2, 'guest 2')
        self.assertEqual(self.hotel.booked_rooms, {'double': {'guest 2': 1}, 'single': {'guest 1': 2}})

    def test_check_in_6(self):
        res = self.hotel.check_in('abc', 1, 'guest 1')
        self.assertFalse(res)


class HotelTestCheckOut(unittest.TestCase):
    def setUp(self):
        self.hotel = Hotel('Test Hotel', {'single': 3, 'double': 2})
        self.hotel.booked_rooms = {'single': {'guest 1': 2}, 'double': {'guest 2': 1}}

    def test_check_out_1(self):
        self.hotel.check_out('single', 1)
        self.assertEqual(self.hotel.available_rooms, {'single': 4, 'double': 2})
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}, 'double': {'guest 2': 1}})

    def test_check_out_2(self):
        self.hotel.check_out('single', 3)
        self.assertEqual(self.hotel.available_rooms, {'single': 6, 'double': 2})
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}, 'double': {'guest 2': 1}})

    def test_check_out_3(self):
        self.hotel.check_out('triple', 2)
        self.assertEqual(self.hotel.available_rooms, {'single': 3, 'double': 2, 'triple': 2})
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}, 'double': {'guest 2': 1}})

    def test_check_out_4(self):
        self.hotel.check_out('double', 1)
        self.assertEqual(self.hotel.available_rooms, {'single': 3, 'double': 3})
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}, 'double': {'guest 2': 1}})

    def test_check_out_5(self):
        self.hotel.check_out('double', 2)
        self.assertEqual(self.hotel.available_rooms, {'single': 3, 'double': 4})
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}, 'double': {'guest 2': 1}})


class HotelTestAvailableRooms(unittest.TestCase):
    def setUp(self):
        self.hotel = Hotel('Test Hotel', {'single': 3, 'double': 2, 'triple': 2})

    def test_get_available_rooms(self):
        result = self.hotel.get_available_rooms('single')
        self.assertEqual(result, 3)

    def test_get_available_rooms_2(self):
        self.hotel.book_room('single', 2, 'guest 1')
        result = self.hotel.get_available_rooms('single')
        self.assertEqual(result, 1)

    def test_get_available_rooms_3(self):
        self.hotel.book_room('single', 3, 'guest 1')
        result = self.hotel.get_available_rooms('single')
        self.assertEqual(result, 0)

    def test_get_available_rooms_4(self):
        self.hotel.book_room('single', 3, 'guest 1')
        result = self.hotel.get_available_rooms('double')
        self.assertEqual(result, 2)

    def test_get_available_rooms_5(self):
        self.hotel.book_room('single', 3, 'guest 1')
        result = self.hotel.get_available_rooms('triple')
        self.assertEqual(result, 2)


class HotelTestMain(unittest.TestCase):
    def setUp(self) -> None:
        self.hotel = Hotel('Test Hotel', {'single': 3, 'double': 2})

    def test_main(self):
        result = self.hotel.book_room('single', 2, 'guest 1')
        self.assertEqual(result, 'Success!')
        self.assertEqual(self.hotel.booked_rooms, {'single': {'guest 1': 2}})
        self.assertEqual(self.hotel.available_rooms, {'single': 1, 'double': 2})

        self.hotel.check_in('single', 2, 'guest 1')
        self.assertEqual(self.hotel.booked_rooms, {'single': {}})
        self.assertEqual(self.hotel.available_rooms, {'single': 1, 'double': 2})

        self.hotel.check_out('single', 2)
        self.assertEqual(self.hotel.available_rooms, {'single': 3, 'double': 2})

        self.assertEqual(self.hotel.get_available_rooms('single'), 3)
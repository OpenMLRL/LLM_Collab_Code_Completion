from datetime import datetime
import numpy as np

class MovieBookingSystem:
    """
    this is a class as movie booking system, which allows to add movies, book tickets and check the available movies within a given time range. 
    """

    def __init__(self):
        """
        Initialize movies contains the information about movies
        >>> system.movies
        [{'name': 'Batman', 'price': 49.9, 'start_time': datetime.datetime(1900, 1, 1, 17, 5), 'end_time': datetime.datetime(1900, 1, 1, 19, 25),
        'seats': array([[0., 0., 0.],
            [0., 0., 0.],
            [0., 0., 0.]])}]
        """
        self.movies = []

    def add_movie(self, name, price, start_time, end_time, n):
        """
        Add a new movie into self.movies
        :param name: str, movie name
        :param price: float, price for one ticket
        :param start_time: str
        :param end_time: str
        :param n: int, the size of seats(n*n)
        >>> system.add_movie('Batman', 49.9, '17:05', '19:25', 3)
        >>> system.movies
        [{'name': 'Batman', 'price': 49.9, 'start_time': datetime.datetime(1900, 1, 1, 17, 5), 'end_time': datetime.datetime(1900, 1, 1, 19, 25),
        'seats': array([[0., 0., 0.],
            [0., 0., 0.],
            [0., 0., 0.]])}]
        """
        start_time_dt = datetime.strptime(start_time, "%H:%M")
        end_time_dt = datetime.strptime(end_time, "%H:%M")
        seats = np.zeros((n, n))
        self.movies.append({
            'name': name,
            'price': price,
            'start_time': start_time_dt,
            'end_time': end_time_dt,
            'seats': seats
        })

    def book_ticket(self, name, seats_to_book):
        """
        Book tickets for a movie. Change the seats value in self.movies if book successfully.
        :param name: str, movie name
        :param seats_to_book: list of tuples, representing seats to book [(row1, col1), (row2, col2), ...]
        :return: str, booking status message. "Movie not found." for no such movie.
                "Booking success." for successfully booking, or "Booking failed." otherwise
        >>> system.add_movie('Batman', 49.9, '17:05', '19:25', 3)
        >>> system.book_ticket('Batman', [(0, 0), (0, 1)])
        'Booking success.'
        >>> system.book_ticket('Batman', [(0, 0)])
        'Booking failed.'
        >>> system.book_ticket('batman', [(0, 0)])
        'Movie not found.'
        """
        for movie in self.movies:
            if movie['name'] == name:
                # Check if all seats are available
                for row, col in seats_to_book:
                    if row < 0 or row >= movie['seats'].shape[0] or col < 0 or col >= movie['seats'].shape[1]:
                        return "Booking failed."
                    if movie['seats'][row, col] != 0:
                        return "Booking failed."
                # Book the seats
                for row, col in seats_to_book:
                    movie['seats'][row, col] = 1
                return "Booking success."
        return "Movie not found."

    def available_movies(self, start_time, end_time):
        """
        Get a list of available movies within the specified time range
        :param start_time: str, start time in HH:MM format
        :param end_time: str, end time in HH:MM format
        :return: list of str, names of available movies
        >>> system.add_movie('Batman', 49.9, '17:05', '19:25', 3)
        >>> system.available_movies('12:00', '22:00')
        ['Batman']
        """
        start_time_dt = datetime.strptime(start_time, "%H:%M")
        end_time_dt = datetime.strptime(end_time, "%H:%M")
        available = []
        for movie in self.movies:
            if movie['start_time'] >= start_time_dt and movie['end_time'] <= end_time_dt:
                available.append(movie['name'])
        return available

import unittest


class MovieBookingSystemTestAddMovie(unittest.TestCase):
    def setUp(self):
        self.system = MovieBookingSystem()

    def tearDown(self):
        self.system = None

    def test_add_movie_1(self):
        self.system.add_movie('Batman', 49.9, '17:05', '19:25', 3)
        self.assertEqual(len(self.system.movies), 1)
        self.assertEqual(self.system.movies[0]['name'], 'Batman')
        self.assertEqual(self.system.movies[0]['price'], 49.9)
        self.assertEqual(self.system.movies[0]['start_time'], datetime.strptime('17:05', '%H:%M'))
        self.assertEqual(self.system.movies[0]['end_time'], datetime.strptime('19:25', '%H:%M'))
        self.assertEqual(self.system.movies[0]['seats'].shape, (3, 3))

    def test_add_movie_2(self):
        self.system.add_movie('Batman', 49.9, '17:05', '19:25', 3)
        self.system.add_movie('Superman', 49.9, '17:05', '19:25', 3)
        self.assertEqual(len(self.system.movies), 2)
        self.assertEqual(self.system.movies[0]['name'], 'Batman')
        self.assertEqual(self.system.movies[1]['name'], 'Superman')

    def test_add_movie_3(self):
        self.system.add_movie('Batman', 39.9, '17:05', '19:25', 3)
        self.assertEqual(len(self.system.movies), 1)
        self.assertEqual(self.system.movies[0]['name'], 'Batman')
        self.assertEqual(self.system.movies[0]['price'], 39.9)
        self.assertEqual(self.system.movies[0]['start_time'], datetime.strptime('17:05', '%H:%M'))
        self.assertEqual(self.system.movies[0]['end_time'], datetime.strptime('19:25', '%H:%M'))
        self.assertEqual(self.system.movies[0]['seats'].shape, (3, 3))

    def test_add_movie_4(self):
        self.system.add_movie('Batman', 29.9, '17:05', '19:25', 3)
        self.assertEqual(len(self.system.movies), 1)
        self.assertEqual(self.system.movies[0]['name'], 'Batman')
        self.assertEqual(self.system.movies[0]['price'], 29.9)
        self.assertEqual(self.system.movies[0]['start_time'], datetime.strptime('17:05', '%H:%M'))
        self.assertEqual(self.system.movies[0]['end_time'], datetime.strptime('19:25', '%H:%M'))
        self.assertEqual(self.system.movies[0]['seats'].shape, (3, 3))

    def test_add_movie_5(self):
        self.system.add_movie('Batman', 19.9, '17:05', '19:25', 3)
        self.assertEqual(len(self.system.movies), 1)
        self.assertEqual(self.system.movies[0]['name'], 'Batman')
        self.assertEqual(self.system.movies[0]['price'], 19.9)
        self.assertEqual(self.system.movies[0]['start_time'], datetime.strptime('17:05', '%H:%M'))
        self.assertEqual(self.system.movies[0]['end_time'], datetime.strptime('19:25', '%H:%M'))
        self.assertEqual(self.system.movies[0]['seats'].shape, (3, 3))


class MovieBookingSystemTestBookTicket(unittest.TestCase):
    def setUp(self):
        self.system = MovieBookingSystem()
        self.system.add_movie('Batman', 49.9, '17:05', '19:25', 3)

    # book successfully
    def test_book_ticket_1(self):
        result = self.system.book_ticket('Batman', [(0, 0), (1, 1), (2, 2)])
        self.assertEqual(result, 'Booking success.')
        self.assertEqual(self.system.movies[0]['seats'][0][0], 1)
        self.assertEqual(self.system.movies[0]['seats'][1][1], 1)
        self.assertEqual(self.system.movies[0]['seats'][2][2], 1)

    # seat is not available
    def test_book_ticket_2(self):
        self.system.book_ticket('Batman', [(0, 0)])
        result = self.system.book_ticket('Batman', [(0, 0)])
        self.assertEqual(result, 'Booking failed.')
        self.assertEqual(self.system.movies[0]['seats'][0][0], 1)

    def test_book_ticket_3(self):
        result = self.system.book_ticket('batman', [(0, 0)])
        self.assertEqual(result, 'Movie not found.')
        self.assertEqual(self.system.movies[0]['seats'][0][0], 0)

    def test_book_ticket_4(self):
        result = self.system.book_ticket('Batman', [(0, 0), (1, 1)])
        self.assertEqual(result, 'Booking success.')
        self.assertEqual(self.system.movies[0]['seats'][0][0], 1)
        self.assertEqual(self.system.movies[0]['seats'][1][1], 1)

    def test_book_ticket_5(self):
        result = self.system.book_ticket('Batman', [(0, 0)])
        self.assertEqual(result, 'Booking success.')
        self.assertEqual(self.system.movies[0]['seats'][0][0], 1)


class MovieBookingSystemTestAvailableMovies(unittest.TestCase):
    def setUp(self):
        self.system = MovieBookingSystem()
        self.system.add_movie('Batman', 49.9, '17:05', '19:25', 3)
        self.system.add_movie('Spiderman', 59.9, '20:00', '22:30', 4)

    def test_available_movies_1(self):
        result = self.system.available_movies('16:00', '23:00')
        self.assertEqual(result, ['Batman', 'Spiderman'])

    def test_available_movies_2(self):
        result = self.system.available_movies('23:00', '23:59')
        self.assertEqual(result, [])

    def test_available_movies_3(self):
        result = self.system.available_movies('17:00', '20:00')
        self.assertEqual(result, ['Batman'])

    def test_available_movies_4(self):
        result = self.system.available_movies('10:00', '23:00')
        self.assertEqual(result, ['Batman', 'Spiderman'])

    def test_available_movies_5(self):
        result = self.system.available_movies('20:00', '23:00')
        self.assertEqual(result, ['Spiderman'])


class MovieBookingSystemTestMain(unittest.TestCase):
    def test_main(self):
        system = MovieBookingSystem()
        system.add_movie('Batman', 49.9, '17:05', '19:25', 3)
        self.assertEqual(len(system.movies), 1)
        self.assertEqual(system.movies[0]['name'], 'Batman')
        self.assertEqual(system.movies[0]['price'], 49.9)
        self.assertEqual(system.movies[0]['start_time'], datetime.strptime('17:05', '%H:%M'))
        self.assertEqual(system.movies[0]['end_time'], datetime.strptime('19:25', '%H:%M'))
        self.assertEqual(system.movies[0]['seats'].shape, (3, 3))

        result = system.book_ticket('Batman', [(0, 0), (1, 1), (2, 2)])
        self.assertEqual(result, 'Booking success.')
        self.assertEqual(system.movies[0]['seats'][0][0], 1)
        self.assertEqual(system.movies[0]['seats'][1][1], 1)
        self.assertEqual(system.movies[0]['seats'][2][2], 1)

        result = system.available_movies('16:00', '23:00')
        self.assertEqual(result, ['Batman'])
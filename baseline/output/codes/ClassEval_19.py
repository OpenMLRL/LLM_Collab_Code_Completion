class ChandrasekharSieve:
    """
    This is a class that uses the Chandrasekhar's Sieve method to find all prime numbers within the range
    """

    def __init__(self, n):
        """
        Initialize the ChandrasekharSieve class with the given limit.
        :param n: int, the upper limit for generating prime numbers
        """
        self.n = n
        self.primes = self.generate_primes()

    def generate_primes(self):
        """
        Generate prime numbers up to the specified limit using the Chandrasekhar sieve algorithm.
        :return: list, a list of prime numbers
        """
        sieve = [True] * (self.n + 1)
        sieve[0] = sieve[1] = False
        for i in range(2, int(self.n**0.5) + 1):
            if sieve[i]:
                for j in range(i*i, self.n + 1, i):
                    sieve[j] = False
        return [i for i in range(self.n + 1) if sieve[i]]

    def get_primes(self):
        """
        Get the list of generated prime numbers.
        :return: list, a list of prime numbers
        """
        return self.primes

import unittest


class ChandrasekharSieveTestGeneratePrimes(unittest.TestCase):
    def test_generate_primes_1(self):
        cs = ChandrasekharSieve(20)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])

    def test_generate_primes_2(self):
        cs = ChandrasekharSieve(18)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17])

    def test_generate_primes_3(self):
        cs = ChandrasekharSieve(15)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13])

    def test_generate_primes_4(self):
        cs = ChandrasekharSieve(10)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7])

    def test_generate_primes_5(self):
        cs = ChandrasekharSieve(1)
        res = cs.generate_primes()
        self.assertEqual(res, [])


class ChandrasekharSieveTestGetPrimes(unittest.TestCase):
    def test_get_primes_1(self):
        cs = ChandrasekharSieve(20)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])

    def test_get_primes_2(self):
        cs = ChandrasekharSieve(18)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17])

    def test_get_primes_3(self):
        cs = ChandrasekharSieve(15)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13])

    def test_get_primes_4(self):
        cs = ChandrasekharSieve(10)
        cs.generate_primes()
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7])

    def test_get_primes_5(self):
        cs = ChandrasekharSieve(1)
        res = cs.get_primes()
        self.assertEqual(res, [])


class ChandrasekharSieveTest(unittest.TestCase):
    def test_chandrasekharsieve(self):
        cs = ChandrasekharSieve(20)
        res = cs.generate_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])
        res = cs.get_primes()
        self.assertEqual(res, [2, 3, 5, 7, 11, 13, 17, 19])
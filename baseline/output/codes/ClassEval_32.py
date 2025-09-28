class DecryptionUtils:
    """
    This is a class that provides methods for decryption, including the Caesar cipher, Vigenere cipher, and Rail Fence cipher.
    """

    def __init__(self, key):
        """
        Initializes the decryption utility with a key.
        :param key: The key to use for decryption,str.
        """
        self.key = key

    def caesar_decipher(self, ciphertext, shift):
        """
        Deciphers the given ciphertext using the Caesar cipher
        :param ciphertext: The ciphertext to decipher,str.
        :param shift: The shift to use for decryption,int.
        :return: The deciphered plaintext,str.
        >>> d = DecryptionUtils('key')
        >>> d.caesar_decipher('ifmmp', 1)
        'hello'
        """
        plaintext = ''
        for char in ciphertext:
            if char.isalpha():
                shift_amount = shift % 26
                if char.islower():
                    decrypted_char = chr((ord(char) - ord('a') - shift_amount) % 26 + ord('a'))
                else:
                    decrypted_char = chr((ord(char) - ord('A') - shift_amount) % 26 + ord('A'))
                plaintext += decrypted_char
            else:
                plaintext += char
        return plaintext

    def vigenere_decipher(self, ciphertext):
        """
        Deciphers the given ciphertext using the Vigenere cipher
        :param ciphertext: The ciphertext to decipher,str.
        :return: The deciphered plaintext,str.
        >>> d = DecryptionUtils('key')
        >>> d.vigenere_decipher('ifmmp')
        'ybocl'
        """
        key = self.key
        key_length = len(key)
        plaintext = ''
        key_index = 0
        for char in ciphertext:
            if char.isalpha():
                shift = ord(key[key_index % key_length].upper()) - ord('A')
                key_index += 1
                if char.islower():
                    decrypted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
                else:
                    decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
                plaintext += decrypted_char
            else:
                plaintext += char
        return plaintext

    def rail_fence_decipher(self, encrypted_text, rails):
        """
        Deciphers the given ciphertext using the Rail Fence cipher
        :param encrypted_text: The ciphertext to decipher,str.
        :param rails: The number of rails to use for decryption,int.
        :return: The deciphered plaintext,str.
        >>> d = DecryptionUtils('key')
        >>> d.rail_fence_decipher('Hoo!el,Wrdl l', 3)
        'Hello, World!'
        """
        rail_layout = [[] for _ in range(rails)]
        index = 0
        direction = 1
        for char in encrypted_text:
            rail_layout[index].append(char)
            index += direction
            if index == rails - 1 or index == 0:
                direction *= -1
        plaintext = ''
        for rail in rail_layout:
            plaintext += ''.join(rail)
        return plaintext

import unittest


class DecryptionUtilsTestCaesarDecipher(unittest.TestCase):
    def test_caesar_decipher(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('ifmmp', 1), 'hello')

    def test_caesar_decipher_2(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('bcdyza', 27), 'abcxyz')

    def test_caesar_decipher_3(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('bcd', 0), 'bcd')

    def test_caesar_decipher_4(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('bcd', 26), 'bcd')

    def test_caesar_decipher_5(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('bcd', -26), 'bcd')

    def test_caesar_decipher_6(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('IFMMP', 1), 'HELLO')

    def test_caesar_decipher_7(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('123', 1), '123')


class DecryptionUtilsTestVigenereDecipher(unittest.TestCase):
    def test_vigenere_decipher(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.vigenere_decipher('ifmmp'), 'ybocl')

    def test_vigenere_decipher_2(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.vigenere_decipher('rijvs'), 'hello')

    def test_vigenere_decipher_3(self):
        d = DecryptionUtils('longkey')
        self.assertEqual(d.vigenere_decipher('LpPjOjE'), 'AbCdEfG')

    def test_vigenere_decipher_4(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.vigenere_decipher('bcd'), 'ryf')

    def test_vigenere_decipher_5(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.vigenere_decipher('bcdaa'), 'ryfqw')

    def test_vigenere_decipher_6(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.vigenere_decipher('123'), '123')


class DecryptionUtilsTestRailFenceDecipher(unittest.TestCase):
    def test_rail_fence_decipher(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.rail_fence_decipher('Hoo!el,Wrdl l', 3), 'Hello, World!')

    def test_rail_fence_decipher_2(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.rail_fence_decipher('Hoo!el,Wrdl l', 4), 'H!W reoldll,o')

    def test_rail_fence_decipher_3(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.rail_fence_decipher('Hoo!el,Wrdl l', 5), 'Holr d,!oeWll')

    def test_rail_fence_decipher_4(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.rail_fence_decipher('Hoo!el,Wrdl l', 6), 'Holrll d,!oeW')

    def test_rail_fence_decipher_5(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.rail_fence_decipher('Hoo!el,Wrdl l', 7), 'Hoe,rll dWl!o')


class DecryptionUtilsTestMain(unittest.TestCase):
    def test_main(self):
        d = DecryptionUtils('key')
        self.assertEqual(d.caesar_decipher('ifmmp', 1), 'hello')
        self.assertEqual(d.vigenere_decipher('ifmmp'), 'ybocl')
        self.assertEqual(d.rail_fence_decipher('Hoo!el,Wrdl l', 3), 'Hello, World!')
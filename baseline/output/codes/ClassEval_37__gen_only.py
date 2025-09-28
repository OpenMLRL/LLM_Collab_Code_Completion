class EncryptionUtils:
    """
    This is a class that provides methods for encryption, including the Caesar cipher, Vigenere cipher, and Rail Fence cipher.
    """

    def __init__(self, key):
        """
        Initializes the class with a key.
        :param key: The key to use for encryption, str.
        """
        self.key = key

    def caesar_cipher(self, plaintext, shift):
        """
        Encrypts the plaintext using the Caesar cipher.
        :param plaintext: The plaintext to encrypt, str.
        :param shift: The number of characters to shift each character in the plaintext, int.
        :return: The ciphertext, str.
        >>> e = EncryptionUtils("key")
        >>> e.caesar_cipher("abc", 1)
        'bcd'

        """
        result = ""
        for char in plaintext:
            if char.isalpha():
                shift_amount = shift % 26
                if char.islower():
                    result += chr((ord(char) - ord('a') + shift_amount) % 26 + ord('a'))
                else:
                    result += chr((ord(char) - ord('A') + shift_amount) % 26 + ord('A'))
            else:
                result += char
        return result

    def vigenere_cipher(self, plaintext):
        """
        Encrypts the plaintext using the Vigenere cipher.
        :param plaintext: The plaintext to encrypt, str.
        :return: The ciphertext, str.
        >>> e = EncryptionUtils("key")
        >>> e.vigenere_cipher("abc")
        'kfa'

        """
        key = self.key
        key_length = len(key)
        result = ""
        for i, char in enumerate(plaintext):
            if char.isalpha():
                key_char = key[i % key_length]
                shift = ord(key_char.lower()) - ord('a')
                if char.islower():
                    result += chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
                else:
                    result += chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
            else:
                result += char
        return result

    def rail_fence_cipher(self, plain_text, rails):
        """
        Encrypts the plaintext using the Rail Fence cipher.
        :param plaintext: The plaintext to encrypt, str.
        :return: The ciphertext, str.
        >>> e = EncryptionUtils("key")
        >>> e.rail_fence_cipher("abc", 2)
        'acb'

        """
        if rails == 1:
            return plain_text
        rail = [''] * rails
        direction = 1
        current_rail = 0
        for char in plain_text:
            rail[current_rail] += char
            if current_rail == rails - 1:
                direction = -1
            elif current_rail == 0:
                direction = 1
            current_rail += direction
        return ''.join(rail)
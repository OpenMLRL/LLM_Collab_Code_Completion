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
        """
        ciphertext = ""
        for char in plaintext:
            if char.isalpha():
                shift_amount = ord(char.lower()) - ord('a')
                shifted_char = chr((shift_amount + shift) % 26 + ord('a'))
                if char.isupper():
                    shifted_char = shifted_char.upper()
                ciphertext += shifted_char
            else:
                ciphertext += char
        return ciphertext

    def vigenere_cipher(self, plaintext):
        """
        Encrypts the plaintext using the Vigenere cipher.
        :param plaintext: The plaintext to encrypt, str.
        :return: The ciphertext, str.
        """
        ciphertext = ""
        for i, char in enumerate(plaintext):
            if char.isalpha():
                shift = ord(self.key[i % len(self.key)].lower()) - ord('a')
                shifted_char = chr((ord(char.lower()) - ord('a') + shift) % 26 + ord('a'))
                if char.isupper():
                    shifted_char = shifted_char.upper()
                ciphertext += shifted_char
            else:
                ciphertext += char
        return ciphertext

    def rail_fence_cipher(self, plaintext, rails):
        """
        Encrypts the plaintext using the Rail Fence cipher.
        :param plaintext: The plaintext to encrypt, str.
        :param rails: The number of rails to use in the Rail Fence cipher, int.
        :return: The ciphertext, str.
        """
        ciphertext = ""
        rail = 0
        direction = 1
        for char in plaintext:
            ciphertext += char
            rail += direction
            if rail == 0 or rail == rails - 1:
                direction *= -1
        return ciphertext
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
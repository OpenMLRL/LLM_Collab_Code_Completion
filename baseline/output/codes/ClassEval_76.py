class SignInSystem:
    """
    This is a class as sigin in system, including adding users, signing in/out, checking sign-in status, and retrieving signed-in/not signed-in users.
    """

    def __init__(self):
        """
        Initialize the sign-in system.
        """
        self.users = {}

    def add_user(self, username):
        """
        Add a user to the sign-in system if the user wasn't in the self.users.
        And the initial state is False.
        :param username: str, the username to be added.
        :return: bool, True if the user is added successfully, False if the user already exists.
        >>> signInSystem.add_user("mike")
        True
        >>> signInSystem.add_user("mike")
        False
        """
        if username in self.users:
            return False
        self.users[username] = False
        return True

    def sign_in(self, username):
        """
        Sign in a user if the user was in the self.users and change the state to True.
        :param username: str, the username to be signed in.
        :return: bool, True if the user is signed in successfully, False if the user does not exist.
        >>> signInSystem.sign_in("mike")
        True
        >>> signInSystem.sign_in("mik")
        False
        """
        if username not in self.users:
            return False
        self.users[username] = True
        return True

    def check_sign_in(self, username):
        """
        Check if a user is signed in.
        :param username: str, the username to be checked.
        :return: bool, True if the user is signed in, False if the user does not exist or is not signed in.
        >>> signInSystem.check_sign_in("jack")
        False
        >>> signInSystem.add_user("jack")
        >>> signInSystem.check_sign_in("jack")
        >>> signInSystem.sign_in("jack")
        >>> signInSystem.check_sign_in("jack")
        True
        """
        if username not in self.users:
            return False
        return self.users[username]

    def all_signed_in(self):
        """
        Check if all users are signed in.
        :return: bool, True if all users are signed in, False otherwise.
        >>> signInSystem.add_user("jack")
        True
        >>> signInSystem.sign_in("jack")
        >>> signInSystem.all_signed_in()
        True
        """
        for status in self.users.values():
            if not status:
                return False
        return True

    def all_not_signed_in(self):
        """
        Get a list of usernames that are not signed in.
        :return: list[str], a list of usernames that are not signed in.
        >>> signInSystem = SignInSystem()
        >>> signInSystem.add_user("a")
        True
        >>> signInSystem.add_user("b")
        True
        >>> signInSystem.all_not_signed_in()
        ['a', 'b']
        """
        return [username for username in self.users if not self.users[username]]

import unittest


class SignInSystemTestAddUser(unittest.TestCase):
    def test_add_user_1(self):
        signin_system = SignInSystem()
        result = signin_system.add_user("user1")
        self.assertTrue(result)

    def test_add_user_2(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        result = signin_system.add_user("user1")
        self.assertFalse(result)

    def test_add_user_3(self):
        signin_system = SignInSystem()
        result = signin_system.add_user("aaa")
        self.assertTrue(result)

    def test_add_user_4(self):
        signin_system = SignInSystem()
        result = signin_system.add_user("bbb")
        self.assertTrue(result)

    def test_add_user_5(self):
        signin_system = SignInSystem()
        result = signin_system.add_user("ccc")
        self.assertTrue(result)


class SignInSystemTestSignIn(unittest.TestCase):
    def test_sign_in_1(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        result = signin_system.sign_in("user1")
        self.assertTrue(result)

    # user not exist
    def test_sign_in_2(self):
        signin_system = SignInSystem()
        result = signin_system.sign_in("user1")
        self.assertFalse(result)

    def test_sign_in_3(self):
        signin_system = SignInSystem()
        signin_system.add_user("aaa")
        result = signin_system.sign_in("aaa")
        self.assertTrue(result)

    def test_sign_in_4(self):
        signin_system = SignInSystem()
        signin_system.add_user("bbb")
        result = signin_system.sign_in("bbb")
        self.assertTrue(result)

    def test_sign_in_5(self):
        signin_system = SignInSystem()
        result = signin_system.sign_in("ccc")
        self.assertFalse(result)


class SignInSystemTestCheckSignIn(unittest.TestCase):
    # has signed in
    def test_check_sign_in_1(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        signin_system.sign_in("user1")
        result = signin_system.check_sign_in("user1")
        self.assertTrue(result)

    # hasn't signed in 
    def test_check_sign_in_2(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        result = signin_system.check_sign_in("user1")
        self.assertFalse(result)

    # not exist
    def test_check_sign_in_3(self):
        signin_system = SignInSystem()
        result = signin_system.check_sign_in("user1")
        self.assertFalse(result)

    def test_check_sign_in_4(self):
        signin_system = SignInSystem()
        signin_system.add_user("aaa")
        signin_system.sign_in("aaa")
        result = signin_system.check_sign_in("aaa")
        self.assertTrue(result)

    def test_check_sign_in_5(self):
        signin_system = SignInSystem()
        signin_system.add_user("bbb")
        signin_system.sign_in("bbb")
        result = signin_system.check_sign_in("bbb")
        self.assertTrue(result)


class SignInSystemTestAllSignedIn(unittest.TestCase):
    def test_all_signed_in_1(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        signin_system.sign_in("user1")
        result = signin_system.all_signed_in()
        self.assertTrue(result)

    def test_all_signed_in_2(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        result = signin_system.all_signed_in()
        self.assertFalse(result)

    def test_all_signed_in_3(self):
        signin_system = SignInSystem()
        signin_system.add_user("aaa")
        signin_system.sign_in("aaa")
        result = signin_system.all_signed_in()
        self.assertTrue(result)

    def test_all_signed_in_4(self):
        signin_system = SignInSystem()
        signin_system.add_user("bbb")
        signin_system.sign_in("bbb")
        result = signin_system.all_signed_in()
        self.assertTrue(result)

    def test_all_signed_in_5(self):
        signin_system = SignInSystem()
        signin_system.add_user("aaa")
        signin_system.add_user("bbb")
        signin_system.sign_in("aaa")
        result = signin_system.all_signed_in()
        self.assertFalse(result)


class SignInSystemTestAllNotSignedIn(unittest.TestCase):
    def test_all_not_signed_in_1(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        signin_system.sign_in("user1")
        result = signin_system.all_not_signed_in()
        self.assertEqual([], result)

    def test_all_not_signed_in_2(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        signin_system.add_user("user2")
        result = signin_system.all_not_signed_in()
        self.assertEqual(["user1", "user2"], result)

    def test_all_not_signed_in_3(self):
        signin_system = SignInSystem()
        signin_system.add_user("aaa")
        signin_system.sign_in("aaa")
        result = signin_system.all_not_signed_in()
        self.assertEqual([], result)

    def test_all_not_signed_in_4(self):
        signin_system = SignInSystem()
        signin_system.add_user("user1")
        signin_system.add_user("aaa")
        signin_system.sign_in("user1")
        result = signin_system.all_not_signed_in()
        self.assertEqual(['aaa'], result)

    def test_all_not_signed_in_5(self):
        signin_system = SignInSystem()
        result = signin_system.all_not_signed_in()
        self.assertEqual([], result)


class SignInSystemTestMain(unittest.TestCase):
    def setUp(self):
        self.signin_system = SignInSystem()

    def test_main(self):
        result = self.signin_system.add_user("user1")
        result = self.signin_system.add_user("user2")
        self.assertTrue(result)

        result = self.signin_system.sign_in("user1")
        self.assertTrue(result)

        result = self.signin_system.check_sign_in("user1")
        self.assertTrue(result)

        result = self.signin_system.all_signed_in()
        self.assertFalse(result)

        result = self.signin_system.all_not_signed_in()
        self.assertEqual(["user2"], result)
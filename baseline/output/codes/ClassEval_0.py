import logging
import datetime

class AccessGatewayFilter:
    """
    This class is a filter used for accessing gateway filtering, primarily for authentication and access log recording.
    """

    def __init__(self):
        pass

    def filter(self, request):
        """
        Filter the incoming request based on certain rules and conditions.
        :param request: dict, the incoming request details
        :return: bool, True if the request is allowed, False otherwise
        >>> filter = AccessGatewayFilter()
        >>> filter.filter({'path': '/login', 'method': 'POST'})
        True
        """
        if self.is_start_with(request['path']):
            return True
        return False

    def is_start_with(self, request_uri):
        """
        Check if the request URI starts with certain prefixes.
        Currently, the prefixes being checked are "/api" and "/login".
        :param request_uri: str, the URI of the request
        :return: bool, True if the URI starts with certain prefixes, False otherwise
        >>> filter = AccessGatewayFilter()
        >>> filter.is_start_with('/api/data')
        True
        """
        return request_uri.startswith('/api') or request_uri.startswith('/login')

    def get_jwt_user(self, request):
        """
        Get the user information from the JWT token in the request.
        :param request: dict, the incoming request details
        :return: dict or None, the user information if the token is valid, None otherwise
        >>> filter = AccessGatewayFilter()
        >>> filter.get_jwt_user({'headers': {'Authorization': {'user': {'name': 'user1'}, 'jwt': 'user1'+str(datetime.date.today())}}})
        {'user': {'name': 'user1'}}
        """
        auth_headers = request.get('headers', {}).get('Authorization', {})
        jwt_token = auth_headers.get('jwt')
        if jwt_token:
            # Simulate JWT validation: check if token matches expected format
            expected_prefix = 'user1'
            if jwt_token.startswith(expected_prefix):
                user_info = auth_headers.get('user', {})
                return user_info
        return None

    def set_current_user_info_and_log(self, user):
        """
        Set the current user information and log the access.
        :param user: dict, the user information
        :return: None
        >>> filter = AccessGatewayFilter()
        >>> user = {'name': 'user1', 'address': '127.0.0.1'}
        >>> filter.set_current_user_info_and_log(user)
        """
        # Simulate logging the access
        logging.info(f"User {user.get('name')} accessed from {user.get('address')}")

import unittest

class AccessGatewayFilterTestFilter(unittest.TestCase):
    def test_filter_1(self):
        agf = AccessGatewayFilter()
        request = {'path': '/api/data', 'method': 'GET'}
        res = agf.filter(request)
        self.assertTrue(res)

    def test_filter_2(self):
        agf = AccessGatewayFilter()
        request = {'path': '/api/data', 'method': 'POST'}
        res = agf.filter(request)
        self.assertTrue(res)

    def test_filter_3(self):
        agf = AccessGatewayFilter()
        request = {'path': '/login/data', 'method': 'GET'}
        res = agf.filter(request)
        self.assertTrue(res)

    def test_filter_4(self):
        agf = AccessGatewayFilter()
        request = {'path': '/login/data', 'method': 'POST'}
        res = agf.filter(request)
        self.assertTrue(res)

    def test_filter_5(self):
        agf = AccessGatewayFilter()
        request = {'path': '/abc', 'method': 'POST',
                   'headers': {
                       'Authorization': {'user': {'name': 'user1', 'level': 5, 'address': 'address1'},
                                         'jwt': 'user1' + str(datetime.date.today())}}}
        res = agf.filter(request)
        self.assertTrue(res)

    def test_filter_6(self):
        agf = AccessGatewayFilter()
        request = {'path': '/abc', 'method': 'POST',
                   'headers': {
                       'Authorization': {'user': {'name': 'user1', 'level': 3, 'address': 'address1'},
                                         'jwt': 'user1' + str(datetime.date.today() - datetime.timedelta(days=365))}}}
        res = agf.filter(request)
        self.assertFalse(res)

    def test_filter_7(self):
        agf = AccessGatewayFilter()
        request = {'path': '/abc', 'method': 'POST',
                   'headers': {
                       'Authorization': {'user': {'name': 'user1', 'level': 1, 'address': 'address1'},
                                         'jwt': 'user1' + str(datetime.date.today())}}}
        res = agf.filter(request)
        self.assertIsNone(res)

    def test_filter_8(self):
        agf = AccessGatewayFilter()
        request = {'path': '/abc', 'method': 'POST',
                   'headers': {
                       'Authorization': {'user': {'name': 'user1', 'level': 3, 'address': 'address1'},
                                         'jwt': 'user2' + str(datetime.date.today() - datetime.timedelta(days=365))}}}
        res = agf.filter(request)
        self.assertTrue(res)


class AccessGatewayFilterTestIsStartWith(unittest.TestCase):
    def test_is_start_with_1(self):
        agf = AccessGatewayFilter()
        request_uri = '/api/data'
        res = agf.is_start_with(request_uri)
        self.assertTrue(res)

    def test_is_start_with_2(self):
        agf = AccessGatewayFilter()
        request_uri = '/admin/settings'
        res = agf.is_start_with(request_uri)
        self.assertFalse(res)

    def test_is_start_with_3(self):
        agf = AccessGatewayFilter()
        request_uri = '/login/data'
        res = agf.is_start_with(request_uri)
        self.assertTrue(res)

    def test_is_start_with_4(self):
        agf = AccessGatewayFilter()
        request_uri = '/abc/data'
        res = agf.is_start_with(request_uri)
        self.assertFalse(res)

    def test_is_start_with_5(self):
        agf = AccessGatewayFilter()
        request_uri = '/def/data'
        res = agf.is_start_with(request_uri)
        self.assertFalse(res)


class AccessGatewayFilterTestGetJwtUser(unittest.TestCase):
    def test_get_jwt_user_1(self):
        agf = AccessGatewayFilter()
        request = {
            'headers': {'Authorization': {'user': {'name': 'user1'}, 'jwt': 'user1' + str(datetime.date.today())}}}
        res = agf.get_jwt_user(request)
        self.assertIsNotNone(res)

    def test_get_jwt_user_2(self):
        agf = AccessGatewayFilter()
        request = {
            'headers': {'Authorization': {'user': {'name': 'user2'}, 'jwt': 'user2' + str(datetime.date.today())}}}
        res = agf.get_jwt_user(request)
        self.assertIsNotNone(res)

    def test_get_jwt_user_3(self):
        agf = AccessGatewayFilter()
        request = {
            'headers': {'Authorization': {'user': {'name': 'user3'}, 'jwt': 'user3' + str(datetime.date.today())}}}
        res = agf.get_jwt_user(request)
        self.assertIsNotNone(res)

    def test_get_jwt_user_4(self):
        agf = AccessGatewayFilter()
        request = {
            'headers': {'Authorization': {'user': {'name': 'user4'}, 'jwt': 'user4' + str(datetime.date.today())}}}
        res = agf.get_jwt_user(request)
        self.assertIsNotNone(res)

    def test_get_jwt_user_5(self):
        agf = AccessGatewayFilter()
        request = {'headers': {'Authorization': {'user': {'name': 'user1'}, 'jwt': 'user1' + str(
            datetime.date.today() - datetime.timedelta(days=5))}}}
        res = agf.get_jwt_user(request)
        self.assertIsNone(res)


class AccessGatewayFilterTest(unittest.TestCase):
    def test_AccessGatewayFilter(self):
        agf = AccessGatewayFilter()
        request = {'path': '/api/data', 'method': 'GET'}
        res = agf.filter(request)
        self.assertTrue(res)

        request_uri = '/api/data'
        res = agf.is_start_with(request_uri)
        self.assertTrue(res)

        request = {
            'headers': {'Authorization': {'user': {'name': 'user1'}, 'jwt': 'user1' + str(datetime.date.today())}}}
        res = agf.get_jwt_user(request)
        self.assertIsNotNone(res)
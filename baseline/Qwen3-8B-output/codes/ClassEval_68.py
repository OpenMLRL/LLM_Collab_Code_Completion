class PageUtil:
    """
    PageUtil class is a versatile utility for handling pagination and search functionalities in an efficient and convenient manner.
    """

    def __init__(self, data, page_size):
        """
        Initialize the PageUtil object with the given data and page size.
        :param data: list, the data to be paginated
        :param page_size: int, the number of items per page
        """
        self.data = data
        self.page_size = page_size
        self.total_items = len(data)
        self.total_pages = (self.total_items + page_size - 1) // page_size

    def get_page(self, page_number):
        """
        Retrieve a specific page of data.
        :param page_number: int, the page number to fetch
        :return: list, the data on the specified page
        >>> page_util = PageUtil([1, 2, 3, 4], 1)
        >>> page_util.get_page(1)
        [1]
        """
        if page_number < 1 or page_number > self.total_pages:
            return []
        start = (page_number - 1) * self.page_size
        end = start + self.page_size
        return self.data[start:end]

    def get_page_info(self, page_number):
        """
        Retrieve information about a specific page.
        :param page_number: int, the page number to fetch information about
        :return: dict, containing page information such as current page number, total pages, etc.
        >>> page_util = PageUtil([1, 2, 3, 4], 1)
        >>> page_util.get_page_info(1)
        >>> {
        >>>     "current_page": 1,
        >>>     "per_page": 1,
        >>>     "total_pages": 4,
        >>>     "total_items": 4,
        >>>     "has_previous": False,
        >>>     "has_next": True,
        >>>     "data": [1]
        >>> }
        """
        if page_number < 1 or page_number > self.total_pages:
            return {}
        start = (page_number - 1) * self.page_size
        end = start + self.page_size
        data = self.data[start:end]
        return {
            "current_page": page_number,
            "per_page": self.page_size,
            "total_pages": self.total_pages,
            "total_items": self.total_items,
            "has_previous": page_number > 1,
            "has_next": page_number < self.total_pages,
            "data": data
        }

    def search(self, keyword):
        """
        Search for items in the data that contain the given keyword.
        :param keyword: str, the keyword to search for
        :return: dict, containing search information such as total results and matching items
        >>> page_util = PageUtil([1, 2, 3, 4], 1)
        >>> page_util.search("1")
        >>> search_info = {
        >>>     "keyword": "1",
        >>>     "total_results": 1,
        >>>     "total_pages": 1,
        >>>     "results": [1]
        >>> }
        """
        if not keyword:
            return {
                "keyword": keyword,
                "total_results": 0,
                "total_pages": 0,
                "results": []
            }
        matched = [item for item in self.data if str(keyword).lower() in str(item).lower()]
        total_results = len(matched)
        total_pages = (total_results + self.page_size - 1) // self.page_size
        return {
            "keyword": keyword,
            "total_results": total_results,
            "total_pages": total_pages,
            "results": matched
        }

import unittest


class PageUtilTestGetPage(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.page_size = 3
        self.page_util = PageUtil(self.data, self.page_size)

    def test_get_page_1(self):
        page_number = 1
        expected_page = [1, 2, 3]
        actual_page = self.page_util.get_page(page_number)
        self.assertEqual(actual_page, expected_page)

    def test_get_page_2(self):
        page_number = 2
        expected_page = [4, 5, 6]
        actual_page = self.page_util.get_page(page_number)
        self.assertEqual(actual_page, expected_page)

    def test_get_page_3(self):
        page_number = 3
        expected_page = [7, 8, 9]
        actual_page = self.page_util.get_page(page_number)
        self.assertEqual(actual_page, expected_page)

    def test_get_page_4(self):
        page_number = 4
        expected_page = [10]
        actual_page = self.page_util.get_page(page_number)
        self.assertEqual(actual_page, expected_page)

    def test_get_page_5(self):
        invalid_page_number = 0
        empty_page = []
        actual_page = self.page_util.get_page(invalid_page_number)
        self.assertEqual(actual_page, empty_page)


class PageUtilTestGetPageInfo(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.page_size = 3
        self.page_util = PageUtil(self.data, self.page_size)

    def test_get_page_info_1(self):
        page_number = 2
        expected_info = {
            "current_page": 2,
            "per_page": 3,
            "total_pages": 4,
            "total_items": 10,
            "has_previous": True,
            "has_next": True,
            "data": [4, 5, 6]
        }
        actual_info = self.page_util.get_page_info(page_number)
        self.assertEqual(actual_info, expected_info)

    def test_get_page_info_2(self):
        page_number = 1
        expected_info = {
            "current_page": 1,
            "per_page": 3,
            "total_pages": 4,
            "total_items": 10,
            "has_previous": False,
            "has_next": True,
            "data": [1, 2, 3]
        }
        actual_info = self.page_util.get_page_info(page_number)
        self.assertEqual(actual_info, expected_info)

    def test_get_page_info_3(self):
        page_number = 3
        expected_info = {
            "current_page": 3,
            "per_page": 3,
            "total_pages": 4,
            "total_items": 10,
            "has_previous": True,
            "has_next": True,
            "data": [7, 8, 9]
        }
        actual_info = self.page_util.get_page_info(page_number)
        self.assertEqual(actual_info, expected_info)

    def test_get_page_info_4(self):
        page_number = 4
        expected_info = {
            "current_page": 4,
            "per_page": 3,
            "total_pages": 4,
            "total_items": 10,
            "has_previous": True,
            "has_next": False,
            "data": [10]
        }
        actual_info = self.page_util.get_page_info(page_number)
        self.assertEqual(actual_info, expected_info)

    def test_get_page_info_5(self):
        invalid_page_number = 5
        empty_info = {}
        actual_info = self.page_util.get_page_info(invalid_page_number)
        self.assertEqual(actual_info, empty_info)


class PageUtilTestSearch(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.page_size = 3
        self.page_util = PageUtil(self.data, self.page_size)

    def test_search_1(self):
        keyword = "1"
        expected_results = {
            "keyword": "1",
            "total_results": 2,
            "total_pages": 1,
            "results": [1, 10]
        }
        actual_results = self.page_util.search(keyword)
        self.assertEqual(actual_results, expected_results)

    def test_search_2(self):
        keyword = "2"
        expected_results = {
            "keyword": "2",
            "total_results": 1,
            "total_pages": 1,
            "results": [2]
        }
        actual_results = self.page_util.search(keyword)
        self.assertEqual(actual_results, expected_results)

    def test_search_3(self):
        keyword = "3"
        expected_results = {
            "keyword": "3",
            "total_results": 1,
            "total_pages": 1,
            "results": [3]
        }
        actual_results = self.page_util.search(keyword)
        self.assertEqual(actual_results, expected_results)

    def test_search_4(self):
        keyword = "4"
        expected_results = {
            "keyword": "4",
            "total_results": 1,
            "total_pages": 1,
            "results": [4]
        }
        actual_results = self.page_util.search(keyword)
        self.assertEqual(actual_results, expected_results)

    def test_search_5(self):
        keyword = "11"
        expected_results = {
            "keyword": "11",
            "total_results": 0,
            "total_pages": 0,
            "results": []
        }
        actual_results = self.page_util.search(keyword)
        self.assertEqual(actual_results, expected_results)


class PageUtilTest(unittest.TestCase):
    def setUp(self):
        self.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        self.page_size = 3
        self.page_util = PageUtil(self.data, self.page_size)

    def test_pageutil(self):
        page_number = 1
        expected_page = [1, 2, 3]
        actual_page = self.page_util.get_page(page_number)
        self.assertEqual(actual_page, expected_page)

        page_number = 2
        expected_info = {
            "current_page": 2,
            "per_page": 3,
            "total_pages": 4,
            "total_items": 10,
            "has_previous": True,
            "has_next": True,
            "data": [4, 5, 6]
        }
        actual_info = self.page_util.get_page_info(page_number)
        self.assertEqual(actual_info, expected_info)

        keyword = "4"
        expected_results = {
            "keyword": "4",
            "total_results": 1,
            "total_pages": 1,
            "results": [4]
        }
        actual_results = self.page_util.search(keyword)
        self.assertEqual(actual_results, expected_results)
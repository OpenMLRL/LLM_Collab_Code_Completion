class ShoppingCart:
    """
    The class manages items, their prices, quantities, and allows to for add, removie, view items, and calculate the total price.
    """

    def __init__(self):
        """
        Initialize the items representing the shopping list as an empty dictionary
        """
        self.items = {}


    def add_item(self, item, price, quantity=1):
        """
        Add item information to the shopping list items, including price and quantity. The default quantity is 1
        :param item: string, Item to be added
        :param price: float, The price of the item
        :param quantity:int, The number of items, defaults to 1
        :return:None
        >>> shoppingcart = ShoppingCart()
        >>> shoppingcart.add_item("apple", 1, 5)
        self.items = {"apple":{"price":1, "quantity":5}}
        """
        if item in self.items:
            self.items[item]['quantity'] += quantity
        else:
            self.items[item] = {'price': price, 'quantity': quantity}


    def remove_item(self, item, quantity=1):
        """
        Subtract the specified quantity of item from the shopping list items
        :param item:string, Item to be subtracted in quantity
        :param quantity:int, Quantity to be subtracted
        :return:None
        >>> shoppingcart.add_item("apple", 1, 5)
        >>> shoppingcart.remove_item("apple", 3)
        self.items = {"apple":{"price":1, "quantity":2}}
        """
        if item in self.items:
            if self.items[item]['quantity'] <= quantity:
                del self.items[item]
            else:
                self.items[item]['quantity'] -= quantity


    def view_items(self) -> dict:
        """
        Return the current shopping list items
        :return:dict, the current shopping list items
        >>> shoppingcart.add_item("apple", 1, 5)
        >>> shoppingcart.remove_item("apple", 3)
        >>> shoppingcart.view_items()
        {"apple":{"price":1, "quantity":2}}
        """
        return self.items.copy()


    def total_price(self) -> float:
        """
        Calculate the total price of all items in the shopping list, which is the quantity of each item multiplied by the price
        :return:float, the total price of all items in the shopping list
        >>> shoppingcart = ShoppingCart()
        >>> shoppingcart.add_item("apple", 1, 5)
        >>> shoppingcart.add_item("banana", 2, 3)
        >>> shoppingcart.total_price()
        11.0
        """
        total = 0.0
        for item in self.items:
            total += self.items[item]['price'] * self.items[item]['quantity']
        return total

import unittest


class ShoppingCartTestAddItem(unittest.TestCase):
    def test_add_item_1(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 5}})

    def test_add_item_2(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 1}})

    def test_add_item_3(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("aaa", 1)
        self.assertEqual(shoppingcart.items, {"aaa": {"price": 1, "quantity": 1}})

    def test_add_item_4(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("bbb", 1)
        self.assertEqual(shoppingcart.items, {"bbb": {"price": 1, "quantity": 1}})

    def test_add_item_5(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("ccc", 1)
        self.assertEqual(shoppingcart.items, {"ccc": {"price": 1, "quantity": 1}})

    def test_add_item_6(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.add_item("apple", 1, 5)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 5}})


class ShoppingCartTestRemoveItem(unittest.TestCase):
    def test_remove_item_1(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.remove_item("apple", 3)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 2}})

    def test_remove_item_2(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.remove_item("apple")
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 4}})

    def test_remove_item_3(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.remove_item("apple", 1)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 4}})

    def test_remove_item_4(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.remove_item("apple", 2)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 3}})

    def test_remove_item_5(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.remove_item("apple", 4)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 1}})

    def test_remove_item_6(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.remove_item("banana", 4)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 5}})


class ShoppingCartTestViewItems(unittest.TestCase):
    def test_view_items_1(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        self.assertEqual(shoppingcart.view_items(), {"apple": {"price": 1, "quantity": 5}})

    def test_view_items_2(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 4)
        self.assertEqual(shoppingcart.view_items(), {"apple": {"price": 1, "quantity": 4}})

    def test_view_items_3(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 3)
        self.assertEqual(shoppingcart.view_items(), {"apple": {"price": 1, "quantity": 3}})

    def test_view_items_4(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 2)
        self.assertEqual(shoppingcart.view_items(), {"apple": {"price": 1, "quantity": 2}})

    def test_view_items_5(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 1)
        self.assertEqual(shoppingcart.view_items(), {"apple": {"price": 1, "quantity": 1}})


class ShoppingCartTestTotalPrice(unittest.TestCase):
    def test_total_price_1(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.add_item("banana", 2, 3)
        self.assertEqual(shoppingcart.total_price(), 11.0)

    def test_total_price_2(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        shoppingcart.add_item("banana", 2, 3)
        shoppingcart.remove_item("apple", 3)
        self.assertEqual(shoppingcart.total_price(), 8.0)

    def test_total_price_3(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 1)
        shoppingcart.add_item("banana", 2, 1)
        self.assertEqual(shoppingcart.total_price(), 3.0)

    def test_total_price_4(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 2)
        shoppingcart.add_item("banana", 2, 1)
        self.assertEqual(shoppingcart.total_price(), 4.0)

    def test_total_price_5(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 3)
        shoppingcart.add_item("banana", 2, 1)
        self.assertEqual(shoppingcart.total_price(), 5.0)


class ShoppingCartTest(unittest.TestCase):
    def test_shoppingcart(self):
        shoppingcart = ShoppingCart()
        shoppingcart.add_item("apple", 1, 5)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 5}})
        self.assertEqual(shoppingcart.view_items(), {"apple": {"price": 1, "quantity": 5}})
        shoppingcart.remove_item("apple", 3)
        self.assertEqual(shoppingcart.items, {"apple": {"price": 1, "quantity": 2}})
        shoppingcart.add_item("banana", 2, 3)
        self.assertEqual(shoppingcart.total_price(), 8.0)
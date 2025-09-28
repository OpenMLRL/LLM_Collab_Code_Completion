class StockPortfolioTracker:
    """
    This is a class as StockPortfolioTracker that allows to add stocks, remove stocks, buy stocks, sell stocks, calculate the total value of the portfolio, and obtain a summary of the portfolio.
    """

    def __init__(self, cash_balance):
        """
        Initialize the StockPortfolioTracker class with a cash balance and an empty portfolio.
        """
        self.portfolio = []
        self.cash_balance = cash_balance

    def add_stock(self, stock):
        """
        Add a stock to the portfolio.
        :param stock: a dictionary with keys "name", "price", and "quantity"
        """
        self.portfolio.append(stock)

    def remove_stock(self, stock):
        """
        Remove a stock from the portfolio.
        :param stock: a dictionary with keys "name", "price", and "quantity"
        """
        for i, s in enumerate(self.portfolio):
            if s["name"] == stock["name"] and s["price"] == stock["price"] and s["quantity"] == stock["quantity"]:
                del self.portfolio[i]
                return True
        return False

    def buy_stock(self, stock):
        """
        Buy a stock and add it to the portfolio.
        :param stock: a dictionary with keys "name", "price", and "quantity"
        :param quantity: the quantity of the stock to buy,int.
        :return: True if the stock was bought successfully, False if the cash balance is not enough.
        """
        cost = stock["price"] * stock["quantity"]
        if self.cash_balance >= cost:
            self.cash_balance -= cost
            self.add_stock(stock)
            return True
        return False

    def sell_stock(self, stock):
        """
        Sell a stock and remove it from the portfolio and add the cash to the cash balance.
        :param stock: a dictionary with keys "name", "price", and "quantity"
        :param quantity: the quantity of the stock to sell,int.
        :return: True if the stock was sold successfully, False if the quantity of the stock is not enough.
        """
        for i, s in enumerate(self.portfolio):
            if s["name"] == stock["name"] and s["price"] == stock["price"]:
                if s["quantity"] >= stock["quantity"]:
                    self.cash_balance += stock["price"] * stock["quantity"]
                    del self.portfolio[i]
                    return True
                else:
                    return False
        return False

    def calculate_portfolio_value(self):
        """
        Calculate the total value of the portfolio.
        :return: the total value of the portfolio, float.
        """
        total_value = self.cash_balance
        for stock in self.portfolio:
            total_value += stock["price"] * stock["quantity"]
        return total_value

    def get_portfolio_summary(self):
        """
        Get a summary of the portfolio.
        :return: a tuple of the total value of the portfolio and a list of dictionaries with keys "name" and "value"
        """
        summary = []
        for stock in self.portfolio:
            summary.append({"name": stock["name"], "value": stock["price"] * stock["quantity"]})
        return (self.calculate_portfolio_value(), summary)

    def get_stock_value(self, stock):
        """
        Get the value of a stock.
        :param stock: a dictionary with keys "name", "price", and "quantity"
        :return: the value of the stock, float.
        """
        return stock["price"] * stock["quantity"]

import unittest


class StockPortfolioTrackerTestAddStock(unittest.TestCase):
    def test_add_stock(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.add_stock({"name": "AAPL", "price": 150.0, "quantity": 10})
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}])

    def test_add_stock_2(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        tracker.add_stock({"name": "AAPL", "price": 150.0, "quantity": 10})
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 20}])

    def test_add_stock_3(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        tracker.add_stock({"name": "MSFT", "price": 150.0, "quantity": 10})
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])

    def test_add_stock_4(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        tracker.add_stock({"name": "AAPL", "price": 150.0, "quantity": 10})
        tracker.add_stock({"name": "MSFT", "price": 150.0, "quantity": 10})
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 20},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])

    def test_add_stock_5(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        tracker.add_stock({"name": "AAPL", "price": 150.0, "quantity": 10})
        tracker.add_stock({"name": "MSFT", "price": 150.0, "quantity": 10})
        tracker.add_stock({"name": "MSFT", "price": 150.0, "quantity": 10})
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 20},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 20}])


class StockPortfolioTrackerTestRemoveStock(unittest.TestCase):
    def test_remove_stock(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.remove_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [])

    def test_remove_stock_2(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.remove_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'MSFT', 'price': 150.0, 'quantity': 10}])

    def test_remove_stock_3(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.remove_stock({"name": "MSFT", "price": 150.0, "quantity": 20}), False)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])

    def test_remove_stock_4(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.remove_stock({"name": "MSFT", "price": 150.0, "quantity": 10}), False)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}])

    def test_remove_stock_5(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.remove_stock({"name": "MSFT", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}])


class StockPortfolioTrackerTestBuyStock(unittest.TestCase):
    def test_buy_stock(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.buy_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 8500.0)

    def test_buy_stock_2(self):
        tracker = StockPortfolioTracker(1000.0)
        self.assertEqual(tracker.buy_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), False)
        self.assertEqual(tracker.portfolio, [])
        self.assertEqual(tracker.cash_balance, 1000.0)

    def test_buy_stock_3(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.buy_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 20}])
        self.assertEqual(tracker.cash_balance, 8500.0)

    def test_buy_stock_4(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.buy_stock({"name": "MSFT", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.buy_stock({"name": "MSFT", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 20}])
        self.assertEqual(tracker.cash_balance, 7000.0)

    def test_buy_stock_5(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.buy_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.buy_stock({"name": "MSFT", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 20},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 7000.0)


class StockPortfolioTrackerTestSellStock(unittest.TestCase):
    def test_sell_stock(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.sell_stock({"name": "AAPL", "price": 150.0, "quantity": 9}), True)
        self.assertEqual(tracker.portfolio, [{"name": "AAPL", "price": 150.0, "quantity": 1}])
        self.assertEqual(tracker.cash_balance, 11350.0)

    def test_sell_stock_2(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.sell_stock({"name": "AAPL", "price": 150.0, "quantity": 20}), False)
        self.assertEqual(tracker.portfolio, [{"name": "AAPL", "price": 150.0, "quantity": 10}])
        self.assertEqual(tracker.cash_balance, 10000.0)

    def test_sell_stock_3(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.sell_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), False)
        self.assertEqual(tracker.portfolio, [])
        self.assertEqual(tracker.cash_balance, 10000.0)

    def test_sell_stock_4(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 20}]
        self.assertEqual(tracker.sell_stock({"name": "AAPL", "price": 150.0, "quantity": 20}), True)
        self.assertEqual(tracker.portfolio, [])
        self.assertEqual(tracker.cash_balance, 13000.0)

    def test_sell_stock_5(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 20},
                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.sell_stock({"name": "AAPL", "price": 150.0, "quantity": 20}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 13000.0)


class StockPortfolioTrackerTestCalculatePortfolioValue(unittest.TestCase):
    def test_calculate_portfolio_value(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.calculate_portfolio_value(), 11500.0)

    def test_calculate_portfolio_value_2(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.calculate_portfolio_value(), 13000.0)

    def test_calculate_portfolio_value_3(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.calculate_portfolio_value(), 10000.0)

    def test_calculate_portfolio_value_4(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 0}]
        self.assertEqual(tracker.calculate_portfolio_value(), 10000.0)

    def test_calculate_portfolio_value_5(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 0.0, 'quantity': 10}]
        self.assertEqual(tracker.calculate_portfolio_value(), 10000.0)


class StockPortfolioTrackerTestGetPortfolioSummary(unittest.TestCase):
    def test_get_portfolio_summary(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.get_portfolio_summary(), (11500.0, [{'name': 'AAPL', 'value': 1500.0}]))

    def test_get_portfolio_summary_2(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.get_portfolio_summary(),
                         (13000.0, [{'name': 'AAPL', 'value': 1500.0}, {'name': 'MSFT', 'value': 1500.0}]))

    def test_get_portfolio_summary_3(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.get_portfolio_summary(), (10000.0, []))

    def test_get_portfolio_summary_4(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 0}]
        self.assertEqual(tracker.get_portfolio_summary(), (10000.0, [{'name': 'AAPL', 'value': 0.0}]))

    def test_get_portfolio_summary_5(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 0.0, 'quantity': 10}]
        self.assertEqual(tracker.get_portfolio_summary(), (10000.0, [{'name': 'AAPL', 'value': 0.0}]))


class StockPortfolioTrackerTestGetStockValue(unittest.TestCase):
    def test_get_stock_value(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.get_stock_value({"name": "AAPL", "price": 150.0, "quantity": 10}), 1500.0)

    def test_get_stock_value_2(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.get_stock_value({"name": "AAPL", "price": 150.0, "quantity": 0}), 0.0)

    def test_get_stock_value_3(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.get_stock_value({"name": "AAPL", "price": 0.0, "quantity": 10}), 0.0)

    def test_get_stock_value_4(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.get_stock_value({"name": "AAPL", "price": 0.0, "quantity": 0}), 0.0)

    def test_get_stock_value_5(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.get_stock_value({"name": "MSFL", "price": 150.0, "quantity": 2}), 300.0)


class StockPortfolioTrackerTestMain(unittest.TestCase):
    def test_main(self):
        tracker = StockPortfolioTracker(10000.0)
        self.assertEqual(tracker.add_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), None)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.buy_stock({"name": "MSFT", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 8500.0)
        self.assertEqual(tracker.sell_stock({"name": "AAPL", "price": 150.0, "quantity": 9}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 1},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 9850.0)
        self.assertEqual(tracker.remove_stock({"name": "AAPL", "price": 150.0, "quantity": 1}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.calculate_portfolio_value(), 11350.0)
        self.assertEqual(tracker.get_portfolio_summary(), (11350.0, [{'name': 'MSFT', 'value': 1500.0}]))
        self.assertEqual(tracker.get_stock_value({"name": "MSFT", "price": 150.0, "quantity": 10}), 1500.0)

    def test_main_2(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.add_stock({"name": "MSFT", "price": 150.0, "quantity": 10}), None)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.remove_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.calculate_portfolio_value(), 11500.0)
        self.assertEqual(tracker.get_portfolio_summary(), (11500.0, [{'name': 'MSFT', 'value': 1500.0}]))
        self.assertEqual(tracker.get_stock_value({"name": "MSFT", "price": 150.0, "quantity": 10}), 1500.0)
        self.assertEqual(tracker.buy_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'MSFT', 'price': 150.0, 'quantity': 10},
                                             {'name': 'AAPL', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 8500.0)

    def test_main_3(self):
        tracker = StockPortfolioTracker(10000.0)
        tracker.portfolio = [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}]
        self.assertEqual(tracker.get_stock_value({"name": "MSFT", "price": 150.0, "quantity": 10}), 1500.0)
        self.assertEqual(tracker.buy_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 20},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 8500.0)
        self.assertEqual(tracker.sell_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'AAPL', 'price': 150.0, 'quantity': 10},
                                             {'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.cash_balance, 10000.0)
        self.assertEqual(tracker.remove_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), True)
        self.assertEqual(tracker.portfolio, [{'name': 'MSFT', 'price': 150.0, 'quantity': 10}])
        self.assertEqual(tracker.calculate_portfolio_value(), 11500.0)
        self.assertEqual(tracker.get_portfolio_summary(), (11500.0, [{'name': 'MSFT', 'value': 1500.0}]))
        self.assertEqual(tracker.get_stock_value({"name": "MSFT", "price": 150.0, "quantity": 10}), 1500.0)
        self.assertEqual(tracker.add_stock({"name": "AAPL", "price": 150.0, "quantity": 10}), None)
        self.assertEqual(tracker.portfolio, [{'name': 'MSFT', 'price': 150.0, 'quantity': 10},
                                             {'name': 'AAPL', 'price': 150.0, 'quantity': 10}])
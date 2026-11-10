import unittest

from shopfront.inventory import stock


class StockTest(unittest.TestCase):
    def setUp(self):
        stock._stock.clear()

    def test_reserve_reduces_stock(self):
        stock.restock("A", 10)
        stock.reserve("A", 3)
        self.assertEqual(stock._stock["A"], 7)

    def test_reserve_rejects_oversell(self):
        stock.restock("A", 1)
        with self.assertRaises(ValueError):
            stock.reserve("A", 2)

    def test_low_stock(self):
        stock.restock("A", 2)
        stock.restock("B", 50)
        self.assertEqual(stock.low_stock_skus(), ["A"])


if __name__ == "__main__":
    unittest.main()

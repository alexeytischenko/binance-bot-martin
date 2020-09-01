import unittest
import exchange_data
import sys


class TestExchangeData(unittest.TestCase):
    """
    Tests receiving exchange assets info.

    Test will be skipped unless it is ran manually in command line: python test_exchange_data.py exchange
    """

    @unittest.skipUnless(len(sys.argv) > 1 and sys.argv[1] == "exchange", "Requires commandline argument: exchange")
    def test_data_dict(self):
        """Tests assets info list length and that 'BNBBTC' key exists."""

        exchange = exchange_data.ExchangeData.get_instance()

        self.assertTrue(
            "BNBBTC" in exchange.info,
            "Failed to receive assets data"
        )
        self.assertGreater(
            len(exchange.info),
            0,
            "Assets data list is empty"
        )


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)

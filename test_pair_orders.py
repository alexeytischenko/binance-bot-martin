import unittest
import pair_orders


class TestPairOrders(unittest.TestCase):

    def test_meta_calc(self):
        """Tests new pair of orders metadata calculation."""

        # incoming test position
        po = pair_orders.PairOrders({
            "order_id": 123456,
            "pair": "ADABNB",
            "side": "SELL",
            "size": 50,
            "price": 0.003327
        })

        # self.assertAlmostEqual(po.meta["reduce"]["price"],
        #                        0.003327 * (1 - pair_orders.REDUCE_VALUE),
        #                        8,
        #                        "Reduce order price miscalculated!")

        # test reduce/close position order
        self.assertDictEqual(
            po.meta["close"],
            {
                "order_id": 123456,
                "pair": "ADABNB",
                "price": 0.003327 * (1 - pair_orders.REDUCE_VALUE),
                "side": "BUY",
                "size": 50,
                "enough_funds": True
            },
            "Close order metadata is incorrect"
        )

        # test increase position order
        self.assertDictEqual(
            po.meta["increase"],
            {
                "order_id": 123456,
                "pair": "ADABNB",
                "price": 0.003327 * (1 + pair_orders.INCREASE_VALUE),
                "side": "SELL",
                "size": 50 * pair_orders.SIZE_MULTIPLICATION,
                "enough_funds": True
            },
            "Increase order metadata is incorrect"
        )

    def test_check_enough_funds(self):
        """Tests if checking funds is correct."""

        # wallets
        enough = [("ADA", 500), ("BNB", 100)]
        not_enough = [("ADA", 1), ("BNB", 0.001)]

        # incoming test SELL position
        po_sell = pair_orders.PairOrders({
            "order_id": 123456,
            "pair": "ADABNB",
            "side": "SELL",
            "size": 50,
            "price": 0.003327
        })

        # check against enough funds
        close_enough_funds, increase_enough_funds = po_sell.check_funds(enough)
        self.assertTrue(close_enough_funds, "SELL position: Quote asset test against enough funds is not correct")
        self.assertTrue(increase_enough_funds, "SELL position: Base asset test against enough funds is not correct")

        # check against empty wallet
        close_enough_funds, increase_enough_funds = po_sell.check_funds(not_enough)
        self.assertFalse(close_enough_funds, "SELL position: Quote asset test against empty wallet is not correct")
        self.assertFalse(increase_enough_funds, "SELL position: Base asset test against empty wallet is not correct")

        # incoming test Buy position
        po_buy = pair_orders.PairOrders({
            "order_id": 123456,
            "pair": "ADABNB",
            "side": "BUY",
            "size": 50,
            "price": 0.003327
        })

        # check against enough funds
        close_enough_funds, increase_enough_funds = po_buy.check_funds(enough)
        self.assertTrue(close_enough_funds, "BUY position: Base asset test against enough funds is not correct")
        self.assertTrue(increase_enough_funds, "BUY position: Quote asset test against enough funds is not correct")

        # check against empty wallet
        close_enough_funds, increase_enough_funds = po_buy.check_funds(not_enough)
        self.assertFalse(close_enough_funds, "BUY position: Base asset test against empty wallet is not correct")
        self.assertFalse(increase_enough_funds, "BUY position: Quote asset test against empty wallet is not correct")


if __name__ == '__main__':
    unittest.main()

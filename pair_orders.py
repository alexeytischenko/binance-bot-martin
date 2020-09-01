import json
import math
import urllib.request
from typing import Dict
from exchange_data import ExchangeData
import binance.exceptions
from binance.client import Client
import bot_log
import bot_db
import bot_client

REDUCE_VALUE = 0.03
INCREASE_VALUE = 0.05
SIZE_MULTIPLICATION = 2


class PairOrders:
    """
    This is a class for placing a new pair of orders.

    On each iteration bot is placing a pair of orders, first one to increase position, other to decrease or close

    Attributes:
    meta (dict): new position
    """

    meta = {}
    pair = ""

    def __init__(self, input_meta: dict):
        """
        The PairOrders class constructor.

        Parameters:
        input_meta (dict): current open position meta data. {pair, side, size of base asset, avg. price}
        """

        # calculate new parameters of the position
        self.meta = {
            "close": {
                "order_id": input_meta["order_id"],
                "pair": input_meta["pair"],
                "size": input_meta["size"],
                "price": input_meta["price"] * (1 - REDUCE_VALUE) if input_meta["side"] == "SELL" else input_meta[
                                                                                                           "price"] * (
                                                                                                               1 + REDUCE_VALUE),
                "side": "SELL" if input_meta["side"] == "BUY" else "BUY",
                "enough_funds": True
            },
            "increase": {
                "order_id": input_meta["order_id"],
                "pair": input_meta["pair"],
                "size": input_meta["size"] * SIZE_MULTIPLICATION,
                "price": input_meta["price"] * (1 + INCREASE_VALUE) if input_meta["side"] == "SELL" else input_meta[
                                                                                                             "price"] * (
                                                                                                                 1 - INCREASE_VALUE),
                "side": input_meta["side"],
                "enough_funds": True
            }
        }
        self.pair = input_meta["pair"]

    def make_limit_order(self, info: str):
        """
        Makes Limit order based on info input data and creates DB record

        Parameters:
        info (str): key name in self.meta dict

        Return:
        dict: placed order info
        """
        bot_log.log_status(f"Making limit order for {info}...")
        exchange = ExchangeData.get_instance()
        precision_base = exchange.info[self.pair]["baseAssetPrecision"]
        quantity = round(self.meta[info]["size"], precision_base)
        # precision_quote = exchange.info[self.pair]["quoteAssetPrecision"]
        precision_quote = int(round(-math.log(float(exchange.info[self.pair]["PRICE_FILTER"]["minPrice"]), 10), 0))
        price = round(self.meta[info]["price"], precision_quote)
        bot_log.log_status(f"pair: {self.meta[info]['pair']} quantity: {quantity}, price: {price}")
        try:
            limit_order = bot_client.client.create_order(
                symbol=self.meta[info]["pair"],
                side=self.meta[info]["side"],
                type=Client.ORDER_TYPE_LIMIT,
                quantity=quantity,
                price=price,
                timeInForce='GTC'
            )
            # write log
            bot_log.log_status(limit_order)
            # calculates order properties
            limit_order["initial_order_id"] = self.meta[info]["order_id"]
            limit_order["order_avg_price"] = price
            limit_order["order_commission"] = 0
            limit_order['executedQty'] = quantity
            # write to DB
            try:
                bot_db.limit_order(limit_order)
            except Exception as ex:
                bot_log.log_status(ex)

            return limit_order

        except binance.exceptions.BinanceAPIException as ex:
            bot_log.log_status(ex)

    def make_orders(self):
        """ Creates 2 limit orders by calling self.make_limit_order """
        # Make ["close", "increase"] orders
        bot_log.log_status("Making pair of orders...")
        for side in ["close", "increase"]:
            self.make_limit_order(side)
        # orders_map_object = map(self.make_limit_order, ["close", "increase"])


    def check_funds(self, funds):
        """
        Checks if there're enough funds to make new orders and update position metadata

        Parameters:
        funds (list[tuple]) : list of wallet assets and their values

        Returns:
        bool: enough funds for close order
        bool: enough funds for increase order
        """
        close_enough_funds, increase_enough_funds = True, True

        exchange = ExchangeData.get_instance()
        base_asset = exchange.info[self.pair]['base']
        base_value_list = list(filter(lambda asset_tuple: asset_tuple[0] == base_asset, funds))
        base_value = 0 if len(base_value_list) == 0 else float(base_value_list[0][1])
        quote_asset = exchange.info[self.pair]['quote']
        quote_value_list = list(filter(lambda asset_tuple: asset_tuple[0] == quote_asset, funds))
        quote_value = 0 if len(quote_value_list) == 0 else float(quote_value_list[0][1])

        # close order check
        if (self.meta["close"]["side"] == "SELL" and
            base_value < self.meta["close"]["size"]) or \
                (self.meta["close"]["side"] == "BUY" and
                 quote_value < self.meta["close"]["size"] * self.meta["close"]["price"]):
            close_enough_funds = False

        # increase order check
        if (self.meta["increase"]["side"] == "SELL" and
            base_value < self.meta["close"]["size"]) or \
                (self.meta["increase"]["side"] == "BUY" and
                 quote_value < self.meta["increase"]["size"] * self.meta["increase"]["price"]):
            increase_enough_funds = False

        # update position metadata
        self.meta["close"]["enough_funds"] = close_enough_funds
        self.meta["increase"]["enough_funds"] = increase_enough_funds

        # log
        bot_log.log_status(f"Funds check result: close_enough_funds - {close_enough_funds}, \
        increase_enough_funds - {increase_enough_funds}")

        return close_enough_funds, increase_enough_funds

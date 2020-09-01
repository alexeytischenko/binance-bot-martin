import json
from exchange_data import ExchangeData
import bot_log
import bot_db
import bot_client
from pair_orders import PairOrders
from exceptions import NotEnoughFundsError
import config
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import binance.exceptions
from binance.client import Client

import sys

# 0. Necessary checks
# 0.1. Entry default parameters
pair = "ADABNB"
side = "BUY"
qnt = 50
# override parameters from the command line
if len(sys.argv) == 4:
    pair = sys.argv[1]
    side = sys.argv[2]
    if side.upper() not in ["SELL", "BUY"]:
        raise ValueError("Side can only be SELL or BUY")
    qnt = float(sys.argv[3])
    if qnt <= 0:
        raise ValueError("Amount must be positive")
    bot_log.log_status(f"Pair: {pair}, side: {side}, qnt: {qnt}")
else:
    bot_log.log_status(f"Using default params ({pair} {side} {qnt}).\
    To override: python bot_init.py pair[TRXBNB] side[SELL] qnt[50]")

# 1. Make an initial order
try:
    initial_order = bot_client.client.create_order(
        symbol=pair,
        side=side,
        type=Client.ORDER_TYPE_MARKET,
        quantity=qnt
    )
    bot_log.log_status(initial_order)
    """
    Returned order info, sample:
    {'symbol': 'BNBBTC', 'orderId': 381056034, 'orderListId': -1, 'clientOrderId': 'UKZWTorB1EZsSlBaxtGlwW', 
    'transactTime': 1588718071792, 'price': '0.00000000', 'origQty': '0.10000000', 'executedQty': '0.10000000', 
    'cummulativeQuoteQty': '0.00018754', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'MARKET', 'side': 'BUY', 
    'fills': [{'price': '0.00187540', 'qty': '0.10000000', 'commission': '0.00007500', 'commissionAsset': 'BNB', 
    'tradeId': 77304381}]}
    """

    # calculates order properties
    initial_order["initial_order_commission"] = sum([float(fill['commission']) for fill in initial_order['fills']])
    initial_order["initial_order_avg_price"] = float(initial_order['cummulativeQuoteQty']) / float(
        initial_order['executedQty'])

    bot_log.log_status("Order. Pair: {}, Q: {}, avg price: {}, commission: {}, Fills: {}".
                       format(pair,
                              qnt,
                              initial_order["initial_order_avg_price"],
                              initial_order["initial_order_commission"],
                              initial_order['fills']
                              )
                       )

    # 1.1 Write order info to the DB
    try:
        bot_db.initial_order(initial_order)
    except Exception as ex:
        bot_log.log_status(ex)

    # 1.2. Check BTC balance
    # receive wallet info {'asset': 'BTC', 'free': '0.00431343', 'locked': '0.00000000'}
    balanceRequest = bot_client.client.get_account()

    # check if wallet is not empty
    if "balances" not in balanceRequest:
        raise NotEnoughFundsError("Your Binance wallet is empty")

    # creating wallet info as a list of tuples, eg [("ADA", 500), ("BNB", "10")]
    balances = [(bal["asset"], bal["free"]) for bal in balanceRequest['balances'] if float(bal["free"]) > 0]
    if len(balances) == 0:
        raise NotEnoughFundsError("Your Binance balance is insufficient to proceed with the orders")
    bot_log.log_status(f"Your active balance is: {balances}")

    # 2. Make a pair of orders to close/increase position
    try:
        # 2.1 Create current position meta-data and pass it to the PairOrders object
        # {pair, side, size of base asset, avg. price}
        current_position = {
            "order_id": initial_order["orderId"],
            "pair": pair,
            "side": side,
            "size": float(initial_order['executedQty']),
            "price": initial_order["initial_order_avg_price"]
        }
        update_position = PairOrders(current_position)
        close_enough_funds, increase_enough_funds = update_position.check_funds(balances)

        # 2.2 Places orders
        if close_enough_funds and increase_enough_funds:
            # place Close and Increase Position Orders
            update_position.make_orders()
        else:
            if close_enough_funds:
                # places a Close Position Order
                update_position.make_limit_order("close")
                raise NotEnoughFundsError("Not enough funds to place an Increase Position Order")
            else:
                # impossible situation - no funds to place a Close Position Order
                raise NotEnoughFundsError("Something goes wrong! Not enough funds to place Close Position Order")

    except NotEnoughFundsError as ex:
        bot_log.log_status(ex)
        exit(-1)

except binance.exceptions.BinanceAPIException as ex:
    bot_log.log_status(ex)
    bot_log.log_status("Exit bot")

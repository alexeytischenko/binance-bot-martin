#!/home/admin/.pyenv/versions/3.8.2/bin/python

import json
from exchange_data import ExchangeData
import bot_log
import bot_db
import bot_client
from pair_orders import PairOrders
from exceptions import NotEnoughFundsError, UnexpectedOrdersError, OrderRejected


# 0. Check BTC balance
# receive wallet info {'asset': 'BTC', 'free': '0.00431343', 'locked': '0.00000000'}
balanceRequest = bot_client.client.get_account()

# check if wallet is not empty
if "balances" not in balanceRequest:
    raise NotEnoughFundsError("Your Binance wallet is empty")

# creating wallet info as a list of tuples, eg [("ADA", 500), ("BNB", "10")]
balances = [(bal["asset"], bal["free"]) for bal in balanceRequest['balances'] if float(bal["free"]) > 0]

# 1. SELECT all open positions
try:
    all_open_positions = bot_db.select_open_positions()

    if len(all_open_positions) == 0:
        bot_log.log_status("There is no open positions. Exit")
        raise Exception("Stop working...")

    for open_position in all_open_positions:
        print(open_position["order_id"])

        # 2.1 SELECT orders from given position with 'NEW' status
        martingale_open_orders = bot_db.select_position_orders(open_position["order_id"], True)
        number_of_orders = len(martingale_open_orders)

        # 2.1.1 Error occurred: if there are zero or more than 2 orders or the only order is increasing
        try:
            bot_log.log_status("Checking number of orders...")
            if number_of_orders == 0 or \
                    number_of_orders > 2 or \
                    (number_of_orders == 1 and martingale_open_orders[0]["side"] == open_position["side"]):
                # 2.2.2 Mark initial order position as ERROR
                bot_db.mark_position(open_position["order_id"], "ERROR")

                # mark martingale_orders status as ERROR and cancel them
                if number_of_orders != 0:
                    for order in martingale_open_orders:
                        bot_db.mark_order(order["order_id"], "ERROR")
                        result = bot_client.client.cancel_order(symbol=open_position["pair"], orderId=order["order_id"])
                        bot_log.log_status(f"Cancel order: {result}")

                raise UnexpectedOrdersError(f"Ouch! Found {number_of_orders} orders in "
                                            f"martingale_order, position: {open_position['order_id']}")

        except UnexpectedOrdersError as ex:
            bot_log.log_status(ex)

        # 2.2 Retrieves orders statuses from Binance
        bot_log.log_status("Retrieves orders statuses from Binance")
        binance_orders = []
        binance_statuses = []
        for order in martingale_open_orders:
            bo = bot_client.client.get_order(
                symbol=order['pair'],
                orderId=order['order_id'])

            # check statuses
            if bo["status"] in ["CANCELED", "REJECTED", "EXPIRED"]:
                bot_db.mark_order(order["order_id"], "ERROR")
                raise OrderRejected(f"Order {order['order_id']} has {bo['status']} status")

            binance_orders.append(bo)
            binance_statuses.append(bo["status"])

        bot_log.log_status(binance_orders)
        """
[ {'symbol': 'ADABNB', 'orderId': 47752850, 'orderListId': -1, 'clientOrderId': 'ZtHwctwDraoOaB9T0033BH', 
'price': '0.00450500', 'origQty': '25.00000000', 'executedQty': '25.00000000', 'cummulativeQuoteQty': 
'0.11262500', 'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'BUY', 'stopPrice': 
'0.00000000', 'icebergQty': '0.00000000', 'time': 1591052712889, 'updateTime': 1591054723780, 'isWorking': 
True, 'origQuoteOrderQty': '0.00000000'}, 

{'symbol': 'ADABNB', 'orderId': 47752853, 'orderListId': -1, 'clientOrderId': 'tYQx3RgcfHKtijoNkDHYyY', 
'price': '0.00487600', 'origQty': '50.00000000', 'executedQty': '50.00000000', 'cummulativeQuoteQty': '0.24380000', 
'status': 'FILLED', 'timeInForce': 'GTC', 'type': 'LIMIT', 'side': 'SELL', 'stopPrice': '0.00000000', 'icebergQty': 
'0.00000000', 'time': 1591052714394, 'updateTime': 1591195399868, 'isWorking': True, 'origQuoteOrderQty': 
'0.00000000'}] 
        """

        # 2.2.1 If all orders are active (NEW or PARTIALLY_FILLED) just stop running
        if "FILLED" not in binance_statuses:
            bot_log.log_status(f"All orders are active. Position: {open_position['order_id']}")
            continue

        # 2.2.2 If all orders (more than one order) are FILLED - mark position and all it orders as SPIKE
        if len(binance_statuses) > 1 and "NEW" not in binance_statuses and "PARTIALLY_FILLED" not in binance_statuses:
            bot_db.mark_position(open_position["order_id"], "SPIKE")
            for order in martingale_open_orders:
                bot_db.mark_order(order["order_id"], "FILLED")
            bot_log.log_status(f"All're filled. Fast movement in both directions. Position: {open_position['order_id']}")
            continue

        need_to_increase = False
        # father proceeds if only one order is filled
        for bo in binance_orders:
            # 2.2.3 If closed position order is filled
            if open_position["side"] != bo["side"] and bo["status"] == 'FILLED':
                # update order and mark it as FILLED
                bot_db.update_position(bo, "FILLED")
                # mark position as FILLED
                bot_db.mark_position(open_position["order_id"], "CLOSED")
                # SNS "Position is closed"
                bot_log.log_status(f'Position {open_position["order_id"]} is closed!')

            # 2.2.4 If increase position order is filled
            if open_position["side"] == bo["side"] and bo["status"] == 'FILLED':
                # update order and mark it as FILLED
                bot_db.update_position(bo, "FILLED")
                # position is increased
                need_to_increase = True

            if bo["status"] != 'FILLED':
                # cancel this order
                print(f'Cancel order {bo["orderId"]} of {open_position["pair"]}')
                result = bot_client.client.cancel_order(symbol=open_position["pair"], orderId=bo["orderId"])
                bot_log.log_status(f"Cancel order: {result}")
                # mark it as EXPIRED
                bot_db.mark_order(bo["orderId"], "EXPIRED")

        # 2.2.5 Increasing position
        if need_to_increase:
            # martingale orders
            count_orders = bot_db.count_position_size(open_position["order_id"], open_position["side"])
            # add initial order
            pos_size = float(open_position["qty"]) + float(count_orders["base"])
            pos_quote = float(open_position["cummulative_quote_qty"]) + float(count_orders["quote"])

            # 2. Make a pair of orders to close/increase position
            try:
                # 2.1 Create current position meta-data and pass it to the PairOrders object
                # {pair, side, size of base asset, avg. price}
                current_position = {
                    "order_id": open_position["order_id"],
                    "pair": open_position["pair"],
                    "side": open_position["side"],
                    "size": pos_size,
                    "price": pos_quote / pos_size
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
                        raise NotEnoughFundsError(
                            "Something goes wrong! Not enough funds to place Close Position Order")

            except NotEnoughFundsError as ex:
                bot_log.log_status(ex)
                continue


except OrderRejected as ex:
    bot_log.log_status(ex)

except Exception as ex:
    bot_log.log_status(ex)

bot_log.log_status("Exit bot.")
"""
limit_order["initial_order_commission"] = sum(
    [float(fill['commission']) for fill in limit_order['fills']])
limit_order["initial_order_avg_price"] = float(limit_order['cummulativeQuoteQty']) / float(
    limit_order['executedQty'])

bot_log.log_status("Order. Pair: {}, Q: {}, avg price: {}, commission: {}, Fills: {}".
                   format(self.meta[info]["pair"],
                          self.meta[info]["size"],
                          limit_order["initial_order_avg_price"],
                          limit_order["initial_order_commission"],
                          limit_order['fills']
                          )
                   )

"""

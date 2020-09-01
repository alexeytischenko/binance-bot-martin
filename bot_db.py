import config
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine(config.db_bot2_url)
db = scoped_session(sessionmaker(bind=engine))


def update_position(order, status):
    """
    Updates order in 'martingale_order' table after it is filled
    """

    db.execute(
        "UPDATE martingale_order SET price=:price, qty=:qty, raworder=:raworder, commission=:commission, "
        "commission_asset=:commission_asset, cummulative_quote_qty=:cummulative_quote_qty, status=:status WHERE "
        "order_id=:order_id",
        {
            "order_id": order['orderId'],
            "qty": order['executedQty'],
            "price": order['price'],
            "raworder": "", # json.dumps(order['fills']),
            "commission": 0, # order["order_commission"],
            "commission_asset": "", # order['fills'][0]['commissionAsset'],
            "cummulative_quote_qty": 0, # order['cummulativeQuoteQty'],
            "status": status
        })
    db.commit()


def count_position_size(order_id, side):
    """
    Counts sum of all filled orders in the position, except initial

    Parameters:
        order_id (int): order_id in 'initial_order' table
        side (str): 'BUY', 'SELL'
    """
    return db.execute("SELECT SUM(qty) as base, SUM(qty*price) as quote FROM martingale_order WHERE "
                      "initial_order_id=:order_id AND side=:side AND status='FILLED' GROUP BY initial_order_id", {
                          "order_id": order_id,
                          "side": side
                      }).fetchone()


def mark_order(order_id, value):
    """
    Updates martingale_order with status=:value

    Parameters:
        order_id (int): order_id in 'initial_order' table
        value (str): 'ERROR', 'OPEN', 'FILLED'
    """

    db.execute("UPDATE martingale_order SET status = :status WHERE order_id = :order_id",
               {"order_id": order_id, "status": value})
    db.commit()


def mark_position(order_id, value):
    """
    Updates initial_order with position=:value

    Parameters:
        order_id (int): order_id in 'initial_order' table
        value (str): 'ERROR', 'OPEN', 'CLOSED'
    """

    db.execute("UPDATE initial_order SET position = :position WHERE order_id = :order_id",
               {"order_id": order_id, "position": value})
    db.commit()


def select_open_positions():
    """Select all open positions from 'initial_order' table"""
    return db.execute("SELECT * FROM initial_order WHERE position = 'OPEN'").fetchall()


def select_position_orders(initial_order_id, new=False):
    """Select all position orders from 'martingale_order' table

    Parameters:
        initial_order_id (int): order_id in 'initial_order' table
        new (bool): adds condition to the select query, whether or not status should be equal to 'NEW'

    Return:
        list: select query result
    """
    query = "SELECT * FROM martingale_order WHERE initial_order_id = :order_id"
    if new:
        query += " AND status = 'NEW'"
    return db.execute(query, {"order_id": initial_order_id}).fetchall()


def limit_order(order):
    """Records limit order info to the DB"""
    db.execute(
        "INSERT INTO martingale_order (initial_order_id, order_id, side, status, pair, transact_time, qty, price, "
        "raworder, commission, commission_asset, cummulative_quote_qty, type) VALUES (:initial_order_id, :order_id, "
        ":side, :status, :pair, to_timestamp(:transact_time), :qty, :price, :raworder, :commission, "
        ":commission_asset, :cummulative_quote_qty, :type)",
        {
            "order_id": order['orderId'],
            "initial_order_id": order['initial_order_id'],
            "side": order['side'],
            "status": order['status'],
            "pair": order['symbol'],
            "transact_time": str(order['transactTime'])[:-3],
            "qty": order['executedQty'],
            "price": '%.8f' % order["order_avg_price"],
            "raworder": json.dumps(order['fills']),
            "commission": '%.8f' % order["order_commission"],
            "commission_asset": "",
            "cummulative_quote_qty": order['cummulativeQuoteQty'],
            "type": 'LIMIT'
        })
    db.commit()


def initial_order(order):
    """Records initial market order info to the DB"""

    db.execute(
        "INSERT INTO initial_order (order_id, position, side, status, pair, transact_time, qty, price, raworder, "
        "commission, commission_asset, cummulative_quote_qty, type) VALUES (:order_id, :position, :side, :status, "
        ":pair, to_timestamp(:transact_time), :qty, :price, :raworder, :commission, :commission_asset, "
        ":cummulative_quote_qty, :type)",
        {
            "order_id": order['orderId'],
            "position": "OPEN",
            "side": order['side'],
            "status": order['status'],
            "pair": order['symbol'],
            "transact_time": str(order['transactTime'])[:-3],
            "qty": order['executedQty'],
            "price": '%.8f' % order["initial_order_avg_price"],
            "raworder": json.dumps(order['fills']),
            "commission": '%.8f' % order["initial_order_commission"],
            "commission_asset": order['fills'][0]['commissionAsset'],
            "cummulative_quote_qty": order['cummulativeQuoteQty'],
            "type": 'MARKET'
        })
    db.commit()

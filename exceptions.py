"""
Custom Exceptions
"""


class NotEnoughFundsError(Exception):
    """
    Insufficient funds to proceed
    """
    pass


class UnexpectedOrdersError(Exception):
    """
    Raises if there are wrong/unexpected orders in 'martingale_order' table
    """
    pass


class OrderRejected(Exception):
    """
    Raises if Binance order has any of the fallowing statuses: "CANCELED", "REJECTED", "EXPIRED"
    """
    pass
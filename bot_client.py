import binance.exceptions
from binance.client import Client
import config


# Create python-binance client
client = Client(config.api_key, config.api_secret)


def make_oco(**params):
    """Additional method to make OCO orders"""
    return client._post('order/oco', True, data=params)
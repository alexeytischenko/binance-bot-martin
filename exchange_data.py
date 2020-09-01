import json
import urllib.request


class ExchangeData:
    """
    This is a Singleton class for retrieving and processing exchange info.

    Attributes:
    info (dict): dict of assets pairs and their properties.
    """

    __instance = None
    info = {}

    @staticmethod
    def get_instance():
        """Static access method. """
        if ExchangeData.__instance is None:
            ExchangeData()

        return ExchangeData.__instance

    def __init__(self):
        """Class constructor"""
        # checks if instance already created
        if ExchangeData.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ExchangeData.__instance = self

        # receiving data
        print('Receiving exchange info from Binance...')
        url_address = 'https://api.binance.com/api/v1/exchangeInfo'
        with urllib.request.urlopen(url_address) as url:
            data = json.loads(url.read())
            # filling info with data, eg: 'PRICE_FILTER', 'LOT_SIZE', 'MIN_NOTIONAL', ocoAllowed etc
            # In BNBBTC pair BNB - base asset, BTC - quote asset
            for symbol in data['symbols']:
                self.info[symbol['symbol']] = {}
                self.info[symbol['symbol']]['ocoAllowed'] = symbol['ocoAllowed']
                self.info[symbol['symbol']]['base'] = symbol['baseAsset']
                self.info[symbol['symbol']]['quote'] = symbol['quoteAsset']
                self.info[symbol['symbol']]['baseAssetPrecision'] = symbol['baseAssetPrecision']
                self.info[symbol['symbol']]['quoteAssetPrecision'] = symbol['quoteAssetPrecision']
                for symbol_filter in symbol['filters']:
                    if symbol_filter['filterType'] in ['PRICE_FILTER', 'LOT_SIZE', 'MIN_NOTIONAL']:
                        self.info[symbol['symbol']][symbol_filter['filterType']] = symbol_filter

        # print(json.dumps(info))
        """
        "BNBBTC": {"ocoAllowed": true, "baseAssetPrecision": 8, "quoteAssetPrecision": 8, "PRICE_FILTER": {"filterType": "PRICE_FILTER", "minPrice": "0.00000010", "maxPrice": "100000.00000000", "tickSize": "0.00000010"}, "LOT_SIZE": {"filterType": "LOT_SIZE", "minQty": "0.01000000", "maxQty": "100000.00000000", "stepSize": "0.01000000"}, "MIN_NOTIONAL": {"filterType": "MIN_NOTIONAL", "minNotional": "0.00010000", "applyToMarket": true, "avgPriceMins": 5}}
        """

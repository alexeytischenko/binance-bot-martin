
Stupid Martingale bot. For goodness' sake don't use it!

### Exchange_info data

The **PRICE_FILTER** defines the price rules for a symbol. There are 3 parts:
*   minPrice defines the minimum price/stopPrice allowed; disabled on minPrice == 0.
*   maxPrice defines the maximum price/stopPrice allowed; disabled on maxPrice == 0.
*   tickSize defines the intervals that a price/stopPrice can be increased/decreased by; disabled on tickSize == 0.

Any of the above variables can be set to 0, which disables that rule in the price filter. In order to pass the price filter, the following must be true for price/stopPrice of the enabled rules:
*   price >= minPrice
*   price <= maxPrice
*   (price-minPrice) % tickSize == 0

_/exchangeInfo format:_\
_{\
  "filterType": "PRICE_FILTER",\
  "minPrice": "0.00000100",\
  "maxPrice": "100000.00000000",\
  "tickSize": "0.00000100"\
}_

The **MIN_NOTIONAL** filter defines the minimum notional value allowed for an order on a symbol. An order's notional value is the price * quantity. applyToMarket determines whether or not the MIN_NOTIONAL filter will also be applied to MARKET orders. Since MARKET orders have no price, the average price is used over the last avgPriceMins minutes. avgPriceMins is the number of minutes the average price is calculated over. 0 means the last price is used.

_/exchangeInfo format:_\
_{\
  "filterType": "MIN_NOTIONAL",\
  "minNotional": "0.00100000",\
  "applyToMarket": true,\
  "avgPriceMins": 5\
}_


The **LOT_SIZE** filter defines the quantity(aka "lots" in auction terms) rules for a symbol.There are 3 parts:
*   minQty defines the minimum quantity allowed.
*   maxQty defines the maximum quantity allowed.
*   stepSize defines the intervals that a quantity can be increased/decreased by.

In order to pass the lot size, the following must be true for quantity:
*   quantity >= minQty
*   quantity <= maxQty
*   (quantity-minQty) % stepSize == 0

_/exchangeInfo format:_\
_{\
  "filterType": "LOT_SIZE",\
  "minQty": "0.00100000",\
  "maxQty": "100000.00000000",\
  "stepSize": "0.00100000"\
}_

### Order statuses
NEW - The order has been accepted by the engine.\
PARTIALLY_FILLED - A part of the order has been filled.\
FILLED - The order has been completely filled.\
CANCELED - The order has been canceled by the user.\
PENDING_CANCEL (currently unused)\
REJECTED - The order was not accepted by the engine and not processed.\
EXPIRED - The order was canceled according to the order type's rules
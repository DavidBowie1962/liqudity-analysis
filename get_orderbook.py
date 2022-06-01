from datetime import datetime, timedelta
from tinkoff.invest import Client, RequestError, Order, OrderBook, GetOrderBookResponse
import creds
import pandas as pd



def hey():
    try:
        with Client(creds.token) as client:
            figi = 'BBG00QPYJ5H0'
            book = client.market_data.get_order_book(figi=figi, depth=30)
            #print(book)

            def cast_money(v):
                return (v.units + v.nano / 1e9)  # nano - 9 нулей

            fast_price_sell, fast_price_buy = book.asks[0], book.bids[0] # центр стакана, мин спред
            best_price_sell, best_price_buy = book.asks[-1], book.bids[-1]  # края стакана, макс спред
            print(fast_price_sell, fast_price_buy)
            print(best_price_sell, best_price_buy)
            #
            # # только для удобной отладки, в проде - лишнее
            bids = [cast_money(p.price) for p in book.bids] # покупатели
            asks = [cast_money(p.price) for p in book.asks] # продавцы
            print(bids, asks, sep="\n")





    except RequestError as e:
        print(str(e))
hey()
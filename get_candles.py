from datetime import datetime, timedelta

from pandas import DataFrame
from ta.trend import ema_indicator
from tinkoff.invest import Client, RequestError, CandleInterval, HistoricCandle
from tinkoff.invest.services import Services

from datetime import datetime, timedelta, date, time, timezone
from typing import Optional
#import converter as op
import creds
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.graph_objects as go


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)



def run():
    try:
        with Client(creds.token) as client:
            # could be changed for the needed period or figi
            figi = 'BBG004RVFCY3' # MGNT moex
            figi_spb = 'BBG000VFBQG4'# MGNT spb
            inp_time_fr = "2022-02-01"
            intp_time_to = "2022-02-25"


            # obtain useable form of money from candles
            def cast_money(v):
                return (v.units + v.nano / 1e9)  # nano - 9 нулей

            # obtain the usd exchange rate to convert rub to usd
            u = client.market_data.get_last_prices(figi=['USD000UTSTOM'])
            usdrur = cast_money(u.last_prices[0].price)

            # создать кастомный data frame для работы с данными
            def create_df_rub(candles: [HistoricCandle]):
                df = DataFrame([{
                    'time': c.time,
                    'volume': round(c.volume / usdrur, 2),
                    'open': round(cast_money(c.open) / usdrur, 2),
                    'close': round(cast_money(c.close) / usdrur, 2),
                    'high': round(cast_money(c.high) / usdrur, 2),
                    'low': round(cast_money(c.low) / usdrur, 2),
                } for c in candles])

                return df

            def create_df(candles: [HistoricCandle]):
                df = DataFrame([{
                    'time': c.time,
                    'volume': c.volume,
                    'open': cast_money(c.open),
                    'close': cast_money(c.close),
                    'high': cast_money(c.high),
                    'low': cast_money(c.low),
                } for c in candles])

                return df



            fr = datetime.strptime(inp_time_fr, "%Y-%m-%d")
            to = datetime.strptime(intp_time_to, "%Y-%m-%d")
            #fr = fr.replace(tzinfo=timezone.utc).timestamp()
            #to = to.replace(tzinfo=timezone.utc).timestamp()
            moex = pd.DataFrame(columns=['time', 'volume', 'open', 'close', 'high', 'low'])
            spb = pd.DataFrame(columns=['time', 'volume', 'open', 'close', 'high', 'low'])
            length = (to - fr) / 3
            day = length.days + 1

            # making dataset for moex
            for i in range(day):
                fr = fr
                t1 = fr + timedelta(days = 3)
                m = client.market_data.get_candles(
                    figi=figi,
                    from_=fr,
                    to=t1,
                    interval=CandleInterval.CANDLE_INTERVAL_HOUR
                )

                s = client.market_data.get_candles(
                    figi=figi_spb,
                    from_=fr,
                    to=t1,
                    interval=CandleInterval.CANDLE_INTERVAL_HOUR
                )
                fr = fr + timedelta(days=3)

                df = create_df_rub(m.candles)
                moex = pd.merge(left=moex, right=df, how='outer')

                df2 = create_df(s.candles)
                spb = pd.merge(left=spb, right=df2, how='outer')

            print(moex)
            print(spb)

            #moex.to_csv('mgnt_mx.csv', sep=',')
            #spb.to_csv('mgnt_sp.csv', sep=',')


    except RequestError as e:
        print(str(e))
run()
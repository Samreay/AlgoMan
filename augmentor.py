from pytrends.request import TrendReq
from pydispatch import dispatcher
from util.config import get_trade_coin_names
from util.util import chunks
import pandas as pd
from datetime import datetime, timedelta

class Augmentor(object):
    def __init__(self):
        dispatcher.connect(self.augment_data, signal="digested_data", sender=dispatcher.Any)

    def get_trends(self, date=None):
        # make this work for a given date
        if date is None:
            date = datetime.now()
        date_old = date  - timedelta(days=30)
        timeframe = '%s %s' % (date_old.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'))
        
        coins = get_trade_coin_names()
        datas = []
        for chunk in chunks(coins, 4):
            print("Getting trends for %s" % chunk)
            pytrends = TrendReq(hl='en-US', tz=360)
            kw_list = chunk
            pytrends.build_payload(kw_list, cat=0, timeframe=timeframe, geo='', gprop='')
            frame = pytrends.interest_over_time()
            frame.drop('isPartial', axis=1, inplace=True)
            datas.append(frame)
            
        data = pd.concat(datas, axis=1)
        print(data)
        return data
        
    def augment_data(self, message):
        print(message)

if __name__ == "__main__":
    a = Augmentor()
    t = a.get_trends()
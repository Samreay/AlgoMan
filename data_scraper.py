import time
from datetime import datetime
from config import get_client, get_trade_coins
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def get_info(client, symbols):
    depth_raw = {}
    tfhour = {}
    prices_raw = client.get_all_tickers()
    for s in symbols:
        print(s)
        depth_raw[s] = client.get_order_book(symbol=s, limit=100)
        time.sleep(0.1)
        tfhour[s] = client.get_ticker(symbol=s)
        time.sleep(0.1)
    return prices_raw, depth_raw, tfhour

if __name__ == "__main__":
    client = get_client()
    coins = get_trade_coins()
    symbols = [c + "BTC" for c in coins]

    while True:

        now = datetime.now()
        filename = now.isoformat().replace(":", "_")
        print(filename)
        try:
            prices_raw, depth_raw, tfhour = get_info(client, symbols)
            data = {"prices": prices_raw, "depth_raw": depth_raw, "time": filename, "tfhour": tfhour}
            with open("raw_data/%s.txt" % filename, "w") as f:
                json.dump(data, f, cls=DateTimeEncoder)
        except Exception as e:
            print(e)

        time.sleep(120)

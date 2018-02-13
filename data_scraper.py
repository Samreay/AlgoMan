import json
import time
from datetime import datetime

from pydispatch import dispatcher

from util.util import DateTimeEncoder
from util.config import get_client, get_trade_coins
from util.timer import RepeatedTimer


def get_info(client, symbols):
    depth_raw = {}
    tfhour = {}
    prices_raw = client.get_all_tickers()
    for s in symbols:
        print("Depth and ticker for %s" % s)
        depth_raw[s] = client.get_order_book(symbol=s, limit=100)
        time.sleep(0.1)
        tfhour[s] = client.get_ticker(symbol=s)
        time.sleep(0.1)
    return prices_raw, depth_raw, tfhour


def get_data(client, symbols):
    now = datetime.now()
    filename = now.isoformat().replace(":", "_")
    print("Polling Binance, at %s" % now.isoformat())
    try:
        prices_raw, depth_raw, tfhour = get_info(client, symbols)
        data = {"prices": prices_raw, "depth_raw": depth_raw, "time": filename, "tfhour": tfhour}
        with open("raw_data/%s.txt" % filename, "w") as f:
            json.dump(data, f, cls=DateTimeEncoder)
        dispatcher.send("raw_data", data=data)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    client = get_client()
    coins = get_trade_coins()
    symbols = [c + "BTC" for c in coins][:1]

    timer = RepeatedTimer(5, get_data, client, symbols)
    input("Press enter to terminate")
    timer.stop()

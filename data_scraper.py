import json
import time
from datetime import datetime
import requests
import gzip

from util.config import get_client, get_trade_coins
from util.timer import RepeatedTimer


def get_info(client, symbols):
    depth_raw = {}
    tfhour = {}
    trades_5m = {}
    trades_2h = {}
    recent = {}
    t = client.get_server_time()["serverTime"]
    prices_raw = client.get_all_tickers()
    for s in symbols:
        print("Depth and ticker for %s" % s)
        tfhour[s] = client.get_ticker(symbol=s)
        depth_raw[s] = client.get_order_book(symbol=s, limit=500)
        time.sleep(0.3)
        recent[s] = client.get_recent_trades(symbol=s, limit=100)
        time.sleep(0.3)
        trades_5m[s] = client.get_klines(symbol=s, interval="5m", limit=100)
        time.sleep(0.15)
        trades_2h[s] = client.get_klines(symbol=s, interval="2h", limit=100)
        time.sleep(0.15)
    return t, prices_raw, depth_raw, tfhour, trades_5m, trades_2h, recent


def get_data(client, symbols):
    now = datetime.now()
    print("Polling Binance, at %s" % now.isoformat())
    try:
        t, prices_raw, depth_raw, tfhour, trades_5m, trades_2h, recent = get_info(client, symbols)
    except Exception as e:
        print(e)
        return
    data = {
        "prices": prices_raw,
        "depth_raw": depth_raw,
        "time": t,
        "pctime": int(now.timestamp()),
        "tfhour": tfhour,
        "trades_5m": trades_5m,
        "trades_2h": trades_2h,
        "recent": recent
    }
    try:
        with gzip.open("raw_data/%s.txt.gzip" % t, "w") as f:
            s = json.dumps(data)
            f.write(s.encode('utf-8'))
    except Exception as e:
        print(e)
    try:
        requests.post("http://localhost:5000/api/add_raw_data", json=json.dumps(data, indent=2))
    except Exception as e:
        print(e)


if __name__ == "__main__":
    client = get_client()
    coins = get_trade_coins()
    symbols = [c + "BTC" for c in coins]

    timer = RepeatedTimer(300, get_data, client, symbols)
    input("Press enter to terminate")
    timer.stop()

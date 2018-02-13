from pydispatch import dispatcher
import numpy as np
import os
import json
import gzip
from scipy.interpolate import interp1d
from scipy.stats import binned_statistic


class RawDataDigester(object):
    def __init__(self, archive="raw_data", digested="digested_data", debug=False):
        self.archive = archive
        self.counter = 0
        self.debug = debug
        self.digested = digested
        dispatcher.connect(self.digest_raw, signal="raw_data", sender=dispatcher.Any)
        # self.digest_archive()

    def digest_raw(self, data):
        self.counter += 1
        data = json.loads(data)
        print("%d digestion for time %s" % (self.counter, data["time"]))
        symbols = list(data["tfhour"].keys())
        time = data["time"]
        
        x = []
        for s in symbols:
            tfhour = data["tfhour"][s]
            depth_raw = data["depth_raw"][s]
            trades = data["recent"][s]
            history_5m = data["trades_5m"][s]
            history_2h = data["trades_2h"][s]
            price = float(tfhour["lastPrice"])

            vals = self.digest_24hour(tfhour)
            digest_x, digest_y = self.digest_depth(price, depth_raw)
            kline_5m_x, kline_5m_y = self.digest_klines(history_5m)
            kline_2h_x, kline_2h_y = self.digest_klines(history_2h)
            recent = self.digest_recent(trades)
    
            x.append(np.concatenate((vals, digest_y, kline_5m_y, kline_2h_y, recent)))
        x = np.array(x).astype(np.float32)
        message = {"time": int(time), "data": x}
        try:
            filename = "%s.npy" % time
            np.save("%s/%s" % (self.digested, filename), x)
        except Exception as e:
            print(e)
        dispatcher.send(message=message, signal="digested_data")
        return x

    def digest_24hour(self, data):
        return [float(data["priceChangePercent"]), float(data["lowPrice"])/float(data["lastPrice"]), float(data["highPrice"])/float(data["lastPrice"]), float(data["quoteVolume"])]

    def digest_recent(self, trades, bins=50):
        data = np.array([[float(x["time"]), float(x["price"]), float(x["qty"])] for x in trades])
        
        times, prices, qty = data.T
        xs = np.arange(len(times))
        prices = 100 * (prices / prices[-1] - 1)
        
        hist1, bine, _ = binned_statistic(xs, prices * qty, statistic="sum", bins=bins)
        hist2, _, _ = binned_statistic(xs, qty, statistic="sum", bins=bine)
        hist3 = hist1 / hist2
        binc = 0.5 * (bine[:-1] + bine[1:])
        
        if self.debug:
            import matplotlib.pyplot as plt
            plt.plot(binc, hist3)

        return hist3

    def digest_klines(self, klines, bins=100):
        data = [[float(x[0]), 0.5 * (float(x[1]) + float(x[2]))] for x in klines]
        data = np.array(data)
        
        times = data[:, 0] - data[:, 0][-1]
        change = 100 * (data[:, 1] / data[:, 1][-1] - 1)
                
        hist, bine, _ = binned_statistic(times, change, bins=bins)
        binc = 0.5 * (bine[:-1] + bine[1:])

        mask = np.isfinite(hist)
        hist2 = hist[mask]
        binc2 = binc[mask]
        
        hist = interp1d(binc2, hist2)(binc)
        if self.debug:
            import matplotlib.pyplot as plt
            plt.plot(binc, hist)
        return binc, hist

    def digest_depth(self, price, depth):
        depth_norm = [(100 * float(row[0]) / price) - 100 for row in depth["bids"][::-1]] + [(100 * float(row[0]) / price) - 100 for row in depth["asks"]]
        depth_weight_bids = [float(row[1]) for row in depth["bids"]]
        depth_weight_asks = [float(row[1]) for row in depth["asks"]]
        depth_weight_bids_cumsum = np.cumsum(depth_weight_bids)
        depth_weight_asks_cumsum = np.cumsum(depth_weight_asks)
        depth_weights_cumsum = np.concatenate((depth_weight_bids_cumsum[::-1], depth_weight_asks_cumsum))
        
        x = depth_norm
        y = depth_weights_cumsum
        
        xnew = np.linspace(-3, 3, 61)
        ynew = interp1d(x, y, bounds_error=False, fill_value=(y[0], y[-1]))(xnew)
        ynew /= ynew.max()

        if self.debug:
            import matplotlib.pyplot as plt
            plt.plot(xnew, ynew)
            plt.xlabel("Percent")
            plt.ylabel("Depth")
        
        return xnew, ynew

    def digest_archive(self, limit=-1):
        files = sorted(os.listdir(self.archive))
        processed = []
        for file in files[:limit]:
            with gzip.open(self.archive + "/" + file, 'rb') as f:
                processed.append(self.digest_raw(f.read().decode('utf-8')))
        return processed

if __name__ == "__main__":
    r = RawDataDigester(debug=False)
    d = r.digest_archive(limit=-1)

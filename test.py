import numpy as np

from util.config import get_client

client = get_client()
prices_raw = client.get_all_tickers()

symbol = 'ETHBNB'
depth_raw = client.get_order_book(symbol=symbol, limit=500)


prices = {x["symbol"]: float(x["price"]) for x in prices_raw}

#%%
price = prices[symbol]
depth_norm = [(100 * float(row[0]) / price) - 100 for row in depth_raw["bids"][::-1]] + [(100 * float(row[0]) / price) - 100 for row in depth_raw["asks"]]
depth_weight_bids = [float(row[1]) for row in depth_raw["bids"]]
depth_weight_asks = [float(row[1]) for row in depth_raw["asks"]]
depth_weight_bids_cumsum = np.cumsum(depth_weight_bids)
depth_weight_asks_cumsum = np.cumsum(depth_weight_asks)
depth_weights = depth_weight_bids[::-1] + depth_weight_asks
depth_weights_cumsum = np.concatenate((depth_weight_bids_cumsum[::-1], depth_weight_asks_cumsum))

import matplotlib.pyplot as plt
plt.plot(depth_norm, depth_weights_cumsum)

import os
import numpy as np
from scipy.interpolate import interp1d
from util.config import get_trade_coins
from pydispatch import dispatcher


class DataStore(object):
    def __init__(self, digested_data="digested_data"):
        self.digested_data = digested_data
        self.current_augmented = {}
        self.prediction_times = [1, 2, 4, 8, 12, 24, 48]
        self.performance = None
        self.consolidate()
        dispatcher.connect(self.add_augmented_data, signal="augmented_data", sender=dispatcher.Any)

    def add_augmented_data(self, data, update=True):
        self.current_augmented.update(data)
        if update:
            self.performance = self.get_performance(self.current_augmented)
        return self.current_augmented

    def consolidate(self, limit=-1):
        files = sorted(os.listdir(self.digested_data))
        for file in files[:limit]:
            data = np.load(self.digested_data + "/" + file)
            time = int(file.replace(".npy", ""))
            self.add_augmented_data({time: data}, update=False)
        return self.add_augmented_data({})  # Triggers the update
    
    def get_performance(self, res):
        current_times = self.get_times()
        prices = {t: res[t][:, 0] for t in current_times}

        matched_times_array = [np.array(current_times) + hours * 3600000 for hours in self.prediction_times]
        indexes = np.arange(len(current_times))

        updated_res = {ct: {"data": res[ct].copy(), "performance": []} for ct in res.keys()}
        num_coins = prices[list(prices.keys())[0]].size
        for h, matched_times in zip(self.prediction_times, matched_times_array):
            lookup_indexes = interp1d(current_times, indexes, bounds_error=False)(matched_times)
            for ct, val in zip(current_times, lookup_indexes):
                if np.isnan(val):
                    updated_res[ct]["performance"].append([np.NaN] * num_coins)
                else:
                    lower = np.floor(val)
                    upper = np.ceil(val)
                    lower_weight = 1 - (val - lower)
                    upper_weight = 1 - lower_weight
                    lower_key = current_times[int(lower)]
                    upper_key = current_times[int(upper)]
                    prices_future = lower_weight * res[lower_key][:, 0] + upper_weight * res[upper_key][:, 0]
                    performance = 100 * (prices_future / prices[ct] - 1)
                    updated_res[ct]["performance"].append(performance)
                    
        for ct in current_times:
            updated_res[ct]["performance"] = np.array(updated_res[ct]["performance"])
        return updated_res

    def get_times(self):
        return sorted(list(self.current_augmented.keys()))

    def get_machine_learning_data(self):
        times = self.get_times()
        data = np.vstack(self.performance[t]["data"][:, 2:] for t in times)
        predictions = [np.hstack(self.performance[t]["performance"][i, :] for t in times) for i in range(len(self.prediction_times))]
        return data, predictions

    def get_ml_datasets(self, training=0.6, test=0.3):
        data, predictions = self.get_machine_learning_data()
        length = data.shape[0]
        index_training = int(np.floor(training * length))
        index_testing = int(np.floor((1 - test) * length))

        data_training = data[:index_training, :]
        predictions_training = [p[:index_training] for p in predictions]

        data_testing = data[index_testing:, :]
        predictions_testing = [p[index_testing:] for p in predictions]

        return data_training, predictions_training, data_testing, predictions_testing

    def get_performance_of_coin(self, symbol):
        coins = get_trade_coins()
        assert symbol in coins
        index = coins.index(symbol)
        times = self.get_times()
        perfs = np.array([self.performance[time]["performance"][:, index] for time in times])
        times = np.array(times)
        return times, perfs

    def plot_performance(self, symbol, hour=None, ax=None):
        times, perfs = self.get_performance_of_coin(symbol)
        import matplotlib.pyplot as plt
        if ax is None:
            fig, ax = plt.subplots()
        if hour is None:
            for i, row in enumerate(perfs.T):
                ax.plot(times, row, label="%d" % self.prediction_times[i])
        else:
            i = self.prediction_times.index(hour)
            ax.plot(times, perfs[:, i], label=hour)
        ax.legend()
        ax.set_ylabel("%s%%" % symbol)
                
if __name__ == "__main__":
    c = DataStore()
    #updated = c.get_performance(res)
    #c.plot_performance("LTC")
    #c.plot_performance("NEO")
    c.get_ml_datasets()
    
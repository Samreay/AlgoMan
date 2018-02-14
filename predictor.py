from sklearn.neural_network import MLPRegressor
import numpy as np
from data_store import DataStore


class Predictor(object):
    def __init__(self, data_store):
        self.data_store = data_store
        self.brain = MLPRegressor(hidden_layer_sizes=(200, 200, 300, 20), max_iter=2000)

    def train(self):
        d1, p1, d2, p2 = self.data_store.get_ml_datasets(training=0.5, test=0.4)

        mask = np.isfinite(p1[0])
        self.brain.fit(d1[mask, :], p1[0][mask])

        mask2 = np.isfinite(p2[0])
        tested = self.brain.predict(d2[mask2, :])
        diff = tested - p2[0][mask2]

        import matplotlib.pyplot as plt
        x = np.arange(tested.size)
        plt.hist(diff, bins=100, histtype='step', color='r')
        plt.hist(p2[0][mask2], bins=100, histtype='step', color='g')



if __name__ == "__main__":
    d = DataStore()
    p = Predictor(d)
    p.train()
# pattern_deviation.py
# This module implements pattern deviation models (e.g., Autoencoders).

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
import numpy as np

class PatternDeviation:
    def __init__(self, input_dim):
        input_layer = Input(shape=(input_dim,))
        encoded = Dense(64, activation='relu')(input_layer)
        encoded = Dense(32, activation='relu')(encoded)
        decoded = Dense(64, activation='relu')(encoded)
        decoded = Dense(input_dim, activation='sigmoid')(decoded)

        self.autoencoder = Model(input_layer, decoded)
        self.autoencoder.compile(optimizer='adam', loss='mse')

    def train_model(self, X_train, epochs=10):
        self.autoencoder.fit(X_train, X_train, epochs=epochs)

    def detect_deviation(self, X):
        reconstruction = self.autoencoder.predict(X)
        loss = np.mean(np.square(X - reconstruction), axis=1)
        return loss

if __name__ == "__main__":
    # Example usage
    X_train = np.random.rand(100, 20)  # Dummy data
    model = PatternDeviation(input_dim=20)
    model.train_model(X_train)
    deviations = model.detect_deviation(X_train)
    print(deviations)

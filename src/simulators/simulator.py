# simulator.py
# This module simulates electrical data and generates continuous data streams.

import numpy as np
import pandas as pd
import time

class ElectricalDataSimulator:
    def __init__(self, output_file):
        self.output_file = output_file

    def generate_data(self):
        while True:
            data = {
                'Voltage': np.random.uniform(220, 240),
                'Current': np.random.uniform(5, 15),
                'Power': np.random.uniform(1000, 3000),
                'Temperature': np.random.uniform(20, 80),
                'Leakage Current': np.random.uniform(0, 5),
                'Load Imbalance': np.random.uniform(0, 10),
                'Time': pd.Timestamp.now()
            }
            df = pd.DataFrame([data])
            df.to_csv(self.output_file, mode='a', header=False, index=False)
            time.sleep(1)

if __name__ == "__main__":
    simulator = ElectricalDataSimulator(output_file="data/simulated_data.csv")
    simulator.generate_data()

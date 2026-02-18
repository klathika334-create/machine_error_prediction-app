# fault_injection.py
# This module injects faults into the simulated data for testing purposes.

import numpy as np
import pandas as pd

class FaultInjectionEngine:
    def __init__(self, data_file):
        self.data_file = data_file

    def inject_faults(self):
        data = pd.read_csv(self.data_file)
        fault_types = ['Overload', 'Loose Connection', 'Insulation Degradation', 'Earth Leakage', 'Short Circuit', 'Aging Wire']
        
        # Inject faults randomly
        for index, row in data.iterrows():
            if np.random.rand() < 0.1:  # 10% chance to inject a fault
                fault = np.random.choice(fault_types)
                data.at[index, 'Fault'] = fault

        # Save the data with faults
        data.to_csv(self.data_file, index=False)

if __name__ == "__main__":
    fault_injector = FaultInjectionEngine(data_file="data/simulated_data.csv")
    fault_injector.inject_faults()

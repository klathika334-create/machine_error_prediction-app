# prevention_engine.py
# This module continuously evaluates system health and generates preventive alerts.

import pandas as pd

class DailyPreventionEngine:
    def __init__(self, data_file):
        self.data_file = data_file

    def evaluate_health(self):
        data = pd.read_csv(self.data_file)
        alerts = []

        for index, row in data.iterrows():
            if row['Temperature'] > 70:
                alerts.append("Overheating trend detected.")
            if row['Leakage Current'] > 3:
                alerts.append("Possible earth leakage detected.")

        return alerts

if __name__ == "__main__":
    prevention_engine = DailyPreventionEngine(data_file="data/simulated_data.csv")
    alerts = prevention_engine.evaluate_health()
    for alert in alerts:
        print(alert)

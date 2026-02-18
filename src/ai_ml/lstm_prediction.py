# lstm_prediction.py
# This module analyzes the dataset and creates a prediction algorithm using LSTM.

import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

class LSTMPrediction:
    def __init__(self, file_path=None):
        # Use absolute path if not provided
        if file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.file_path = os.path.join(os.path.dirname(base_dir), 'data', 'Industrial_MultiClass_Dataset_With_Slip.xlsx')
        else:
            self.file_path = file_path
        self.scaler = MinMaxScaler()
        self.model = None

    def load_and_preprocess_data(self):
        # Load the dataset
        data = pd.read_excel(self.file_path)

        # Use 'Fault_Type' as the target column and include 'Combination' for mapping
        self.features = data.drop(columns=['Fault_Type', 'Combination']).values
        self.target = data['Fault_Type'].astype('category').cat.codes.values

        # Save the mapping of target codes to fault types and combinations
        self.target_mapping = data[['Fault_Type', 'Combination']].drop_duplicates()
        self.target_mapping['Fault_Code'] = self.target_mapping['Fault_Type'].astype('category').cat.codes

        # Normalize the features
        self.features = self.scaler.fit_transform(self.features)

        # Reshape for LSTM input (samples, timesteps, features)
        self.features = self.features.reshape((self.features.shape[0], 1, self.features.shape[1]))

    def build_model(self):
        # Define the LSTM model
        self.model = Sequential([
            LSTM(50, activation='relu', input_shape=(self.features.shape[1], self.features.shape[2])),
            Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mse')

    def train_model(self, epochs=10):
        # Train the model
        self.model.fit(self.features, self.target, epochs=epochs, verbose=1)

    def predict(self, new_data):
        # Preprocess new data
        new_data = self.scaler.transform(new_data)
        new_data = new_data.reshape((new_data.shape[0], 1, new_data.shape[1]))
        return self.model.predict(new_data)

    def get_fault_details(self, prediction):
        # Map the prediction to fault type and combination
        fault_code = int(round(prediction[0][0]))
        fault_row = self.target_mapping[self.target_mapping['Fault_Code'] == fault_code]
        if not fault_row.empty:
            fault_type = fault_row['Fault_Type'].values[0]
            combination = fault_row['Combination'].values[0]
            return fault_type, combination
        return "Unknown", "Unknown"

if __name__ == "__main__":
    # Example usage
    lstm_predictor = LSTMPrediction(file_path="data/Industrial_MultiClass_Dataset_With_Slip.xlsx")
    lstm_predictor.load_and_preprocess_data()
    lstm_predictor.build_model()
    lstm_predictor.train_model(epochs=10)

    # Example prediction
    sample_data = np.random.rand(1, lstm_predictor.features.shape[2])  # Dummy data
    prediction = lstm_predictor.predict(sample_data)
    fault_type, combination = lstm_predictor.get_fault_details(prediction)
    print("Prediction:", prediction)
    print("Fault Type:", fault_type)
    print("Combination:", combination)

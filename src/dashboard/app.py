





# app.py
# This module serves the web-based dashboard for real-time visualization and system insights.

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
import os


# For local execution, use relative import
from ai_ml.lstm_prediction import LSTMPrediction
# from src.ai_ml.anomaly_detection import AnomalyDetection  # imported only if needed
# from src.ai_ml.pattern_deviation import PatternDeviation  # imported only if needed

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
app.config['MONGO_URI'] = 'mongodb://localhost:27017/machine_error_db'
mongo = PyMongo(app)

base_dir = os.path.dirname(os.path.abspath(__file__))
lstm_data_path = os.path.join(os.path.dirname(os.path.dirname(base_dir)), 'data', 'Industrial_MultiClass_Dataset_With_Slip.xlsx')
lstm_predictor = LSTMPrediction(file_path=lstm_data_path)
lstm_predictor.load_and_preprocess_data()
lstm_predictor.build_model()

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session.get('username'), role=session.get('role'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = mongo.db.users
        user = users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user.get('role', 'user')
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        role = request.form.get('role', 'user')
        if password != confirm:
            return render_template('signup.html', error='Passwords do not match')
        users = mongo.db.users
        if users.find_one({'username': username}):
            return render_template('signup.html', error='Username already exists')
        pw_hash = generate_password_hash(password)
        users.insert_one({'username': username, 'password': pw_hash, 'role': role})
        return render_template('signup.html', success='User created successfully! Please log in.')
    return render_template('signup.html')

# Load dataset globally for streaming
try:
    df_dataset = pd.read_excel(lstm_data_path)
    print(f"Dataset loaded successfully: {len(df_dataset)} rows")
except Exception as e:
    print(f"Error loading dataset: {e}")
    df_dataset = pd.DataFrame()

CURRENT_INDEX = 0

@app.route('/api/random-data')
def random_data():
    global CURRENT_INDEX
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        if df_dataset.empty:
            return jsonify({'error': 'Dataset not loaded'}), 500

        # Get sequential chunk
        chunk_size = 20
        start_idx = CURRENT_INDEX
        end_idx = start_idx + chunk_size
        
        # Handle wrapping around
        if end_idx >= len(df_dataset):
            subset = df_dataset.iloc[start_idx:]
            remaining = chunk_size - len(subset)
            subset_start = df_dataset.iloc[:remaining]
            data_chunk = pd.concat([subset, subset_start])
            CURRENT_INDEX = remaining
        else:
            data_chunk = df_dataset.iloc[start_idx:end_idx]
            CURRENT_INDEX = end_idx

        # Convert to list of dicts for JSON response
        # Ensure we replace NaN with None or handle them, ensuring valid JSON
        data_list = data_chunk.replace({np.nan: None}).to_dict(orient='records')
        
        return jsonify(data_list)
        
    except Exception as e:
        import traceback
        print('Error in /api/random-data:', e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/prediction-details')
def prediction_details():
    if 'username' not in session:
        return redirect(url_for('login'))

    # LSTM Prediction sample
    try:
        sample_data = np.random.rand(1, lstm_predictor.features.shape[2])
        lstm_pred = lstm_predictor.predict(sample_data)
        fault_type, combination = lstm_predictor.get_fault_details(lstm_pred)
        lstm_result = {
            'prediction': str(lstm_pred[0][0]),
            'fault_type': fault_type,
            'combination': combination
        }
    except Exception as e:
        lstm_result = {'prediction': 'N/A', 'fault_type': 'N/A', 'combination': 'N/A'}

    # Anomaly Detection sample (only if data/simulated_data.csv exists)
    anomaly_result = None
    anomaly_path = os.path.join('data', 'simulated_data.csv')
    if os.path.exists(anomaly_path):
        try:
            from src.ai_ml.anomaly_detection import AnomalyDetection
            ad = AnomalyDetection(data_file=anomaly_path)
            # Use random data for demonstration or real prediction if implemented
            anomaly_result = ad.detect()
        except Exception as e:
            anomaly_result = {'error': str(e)}

    # Pattern Deviation sample (if implemented)
    pattern_result = None
    try:
        from src.ai_ml.pattern_deviation import PatternDeviation
        pdv = PatternDeviation()
        pattern_result = pdv.detect()
    except Exception as e:
        pattern_result = {'error': str(e)}

    return render_template('prediction_details.html', lstm=lstm_result, anomaly=anomaly_result, pattern=pattern_result, username=session.get('username'), role=session.get('role'))


# Information page route
@app.route('/information')
def information():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('information.html', username=session.get('username'), role=session.get('role'))

# Add additional routes for user management, charts, etc. as needed









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
from ai_ml.anomaly_detection import AnomalyDetection
from ai_ml.pattern_deviation import PatternDeviation

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

# Initialize AI models
anomaly_detector = AnomalyDetection(data_file=None)
pattern_deviation_model = None

if not df_dataset.empty:
    # 1. Anomaly Detection
    try:
        anomaly_detector.train_model(df_dataset)
        print("Anomaly Detection model trained.")
    except Exception as e:
        print(f"Error training Anomaly Detection: {e}")

    # 2. Pattern Deviation
    try:
        cols_to_drop = ['Fault', 'Time', 'Fault_Type', 'Combination']
        existing_cols_to_drop = [c for c in cols_to_drop if c in df_dataset.columns]
        pattern_features = df_dataset.drop(columns=existing_cols_to_drop).select_dtypes(include=[float, int]).fillna(0)
        input_dim = pattern_features.shape[1]
        pattern_deviation_model = PatternDeviation(input_dim=input_dim)
        # Train briefly for demo
        pattern_deviation_model.train_model(pattern_features, epochs=1)
        print("Pattern Deviation model trained.")
    except Exception as e:
        print(f"Error training Pattern Deviation: {e}")

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
        
        # Check for faults and generate explanation
        from genai.explanation import generate_explanation
        
        # Look for the last non-normal fault in the chunk
        latest_fault = None
        for row in reversed(data_list):
            fault_type = row.get('Fault_Type', 'Normal')
            combination = row.get('Combination', '-')
            
            # Check if it's a fault (adjust conditions based on actual dataset values)
            if fault_type not in ['Normal', 'No Fault', '-'] or (combination != '-' and combination != 'Normal'):
                latest_fault = fault_type if fault_type not in ['Normal', 'No Fault', '-'] else combination
                break
        
        explanation = None
        if latest_fault:
            explanation = generate_explanation(latest_fault)
            
        # Add explanation to the response (can be added to the last item or as a separate field if we change structure, 
        # but to keep it simple let's append it to the last item as metadata or wrapping)
        
        # Better approach: Return object with data and metadata, BUT frontend expects list.
        # So we will add 'explanation' field to the last item in the list.
        if data_list and explanation:
            data_list[-1]['explanation'] = explanation
            data_list[-1]['fault_detected'] = latest_fault

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
    
    # Generate/Get data for views
    
    # 1. Anomaly Data
    anomaly_data = {'status': 'Unknown', 'output': 'Model not ready'}
    if not df_dataset.empty:
        try:
            sample = df_dataset.sample(1)
            cols_to_drop = ['Fault', 'Time', 'Fault_Type', 'Combination']
            existing_cols_to_drop = [c for c in cols_to_drop if c in sample.columns]
            features = sample.drop(columns=existing_cols_to_drop).select_dtypes(include=[float, int]).fillna(0)
            
            pred = anomaly_detector.predict_anomalies(features)
            status = "Normal" if pred[0] == 1 else "Anomaly"
            anomaly_data = {'status': status, 'output': f"Score: {pred[0]} (Simulated)"}
        except Exception as e:
            anomaly_data = {'status': 'Error', 'output': str(e)}

    # 2. LSTM Data
    lstm_data = {'prediction': 'N/A', 'fault_type': 'N/A', 'combination': 'N/A'}
    if not df_dataset.empty and lstm_predictor.model:
        try:
            # Re-using the same sample logic often makes sense, but LSTMPrediction needs specific shape
            # LSTMPrediction.predict expects (n_samples, n_features) before own preprocessing?
            # actually lstm_predictor.predict calls scaler.transform(new_data)
            # define features for LSTM (exclude target)
            sample_lstm = sample.drop(columns=['Fault_Type', 'Combination'])
            # We need to ensure columns match what scaler expects. 
            # scaler was fit on data.drop(columns=['Fault_Type', 'Combination']).values
            # So sample_lstm.values should work if columns order is preserved (usually is)
            
            prediction = lstm_predictor.predict(sample_lstm.values)
            # prediction is raw value?
            # get_fault_details expects prediction array
            # But wait, lstm_predictor.predict returns model.predict
            # and get_fault_details wraps logic
            
            # The get_fault_details logic in LSTMPrediction seems to assume prediction is a value close to a class index?
            # "fault_code = int(round(prediction[0][0]))"
            
            fault_type, combination = lstm_predictor.get_fault_details(prediction)
            
            lstm_data = {
                'prediction': str(prediction[0][0]),
                'fault_type': fault_type,
                'combination': combination
            }
        except Exception as e:
            lstm_data['prediction'] = f"Error: {str(e)}"

    # 3. Pattern Data
    pattern_data = {'deviation': 'N/A'}
    if pattern_deviation_model and not df_dataset.empty:
        try:
             # Use same features as anomaly for consistency (numeric)
             deviation = pattern_deviation_model.detect_deviation(features)
             pattern_data = {'deviation': f"{deviation[0]:.4f}"}
        except Exception as e:
             pattern_data['deviation'] = f"Error: {str(e)}"

    return render_template('prediction_details.html', 
                           username=session.get('username'),
                           role=session.get('role', 'user'),
                           anomaly=anomaly_data,
                           lstm=lstm_data,
                           pattern=pattern_data)

# ── In-memory solutions history ──
solutions_history = []
MAX_SOLUTIONS = 50

@app.route('/api/fault-alert')
def fault_alert():
    """Run LSTM prediction on a random sample, generate AI solution, return alert data."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        if df_dataset.empty or lstm_predictor.model is None:
            return jsonify({'alert': False, 'message': 'Model not ready'}), 200
        
        # Sample a random row
        sample = df_dataset.sample(1)
        
        # LSTM prediction
        sample_features = sample.drop(columns=['Fault_Type', 'Combination'])
        prediction = lstm_predictor.predict(sample_features.values)
        fault_type, combination = lstm_predictor.get_fault_details(prediction)
        
        # Also get the actual fault from the sampled row for comparison
        actual_fault = sample['Fault_Type'].values[0]
        actual_combo = sample['Combination'].values[0]
        
        # Use the LSTM-predicted fault for the solution
        # If the predicted fault is unknown/normal, fall back to actual
        display_fault = fault_type if fault_type not in ['Unknown', 'Normal', 'No Fault'] else actual_fault
        display_combo = combination if combination not in ['Unknown', '-'] else actual_combo
        
        is_fault = display_fault not in ['Normal', 'No Fault', 'Unknown', '-', '']
        
        from genai.explanation import generate_solution
        
        if is_fault:
            solution = generate_solution(display_fault, display_combo)
            
            # Store in history (cap at MAX_SOLUTIONS)
            solutions_history.insert(0, solution)
            if len(solutions_history) > MAX_SOLUTIONS:
                solutions_history.pop()
            
            return jsonify({
                'alert': True,
                'fault_type': display_fault,
                'combination': display_combo,
                'severity': solution['severity'],
                'subject': solution['subject'],
                'body': solution['body'],
                'timestamp': solution['timestamp'],
                'prediction_raw': float(prediction[0][0])
            })
        else:
            return jsonify({
                'alert': False,
                'fault_type': display_fault,
                'combination': display_combo,
                'message': 'System operating normally',
                'timestamp': __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/solutions')
def get_solutions():
    """Return the solutions history as JSON."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(solutions_history)

@app.route('/api/solutions/clear', methods=['POST'])
def clear_solutions():
    """Clear the solutions history."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    solutions_history.clear()
    return jsonify({'status': 'cleared'})

# Add additional routes for user management, charts, etc. as needed



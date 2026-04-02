





# app.py
# This module serves the web-based dashboard for real-time visualization and system insights.

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()


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

# Global AI Settings (In-memory for session)
ai_settings = {
    'gemini_insights': True,
    'gemini_solutions': True
}

def init_db():
    """Ensure essential users exist on start."""
    with app.app_context():
        try:
            users = mongo.db.users
            if not users.find_one({'username': 'admin'}):
                users.insert_one({
                    'username': 'admin',
                    'password': generate_password_hash('admin123'),
                    'role': 'admin',
                    'login_count': 0,
                    'last_login': None
                })
                print("[DB] Default admin user initialized (admin/admin123).")
        except Exception as e:
            print(f"[DB] Error initializing users: {e}")

init_db()

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('intro'))
    return render_template('index.html', username=session.get('username'), role=session.get('role'))

@app.route('/intro')
def intro():
    return render_template('intro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            username = request.form['username'].strip()
            password = request.form['password'].strip()
            users = mongo.db.users
            user = users.find_one({'username': username})
            
            if user and check_password_hash(user['password'], password):
                session['username'] = username
                session['role'] = user.get('role', 'user')
                
                # Track login stats
                users.update_one({'_id': user['_id']}, {
                    '$inc': {'login_count': 1},
                    '$set': {'last_login': datetime.now()}
                })
                
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Invalid username or password.')
        except Exception as e:
            print(f"[Login Error] {e}")
            return render_template('login.html', error='System error during login. Please try again later.')
    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Fetch fresh user data for stats
    user = mongo.db.users.find_one({'username': session['username']})
    
    return render_template('profile.html', 
        username=session.get('username'), 
        role=session.get('role', 'user'),
        login_count=user.get('login_count', 0),
        last_login=user.get('last_login', 'Never'),
        last_logout=user.get('last_logout', 'Never')
    )

@app.route('/logout')
def logout():
    # Track logout time
    if 'username' in session:
        mongo.db.users.update_one({'username': session['username']}, {
            '$set': {'last_logout': datetime.now()}
        })
        
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

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Manage global AI settings."""
    global ai_settings
    if request.method == 'POST':
        try:
            data = request.get_json()
            if 'gemini_insights' in data:
                ai_settings['gemini_insights'] = bool(data['gemini_insights'])
            if 'gemini_solutions' in data:
                ai_settings['gemini_solutions'] = bool(data['gemini_solutions'])
            return jsonify({'success': True, 'settings': ai_settings})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400
    return jsonify(ai_settings)

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
MAX_SOLUTIONS = 15

# ── Rate limiting: max 6 alerts per minute ──
import time as _time
alert_timestamps = []  # timestamps of recent alerts
MAX_ALERTS_PER_MINUTE = 5

# ── Email configuration (saves to Gmail Drafts via IMAP) ──
import imaplib
import uuid
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email_draft(solution):
    """Save a solution as a draft in Gmail's Drafts folder via IMAP.
    The draft has no 'To' field so the user can add recipients later.
    Returns the direct link to the draft if successful, False otherwise."""
    email_user = os.environ.get('EMAIL_ADDRESS', '')
    email_pass = os.environ.get('EMAIL_APP_PASSWORD', '')
    imap_server = os.environ.get('EMAIL_IMAP_SERVER', 'imap.gmail.com')
    imap_port = int(os.environ.get('EMAIL_IMAP_PORT', '993'))
    
    if not email_user or not email_pass:
        print('[EMAIL] Skipping — EMAIL_ADDRESS or EMAIL_APP_PASSWORD not set in .env')
        return False
    
    try:
        # Generate a unique ID to find this exact message later
        draft_uuid = str(uuid.uuid4())
        
        # Build the email (no To: field — user adds recipients later)
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['Subject'] = solution['subject']
        
        # Add CC recipients if configured
        cc_emails = os.environ.get('EMAIL_CC_RECIPIENTS', '')
        if cc_emails:
            # Clean up the list (remove extra spaces)
            cc_list = [addr.strip() for addr in cc_emails.split(',') if addr.strip()]
            if cc_list:
                msg['Cc'] = ', '.join(cc_list)
        
        msg['X-Auris-Draft-ID'] = draft_uuid  # Custom header for search
        msg.attach(MIMEText(solution['body'], 'plain'))
        
        # Connect via IMAP and save to Drafts
        imap = imaplib.IMAP4_SSL(imap_server, imap_port)
        imap.login(email_user, email_pass)
        
        # Select Drafts folder (required for append? Standard IMAP append takes mailbox name, 
        # but we need to select it for searching anyway)
        # Gmail uses '[Gmail]/Drafts'
        imap.append('[Gmail]/Drafts', '', imaplib.Time2Internaldate(imaplib.time.time()), msg.as_bytes())
        
        # Now find the message to get its Thread ID (so we can link to it)
        imap.select('[Gmail]/Drafts')
        # Search by our unique header
        typ, data = imap.search(None, f'(HEADER X-Auris-Draft-ID "{draft_uuid}")')
        
        draft_link = None
        if typ == 'OK' and data[0]:
            # Get the last message ID found (should be unique anyway)
            msg_id = data[0].split()[-1]
            # Fetch X-GM-THRID (Gmail extension for Thread ID)
            typ, msg_data = imap.fetch(msg_id, '(X-GM-THRID)')
            if typ == 'OK':
                # Response format: b'seq (X-GM-THRID 123456789...)'
                # Parse to extract ID
                raw_resp = msg_data[0]
                if isinstance(raw_resp, tuple):
                    raw_resp = raw_resp[0] # The string part
                
                resp_str = raw_resp.decode('utf-8')
                match = re.search(r'X-GM-THRID\s+(\d+)', resp_str)
                if match:
                    thread_id = int(match.group(1))
                    # Gmail URL uses hex version of thread ID
                    hex_thread_id = hex(thread_id)[2:] # remove 0x prefix
                    draft_link = f'https://mail.google.com/mail/u/0/#drafts/{hex_thread_id}'
        
        imap.logout()
        
        if draft_link:
            print(f'[EMAIL] Draft saved & linked: {solution["subject"][:60]}...')
            return draft_link
        else:
            print(f'[EMAIL] Draft saved (link not generated): {solution["subject"][:60]}...')
            return True # Fallback to True if link generation fails but save succeeded

    except Exception as e:
        print(f'[EMAIL] Failed to save draft: {e}')
        return False

@app.route('/api/fault-alert')
def fault_alert():
    """Run LSTM prediction on a random sample, generate AI solution, return alert data."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        if df_dataset.empty or lstm_predictor.model is None:
            return jsonify({'alert': False, 'message': 'Model not ready'}), 200
        
        # ── Rate limiting: max 6 alerts per minute ──
        now = _time.time()
        # Remove timestamps older than 60 seconds
        while alert_timestamps and alert_timestamps[0] < now - 60:
            alert_timestamps.pop(0)
        
        if len(alert_timestamps) >= MAX_ALERTS_PER_MINUTE:
            return jsonify({
                'alert': False,
                'rate_limited': True,
                'message': f'Rate limit reached ({MAX_ALERTS_PER_MINUTE}/min). Next alert available in {int(60 - (now - alert_timestamps[0]))}s',
                'timestamp': __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Sample a random row — prefer fault rows for alert variety
        # Try up to 5 samples to find a non-normal row
        sample = None
        for _ in range(5):
            candidate = df_dataset.sample(1)
            if str(candidate['Fault_Type'].values[0]).strip() not in ['Normal Operation', 'Normal', 'No Fault', '-']:
                sample = candidate
                break
        if sample is None:
            sample = df_dataset.sample(1)

        # Get actual fault directly from the dataset row (ground truth)
        actual_fault = str(sample['Fault_Type'].values[0]).strip()
        actual_combo = str(sample['Combination'].values[0]).strip()

        # LSTM prediction for raw value reference only
        try:
            sample_features = sample.drop(columns=['Fault_Type', 'Combination'])
            prediction = lstm_predictor.predict(sample_features.values)
            prediction_raw = float(prediction[0][0])
        except Exception:
            prediction_raw = 0.0

        # Use actual dataset fault — this guarantees all 23 fault types can appear
        display_fault = actual_fault
        display_combo = actual_combo if actual_combo not in ['-', ''] else 'N/A'

        is_fault = display_fault not in ['Normal Operation', 'Normal', 'No Fault', 'Unknown', '-', '']
        
        from genai.explanation import generate_solution_with_ai

        if is_fault:
            # Extract live sensor readings from the sample row for AI context
            sensor_cols = ['Voltage (V)', 'Current (A)', 'Power (kW)', 'Temperature (\u00b0C)',
                           'Vibration (mm/s)', 'Speed (RPM)', 'Slip', 'Power Factor']
            sensor_readings = {}
            for col in sensor_cols:
                if col in sample.columns:
                    val = sample[col].values[0]
                    if val is not None and str(val) != 'nan':
                        sensor_readings[col] = round(float(val), 3)

            # Always prefer Gemini AI for quality drafts, even in Silent Mode
            try:
                solution = generate_solution_with_ai(display_fault, display_combo, sensor_readings)
            except Exception as e:
                print(f"[Gemini] Error generating AI solution: {e}")
                from genai.explanation import generate_solution
                solution = generate_solution(display_fault, display_combo)
                solution['ai_generated'] = False
            
            # AI setting toggle only controls the visual interruption (notification)
            solution['silent_mode'] = not ai_settings.get('gemini_solutions', True)
            
            # Record this alert timestamp
            alert_timestamps.append(now)
            
            # Store in history (cap at MAX_SOLUTIONS = 15)
            solutions_history.insert(0, solution)
            while len(solutions_history) > MAX_SOLUTIONS:
                solutions_history.pop()
            
            # Always send email draft (even if solutions toggled OFF, it acts as a background log)
            email_link = send_email_draft(solution)
            solution['email_link'] = email_link if isinstance(email_link, str) else None
            solution['email_sent'] = bool(email_link)
            
            return jsonify({
                'alert': True,
                'fault_type': display_fault,
                'combination': display_combo,
                'severity': solution['severity'],
                'subject': solution['subject'],
                'body': solution['body'],
                'timestamp': solution['timestamp'],
                'prediction_raw': prediction_raw,
                'ai_generated': solution.get('ai_generated', False),
                'show_frontend_notification': ai_settings.get('gemini_solutions', True),
                'email_sent': bool(email_link),
                'email_link': solution['email_link'],
                'alerts_remaining': MAX_ALERTS_PER_MINUTE - len(alert_timestamps)
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

@app.route('/api/report')
def generate_report():
    if 'username' not in session:
        return redirect(url_for('login'))

    period = request.args.get('period', 'monthly')
    plant = request.args.get('plant', 'all')

    if df_dataset.empty:
        return jsonify({'error': 'Dataset not loaded'}), 500

    # Build stats for Gemini
    metrics = ['Voltage (V)', 'Current (A)', 'Power (kW)', 'Temperature (\u00b0C)',
               'Vibration (mm/s)', 'Speed (RPM)', 'Slip', 'Power Factor']
    metric_averages = {}
    for m in metrics:
        if m in df_dataset.columns:
            val = pd.to_numeric(df_dataset[m], errors='coerce').mean()
            if not pd.isna(val):
                metric_averages[m] = val

    fault_counts = {}
    if 'Fault_Type' in df_dataset.columns:
        for f, c in df_dataset['Fault_Type'].value_counts().items():
            if f not in ['Normal Operation', 'Normal', 'No Fault', '-']:
                fault_counts[str(f)] = int(c)

    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Try Gemini AI report first
    try:
        from genai.chatbot import generate_ai_report
        report_data = {
            'period': period,
            'plant': 'All Plants' if plant == 'all' else plant.capitalize(),
            'total_records': len(df_dataset),
            'generated_at': generated_at,
            'metric_averages': metric_averages,
            'fault_counts': fault_counts
        }
        ai_report = generate_ai_report(report_data)
        if ai_report:
            header = (
                f"AURISPOWER AI-POWERED SYSTEM REPORT\n"
                f"\u2728 Generated by Gemini AI\n"
                f"Period: {period.capitalize()} | Plant: {'All Plants' if plant == 'all' else plant.capitalize()}\n"
                f"Generated on: {generated_at}\n"
                f"Total Records Analyzed: {len(df_dataset)}\n"
                f"{'='*60}\n\n"
            )
            full_report = header + ai_report
            from flask import Response
            return Response(
                full_report,
                mimetype='text/plain',
                headers={'Content-disposition': f'attachment; filename=aurispower_{period}_ai_report.txt'}
            )
    except Exception as e:
        print(f'[Gemini] Report generation failed, using standard: {e}')

    # Standard fallback report
    report_lines = [
        f"AURISPOWER System Report",
        f"Period: {period.capitalize()}",
        f"Plant: {'All Plants' if plant == 'all' else plant.capitalize()}",
        f"Generated on: {generated_at}",
        f"-" * 50,
        f"Total Records Analyzed: {len(df_dataset)}",
        f"\n=== Average Metrics ==="
    ]
    for m, v in metric_averages.items():
        report_lines.append(f"{m}: {v:.4f}")
    report_lines.append("\n=== Fault Instances ===")
    for f, c in fault_counts.items():
        report_lines.append(f"{f}: {c}")

    from flask import Response
    return Response(
        "\n".join(report_lines),
        mimetype='text/plain',
        headers={'Content-disposition': f'attachment; filename=aurispower_{period}_report.txt'}
    )


@app.route('/api/chat', methods=['POST'])
def api_chat():
    """Gemini-powered conversational chatbot endpoint."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    try:
        data = request.get_json(force=True)
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400

        # Build context: recent fault history
        fault_history = [
            {
                'fault_type': s.get('fault_type', 'Unknown'),
                'severity': s.get('severity', '?'),
                'combination': s.get('combination', '-'),
                'timestamp': s.get('timestamp', '')
            }
            for s in solutions_history[:5]
        ]

        # Latest sensor snapshot from dataset
        sensor_snapshot = None
        if not df_dataset.empty:
            latest = df_dataset.iloc[-1]
            sensor_cols = ['Voltage (V)', 'Current (A)', 'Power (kW)', 'Temperature (\u00b0C)',
                           'Vibration (mm/s)', 'Speed (RPM)', 'Slip', 'Power Factor']
            sensor_snapshot = {
                col: round(float(latest[col]), 2)
                for col in sensor_cols
                if col in df_dataset.columns and str(latest[col]) != 'nan'
            }

        from genai.chatbot import chat_with_gemini
        result = chat_with_gemini(user_message, fault_history, sensor_snapshot)
        return jsonify(result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'response': f'Error: {str(e)}'}), 500


@app.route('/api/insights')
def api_insights():
    """Gemini-powered predictive trend insights from recent sensor data."""
    if 'username' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
        
    if not ai_settings.get('gemini_insights', True):
        return jsonify({'success': False, 'insights': [], 'disabled': True, 'message': 'Gemini Insights are currently disabled.'})

    try:
        if df_dataset.empty:
            return jsonify({'insights': ['Dataset not loaded.'], 'success': False})

        # Compute stats on last 50 rows
        recent = df_dataset.tail(50)
        sensor_cols = ['Voltage (V)', 'Current (A)', 'Power (kW)', 'Temperature (\u00b0C)',
                       'Vibration (mm/s)', 'Speed (RPM)', 'Slip', 'Power Factor']
        sensor_stats = {}
        for col in sensor_cols:
            if col in recent.columns:
                numeric = pd.to_numeric(recent[col], errors='coerce').dropna()
                if not numeric.empty:
                    sensor_stats[col] = {
                        'mean': float(numeric.mean()),
                        'max': float(numeric.max()),
                        'min': float(numeric.min()),
                        'std': float(numeric.std())
                    }

        recent_faults = [
            str(f) for f in recent['Fault_Type'].values
            if str(f) not in ['Normal Operation', 'Normal', 'No Fault', '-']
        ] if 'Fault_Type' in recent.columns else []

        from genai.chatbot import generate_trend_insights
        result = generate_trend_insights(sensor_stats, recent_faults)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'insights': [f'Insight generation error: {str(e)}']}), 500

# Add additional routes for user management, charts, etc. as needed

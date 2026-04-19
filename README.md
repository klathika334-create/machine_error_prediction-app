---
title: Aurispower Machine Prediction
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
python_version: 3.10
pinned: false
---

# Machine Error Prediction

This project implements a machine learning system using AI fundamentals and LSTM to predict machine errors and provide preventive maintenance suggestions.

## System Architecture

### 1. Electrical Data Simulator (Digital Twin Layer)
Simulates electrical system data, replacing real-world hardware.

### 2. Fault Injection Engine
Creates intentional faults for testing system response.

### 3. AI / ML Prediction Layer
Analyzes data to detect anomalies and predict failures.

### 4. Daily Prevention Engine
Evaluates system health and generates preventive alerts.

### 5. GenAI Explanation Module
Converts technical outputs into human-readable maintenance advice.

### 6. Dashboard & User Interface
Provides real-time visualization and system insights.

### 7. Role-Based Access & Authentication
Ensures data privacy and usability with role-based access control.

## Project Structure
```
Machine error prediction/
│
├── data/                     # Dataset folder
│   ├── train/
│   ├── test/
│   ├── validation/
│   └── README.md
│
├── src/                      # Source code folder
│   ├── simulators/           # Electrical Data Simulator
│   │   ├── simulator.py
│   │   └── fault_injection.py
│   ├── ai_ml/                # AI/ML Prediction Layer
│   │   ├── anomaly_detection.py
│   │   ├── time_series_model.py
│   │   └── pattern_deviation.py
│   ├── prevention_engine/    # Daily Prevention Engine
│   │   └── prevention_engine.py
│   ├── genai/                # GenAI Explanation Module
│   │   └── explanation.py
│   ├── dashboard/            # Dashboard & User Interface
│   │   ├── app.py
│   │   ├── templates/
│   │   │   └── index.html
│   │   └── static/
│   │       ├── css/
│   │       └── js/
│   │       └── images/
│   └── auth/                 # Role-Based Access & Authentication
│       ├── auth.py
│       └── models.py
│
├── requirements.txt          # Python dependencies
├── app.py                    # Main entry point
└── README.md                 # Project documentation

```

## Running Locally (No Docker)

1. **MongoDB Setup**:
   - Download MongoDB binaries from the official site.
   - Extract them and run:
     ```bash
     mkdir -p mongodb_data
     ./mongodb-linux-x86_64-ubuntu2204-7.0.5/bin/mongod --dbpath mongodb_data --port 27017 --bind_ip 127.0.0.1 --fork --logpath mongodb_data/mongod.log
     ```

2. **Run Application**:
   ```bash
   source venv/bin/activate
   python src/dashboard/app.py
   ```

# Project Information

## Overview
This project is a Machine Error Prediction Dashboard that leverages AI fundamentals and LSTM (Long Short-Term Memory) neural networks to predict and visualize machine faults in real time. It features a modular, layered architecture for scalability and maintainability.

## Architecture
- **Backend:** Python (Flask), pandas, flask-pymongo, bcrypt, flask-jwt-extended
- **Frontend:** HTML, CSS (glassmorphism/dark theme), JavaScript, Chart.js
- **Database:** MongoDB (user management), Excel (analytics data)
- **AI/ML:** LSTM for time-series prediction, modular AI/ML pipeline

## Key Features
- Secure authentication (signup/login) with hashed passwords and JWT
- Role-based user management (MongoDB)
- Live dashboard with animated, premium UI
- Visualization of 8 key metrics (Voltage, Current, Power, Temperature, Vibration, Speed, Slip, Power Factor) from Excel data
- Random sampling of 12 records for real-time analytics
- Live monitor for latest machine issue
- Modular codebase: simulators, AI/ML, prevention engine, GenAI, dashboard, authentication

## Plugins & Packages Used
- **Flask** - Web framework
- **pandas** - Data manipulation and Excel reading
- **flask-pymongo** - MongoDB integration
- **bcrypt** - Password hashing
- **flask-jwt-extended** - JWT authentication
- **Chart.js** - Frontend charting
- **dotenv** - Environment variable management
- **Werkzeug** - Secure password utilities

## How it Works
1. Users sign up and log in securely (MongoDB stores credentials, passwords are hashed).
2. After login, the dashboard displays 8 separate charts for each metric, using 12 random records from the Excel dataset.
3. The backend serves data via a REST API endpoint (`/api/random-data`), which the frontend fetches and visualizes.
4. The latest machine issue is shown in a live monitor section.
5. All code is modular, with clear separation between authentication, AI/ML, and dashboard logic.

## Deployment
- Run `python src/dashboard/app.py` to start the Flask server.
- MongoDB must be running locally on `mongodb://localhost:27017`.
- Excel file must be placed in `data/Industrial_MultiClass_Dataset_With_Slip.xlsx`.

## Further Details
- Premium, animated UI with glassmorphism and dark mode for modern look and feel.
- Extensible for additional analytics, metrics, or user roles as needed.

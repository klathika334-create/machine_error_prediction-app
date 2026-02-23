# AurisPower Machine Error Prediction: System Architecture

The AurisPower system is a comprehensive Industry 4.0 solution designed for predictive maintenance of industrial machinery. It integrates real-time data simulation, machine learning for fault prediction, and Generative AI for maintenance advice.

## High-Level Architecture

The system follows a modular architecture consisting of five primary layers:

```mermaid
graph TD
    subgraph "Data Acquisition & Simulation"
        DS[Industrial Dataset (.xlsx)] --> DT[Digital Twin / Simulator]
        FI[Fault Injection Engine] --> DT
    end

    subgraph "AI / ML Prediction Layer"
        DT --> LSTM[LSTM Time-Series Predictor]
        DT --> AD[Anomaly Detection]
        DT --> PD[Pattern Deviation Model]
    end

    subgraph "Intelligent Logic Layer"
        LSTM --> GE[GenAI Explanation Module]
        AD --> PE[Prevention Engine]
        PD --> PE
    end

    subgraph "Integration & Storage Layer"
        FL[Flask Backend] <--> DB[(MongoDB)]
        FL <--> GE
        FL <--> PE
    end

    subgraph "Interface Layer"
        FL <--> UI[Web Dashboard]
        UI --> AU[Role-Based Authentication]
        GE --> ED[Email Drafts / Alerts]
    end
```

## Component Breakdown

### 1. Data Layer (Digital Twin)
- **Industrial Dataset**: Uses a real-world multiclass dataset (`Industrial_MultiClass_Dataset_With_Slip.xlsx`) containing electrical and mechanical parameters.
- **Simulator**: Emulates continuous data streams from industrial sensors (Voltage, Current, Temperature, etc.).
- **Fault Injection**: Allows for the intentional introduction of specific faults to test system resilience and model accuracy.

### 2. AI / ML Prediction Layer
- **LSTM Predictor**: A Long Short-Term Memory neural network (TensorFlow/Keras) that analyzes time-series data to predict future fault codes.
- **Anomaly Detection**: Implements unsupervised learning to identify outliers and unusual system behavior.
- **Pattern Deviation**: Uses an Autoencoder-like approach to detect subtle shifts in operating patterns before they become critical failures.

### 3. GenAI Explanation Module
- **Contextual Explanations**: Converts complex model outputs into human-readable descriptions of what is happening.
- **Corrective Actions**: Generates detailed, step-by-step maintenance solutions based on the predicted fault.
- **Automated Alerts**: Can automatically save detailed maintenance guides as Gmail drafts for the engineering team.

### 4. Prevention Engine
- Evaluates system health logs against thresholds.
- Generates proactive maintenance alerts based on trends (e.g., rising temperature trends before a threshold is hit).

### 5. Web Interface & Dashboard
- **Frontend**: A responsive dashboard for real-time visualization of machine metrics and predicted faults.
- **Backend**: Built with Flask, managing the flow of data between models and the UI.
- **Storage**: MongoDB stores user profiles, role-based access information, and session-specific statistics.

## Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS, JavaScript |
| **Backend** | Python (Flask) |
| **AI / ML** | TensorFlow, Keras, Scikit-learn, Pandas, NumPy |
| **GenAI** | Customized logic for solution generation (extensible for LLM integration) |
| **Database** | MongoDB |
| **Version Control** | Git |

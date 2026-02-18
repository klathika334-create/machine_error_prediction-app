# explanation.py
# This module converts system outputs into human-readable maintenance advice.

def generate_explanation(alert):
    explanations = {
        "Overheating trend detected.": "The wiring temperature has been increasing abnormally, which usually indicates loose connections. Inspection is recommended within the next two days to avoid fire risk.",
        "Possible earth leakage detected.": "Earth leakage has been detected. This could indicate insulation degradation or a potential short circuit. Immediate inspection is advised."
    }
    return explanations.get(alert, "No explanation available.")

if __name__ == "__main__":
    alert = "Overheating trend detected."
    explanation = generate_explanation(alert)
    print(explanation)

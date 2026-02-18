# explanation.py
# This module converts system outputs into human-readable maintenance advice
# and generates detailed solutions for detected faults.

from datetime import datetime

def generate_explanation(alert):
    """Generate a brief explanation for a fault type."""
    explanations = {
        "Normal": "System is operating within normal parameters.",
        "No Fault": "System is operating within normal parameters.",
        "Overheating": "The wiring temperature has been increasing abnormally, which usually indicates loose connections. Inspection is recommended within the next two days to avoid fire risk.",
        "Voltage Sag": "A temporary dip in voltage has been detected. Check for heavy load switching or grid instability.",
        "Voltage Swell": "A temporary spike in voltage has been detected. This could damage sensitive equipment. Check voltage regulation systems.",
        "Earth Leakage": "Earth leakage has been detected. This could indicate insulation degradation or a potential short circuit. Immediate inspection is advised.",
        "Short Circuit": "Critical: Short circuit detected. Immediate system shutdown and inspection is required to prevent equipment damage.",
        "Open Circuit": "Open circuit detected. Check for broken conductors or disconnected wires.",
        "Overload": "System overload detected. Reduce load immediately to prevent tripping or damage.",
        "Unbalanced": "Phase unbalance detected. Check loads on each phase and distribution system."
    }
    
    alert_clean = str(alert).strip()
    
    if alert_clean in explanations:
        return explanations[alert_clean]
    
    for key, text in explanations.items():
        if key.lower() in alert_clean.lower():
            return text
            
    return "Fault detected. Please inspect the system logs for more details."


def generate_solution(fault_type, combination):
    """
    Generate a detailed AI-powered solution for a detected fault.
    Returns a dict with subject, body (email-ready), severity, and timestamp.
    """
    
    # Comprehensive solution database keyed by fault type
    solutions = {
        "Overheating": {
            "severity": "critical",
            "cause": "Excessive thermal buildup due to loose connections, overloaded circuits, or inadequate ventilation in the electrical panel.",
            "steps": [
                "1. Immediately reduce load on the affected circuit by at least 30%",
                "2. Inspect all terminal connections for signs of discoloration or melting",
                "3. Use thermal imaging to identify hotspot locations",
                "4. Check ventilation fans and cooling systems in the panel enclosure",
                "5. Verify conductor sizing matches the load requirements (NEC Table 310.16)",
                "6. Re-torque all connections to manufacturer specifications",
                "7. Schedule preventive maintenance within 48 hours"
            ],
            "urgency": "HIGH — Risk of fire or equipment damage. Address within 24 hours."
        },
        "Voltage Sag": {
            "severity": "warning",
            "cause": "Temporary voltage reduction typically caused by heavy motor starting, utility grid fluctuations, or transformer tap issues.",
            "steps": [
                "1. Monitor voltage levels at the main distribution panel for 24 hours",
                "2. Check for large motor starts coinciding with sag events",
                "3. Inspect utility transformer tap settings",
                "4. Consider installing a Voltage Regulator or UPS for sensitive loads",
                "5. Review power factor correction capacitor bank status",
                "6. Contact utility provider if sags exceed ±10% of nominal"
            ],
            "urgency": "MEDIUM — Could cause equipment malfunction. Investigate within 3 days."
        },
        "Voltage Swell": {
            "severity": "warning",
            "cause": "Temporary voltage increase often caused by sudden load shedding, capacitor bank switching, or single-phase fault on a three-phase system.",
            "steps": [
                "1. Check for recent load disconnections or capacitor bank switching events",
                "2. Inspect surge protection devices (SPDs) at the service entrance",
                "3. Verify voltage regulator operation and settings",
                "4. Install transient voltage surge suppressors (TVSS) on sensitive equipment",
                "5. Monitor and log voltage events using a power quality analyzer",
                "6. Review grounding system integrity"
            ],
            "urgency": "MEDIUM — Risk of insulation breakdown. Investigate within 48 hours."
        },
        "Earth Leakage": {
            "severity": "critical",
            "cause": "Current leaking to ground through damaged insulation, moisture ingress, or deteriorated cable sheathing.",
            "steps": [
                "1. IMMEDIATELY isolate the affected circuit using the main breaker",
                "2. Perform insulation resistance test (Megger test) on all conductors",
                "3. Inspect cable runs for physical damage, moisture, or rodent activity",
                "4. Check GFCI/RCD devices for proper operation (trip test)",
                "5. Test grounding electrode system resistance (must be < 5 ohms)",
                "6. Replace any cables with insulation resistance below 1 MΩ",
                "7. Verify motor winding insulation integrity"
            ],
            "urgency": "CRITICAL — Electric shock hazard. Address immediately."
        },
        "Short Circuit": {
            "severity": "critical",
            "cause": "Direct contact between live conductors due to insulation failure, foreign objects, or mechanical damage.",
            "steps": [
                "1. EMERGENCY: Ensure power is disconnected at the source immediately",
                "2. Do NOT re-energize until fault is located and cleared",
                "3. Inspect all junction boxes and termination points for arc damage",
                "4. Perform continuity and insulation testing on all conductors",
                "5. Check protective devices (fuses/breakers) for proper coordination",
                "6. Replace damaged conductors and components",
                "7. Perform a phased re-energization with current monitoring",
                "8. Document the incident for compliance records"
            ],
            "urgency": "EMERGENCY — Fire and equipment destruction risk. Immediate shutdown required."
        },
        "Open Circuit": {
            "severity": "warning",
            "cause": "Broken conductor, loose connection, blown fuse, or tripped breaker causing an interrupted current path.",
            "steps": [
                "1. Identify the affected phase/circuit using multimeter continuity test",
                "2. Inspect all terminal blocks, bus bars, and splice points",
                "3. Check for tripped breakers or blown fuses in the panel",
                "4. Verify conductor integrity using a cable tracer/toner",
                "5. Re-terminate any loose or corroded connections",
                "6. Test the circuit under load after repair"
            ],
            "urgency": "MEDIUM — Equipment downtime. Repair within 24 hours."
        },
        "Overload": {
            "severity": "critical",
            "cause": "Current exceeding the rated capacity of conductors or protective devices, often due to additional loads or mechanical binding.",
            "steps": [
                "1. Immediately shed non-critical loads to reduce current below rated capacity",
                "2. Measure actual current draw on each phase with a clamp meter",
                "3. Compare measured values against breaker/fuse ratings and conductor ampacity",
                "4. Check for mechanical issues (seized bearings, jammed equipment)",
                "5. Redistribute loads across available circuits for better balance",
                "6. Upgrade conductor sizing or protective devices if load growth is permanent",
                "7. Install overload relays with proper settings on motor circuits"
            ],
            "urgency": "HIGH — Risk of conductor damage and fire. Reduce load immediately."
        },
        "Unbalanced": {
            "severity": "warning",
            "cause": "Unequal current or voltage distribution across three phases, caused by uneven single-phase load distribution or a failed phase.",
            "steps": [
                "1. Measure voltage and current on all three phases at the main panel",
                "2. Calculate percentage imbalance (should be < 2% for voltage, < 10% for current)",
                "3. Redistribute single-phase loads evenly across the three phases",
                "4. Check for failed capacitors in power factor correction banks",
                "5. Inspect for single-phasing conditions on motors (check contactors)",
                "6. Verify utility supply balance at the service entrance",
                "7. Consider installing a phase balancer for chronic issues"
            ],
            "urgency": "MEDIUM — Motor overheating risk. Balance loads within 72 hours."
        }
    }
    
    # Clean inputs
    fault_clean = str(fault_type).strip() if fault_type else "Unknown"
    combo_clean = str(combination).strip() if combination else "-"
    
    # Find matching solution
    solution_data = None
    matched_fault = fault_clean
    
    # Direct match
    if fault_clean in solutions:
        solution_data = solutions[fault_clean]
    else:
        # Partial match
        for key, data in solutions.items():
            if key.lower() in fault_clean.lower():
                solution_data = data
                matched_fault = key
                break
    
    # Also check combination for partial match if no direct fault match
    if not solution_data and combo_clean not in ['-', 'Normal', 'No Fault']:
        for key, data in solutions.items():
            if key.lower() in combo_clean.lower():
                solution_data = data
                matched_fault = key
                break
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not solution_data:
        # Generic solution for unknown faults
        return {
            "fault_type": fault_clean,
            "combination": combo_clean,
            "severity": "info",
            "subject": f"[ALERT] Machine Fault Detected: {fault_clean}",
            "body": (
                f"Dear Maintenance Team,\n\n"
                f"A fault has been detected in the monitored system.\n\n"
                f"Fault Type: {fault_clean}\n"
                f"Combination: {combo_clean}\n"
                f"Detected At: {timestamp}\n\n"
                f"Recommended Action:\n"
                f"  1. Review system logs for the affected circuit\n"
                f"  2. Perform visual inspection of all connections\n"
                f"  3. Run diagnostic tests on the affected equipment\n"
                f"  4. Schedule preventive maintenance\n\n"
                f"Urgency: STANDARD — Investigate within the next maintenance window.\n\n"
                f"Best Regards,\n"
                f"AurisPower AI Monitoring System"
            ),
            "timestamp": timestamp
        }
    
    steps_text = "\n".join(f"  {step}" for step in solution_data["steps"])
    
    return {
        "fault_type": fault_clean,
        "combination": combo_clean,
        "severity": solution_data["severity"],
        "subject": f"[{solution_data['severity'].upper()}] Machine Fault: {matched_fault} — Immediate Action Required",
        "body": (
            f"Dear Maintenance Team,\n\n"
            f"⚠️ A {solution_data['severity'].upper()} fault has been detected by the AurisPower AI Monitoring System.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"FAULT DETAILS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  Type: {fault_clean}\n"
            f"  Combination: {combo_clean}\n"
            f"  Detected At: {timestamp}\n"
            f"  Severity: {solution_data['severity'].upper()}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"ROOT CAUSE ANALYSIS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  {solution_data['cause']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"RECOMMENDED CORRECTIVE ACTIONS\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{steps_text}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"URGENCY\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"  {solution_data['urgency']}\n\n"
            f"Please acknowledge this alert and update the maintenance log.\n\n"
            f"Best Regards,\n"
            f"AurisPower AI Monitoring System"
        ),
        "timestamp": timestamp
    }


if __name__ == "__main__":
    alert = "Overheating trend detected."
    explanation = generate_explanation(alert)
    print(explanation)
    
    solution = generate_solution("Overheating", "High Temperature + Vibration")
    print("\n--- Solution ---")
    print(f"Subject: {solution['subject']}")
    print(f"Severity: {solution['severity']}")
    print(solution['body'])

# explanation.py
# This module converts system outputs into human-readable maintenance advice
# and generates detailed solutions for detected faults.
# Updated: covers all 23 fault types from the Industrial dataset.
# Gemini AI integration: tries Gemini first, falls back to hardcoded solutions.

from datetime import datetime
import random

def generate_explanation(alert):
    """Generate a brief explanation for a fault type."""
    explanations = {
        "Normal Operation": "System is operating within normal parameters. No action required.",
        "Undervoltage": "Supply voltage has dropped below acceptable limits. Check the power supply and distribution network.",
        "Overvoltage": "Supply voltage has exceeded safe limits. Risk of insulation damage and equipment failure.",
        "Voltage Unbalance": "Unequal voltages detected across phases. Can cause motor overheating and reduced efficiency.",
        "Overcurrent": "Current is exceeding rated limits. Risk of conductor damage and fire. Reduce load immediately.",
        "Single Phasing": "One supply phase is missing. Equipment is running on two phases — immediate shutdown required.",
        "Stator Winding Fault": "Stator winding insulation failure detected. Motor needs immediate de-energization and inspection.",
        "Rotor Bar Fault": "Broken or cracked rotor bars detected. Motor efficiency is compromised and torque is reduced.",
        "Insulation Breakdown": "Electrical insulation has deteriorated. Risk of short circuit and electric shock.",
        "Bearing Inner Race Fault": "Fault detected on the inner race of the bearing. Vibration and noise will increase progressively.",
        "Bearing Outer Race Fault": "Fault detected on the outer race of the bearing. Vibration signature indicates race degradation.",
        "Shaft Misalignment": "Motor shaft is misaligned with the driven equipment. Excessive vibration and bearing wear will result.",
        "Rotor Imbalance": "Rotor mass distribution is uneven. This causes vibration, bearing wear, and structural fatigue.",
        "Mechanical Overload": "Mechanical load on the motor exceeds its rated capacity. Risk of motor burnout.",
        "Stator Overheating": "Stator temperature has reached critical levels. Check cooling, loading, and ventilation.",
        "Bearing Overheating": "Bearing temperature is dangerously high. Likely caused by lubrication failure or overloading.",
        "Cooling Failure": "The cooling system has failed or is insufficient. Motor temperature will rise rapidly.",
        "Overload with Overheating": "Combined overload and overheating condition detected. Critical — immediate intervention needed.",
        "Bearing Fault with Speed Drop": "Bearing degradation is causing speed reduction. Progressive failure leading to seizure.",
        "Voltage Unbalance with Rotor Fault": "Combined voltage imbalance and rotor fault. Compounded stress on the motor.",
        "Insulation Breakdown with Ground Leakage": "Insulation failure with current leaking to ground. Shock hazard — isolate immediately.",
        "Electrical and Mechanical Combined Failure": "Simultaneous electrical and mechanical faults detected. System integrity is severely compromised.",
        "Catastrophic System Failure": "EMERGENCY: Critical multi-system failure detected. Immediate shutdown and full inspection mandatory."
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
    Covers all 23 fault types in the Industrial dataset.
    """

    solutions = {
        "Undervoltage": {
            "severity": "warning",
            "cause": "Supply voltage has dropped below the permissible limit, typically due to utility issues, heavy loading, long cable runs, or transformer tap misconfigurations.",
            "steps": [
                "1. Measure voltage at main panel and compare to rated value",
                "2. Check utility supply voltage at the point of common coupling",
                "3. Inspect transformer tap settings and adjust if necessary",
                "4. Evaluate cable sizing for excessive voltage drop under load",
                "5. Install automatic voltage regulator (AVR) for sensitive loads",
                "6. Reduce non-critical loads during peak demand periods",
                "7. Contact utility provider if supply voltage is persistently low"
            ],
            "urgency": "MEDIUM — Equipment malfunction risk. Investigate within 48 hours."
        },
        "Overvoltage": {
            "severity": "critical",
            "cause": "Supply voltage has exceeded safe limits due to load shedding, capacitor switching, or utility overvoltage events.",
            "steps": [
                "1. Immediately check voltage levels at all distribution panels",
                "2. Inspect surge protection devices (SPDs) for damage",
                "3. Verify voltage regulator and AVR operation",
                "4. Disconnect sensitive equipment until voltage stabilises",
                "5. Check for disconnected large loads that may have caused voltage rise",
                "6. Install transient voltage surge suppressors on critical circuits",
                "7. Log the event and notify utility provider"
            ],
            "urgency": "HIGH — Risk of insulation damage. Investigate within 24 hours."
        },
        "Voltage Unbalance": {
            "severity": "warning",
            "cause": "Unequal phase voltages caused by uneven single-phase load distribution, open delta transformer, or a defective phase conductor.",
            "steps": [
                "1. Measure all three phase voltages and calculate percentage imbalance",
                "2. Redistribute single-phase loads evenly across the three phases",
                "3. Inspect transformer winding and connections for faults",
                "4. Check for blown fuses or open contactors on one phase",
                "5. Verify utility supply balance at the service entrance",
                "6. Consider installing a phase balancer for chronic imbalance",
                "7. Monitor motor temperatures — unbalance accelerates overheating"
            ],
            "urgency": "MEDIUM — Motor overheating risk. Balance loads within 72 hours."
        },
        "Overcurrent": {
            "severity": "critical",
            "cause": "Current exceeds rated conductor and equipment limits due to overloading, short circuit, or mechanical jam.",
            "steps": [
                "1. Immediately shed non-critical loads to reduce current below rated value",
                "2. Measure current on all phases using a clamp meter",
                "3. Inspect for mechanical jams or seized components driving high current",
                "4. Check circuit breaker and fuse ratings vs actual load",
                "5. Verify overload relay settings on motor starters",
                "6. Inspect for signs of overheating in conductors and terminals",
                "7. Upgrade conductor sizing or protective devices if load is permanent"
            ],
            "urgency": "HIGH — Risk of conductor damage and fire. Reduce load immediately."
        },
        "Single Phasing": {
            "severity": "critical",
            "cause": "One of the three supply phases is absent due to a blown fuse, open contactor, broken conductor, or utility fault.",
            "steps": [
                "1. IMMEDIATELY stop all motors operating under single-phase condition",
                "2. Identify the missing phase using a multimeter or phase indicator",
                "3. Check fuses and replace any that have blown",
                "4. Inspect contactor contacts for wear, welding, or open circuit",
                "5. Trace the conductor from the panel to the motor for breaks",
                "6. Verify utility supply has all three phases at the service entrance",
                "7. Install phase-failure relay for automatic protection in future"
            ],
            "urgency": "CRITICAL — Motor will overheat and burn out rapidly. Shut down immediately."
        },
        "Stator Winding Fault": {
            "severity": "critical",
            "cause": "Stator winding insulation has degraded due to thermal stress, moisture ingress, voltage spikes, or mechanical vibration.",
            "steps": [
                "1. De-energize the motor immediately",
                "2. Perform insulation resistance (Megger) test on all windings",
                "3. Measure winding resistance across all phases for imbalance",
                "4. Inspect windings visually for burnt marks, discolouration, or swelling",
                "5. Check for moisture ingress in the motor enclosure",
                "6. Send motor to rewinding shop if insulation resistance is below 1 MΩ",
                "7. Install surge arrestors to prevent future voltage spike damage"
            ],
            "urgency": "CRITICAL — Motor failure imminent. Remove from service immediately."
        },
        "Rotor Bar Fault": {
            "severity": "warning",
            "cause": "One or more rotor bars are cracked or broken due to thermal cycling, mechanical stress, or casting defects.",
            "steps": [
                "1. Perform Motor Current Signature Analysis (MCSA) to confirm rotor bar faults",
                "2. Monitor vibration levels — broken bars increase vibration at twice slip frequency",
                "3. Reduce load on the motor to slow fault progression",
                "4. Schedule rotor inspection during next maintenance window",
                "5. Check startup frequency — repeated DOL starts accelerate rotor bar cracking",
                "6. Consider using a soft starter or VFD to reduce thermal stress",
                "7. Replace rotor if more than 2 consecutive bars are broken"
            ],
            "urgency": "MEDIUM — Progressive failure. Inspect within 7 days."
        },
        "Insulation Breakdown": {
            "severity": "critical",
            "cause": "Electrical insulation has deteriorated due to age, moisture, chemical contamination, or sustained overvoltage.",
            "steps": [
                "1. De-energize all affected circuits immediately",
                "2. Perform Megger insulation resistance test on all conductors",
                "3. Conduct polarisation index (PI) test for winding insulation quality",
                "4. Inspect cable runs for physical damage, heat marks, or moisture",
                "5. Replace any cable with insulation resistance below 1 MΩ",
                "6. Dry out damp motor windings with a low-voltage heat source",
                "7. Apply insulation varnish treatment after repair"
            ],
            "urgency": "CRITICAL — Electric shock and fire risk. Address immediately."
        },
        "Bearing Inner Race Fault": {
            "severity": "warning",
            "cause": "The inner race of the motor or driven equipment bearing has developed pitting or spalling due to fatigue, contamination, or misalignment.",
            "steps": [
                "1. Perform vibration spectrum analysis to confirm inner race fault frequency",
                "2. Monitor vibration trend — schedule replacement before amplitude doubles",
                "3. Check shaft alignment with laser alignment tool",
                "4. Inspect lubrication quality and quantity — contamination accelerates race wear",
                "5. Check bearing fit on shaft for looseness (fretting corrosion)",
                "6. Replace bearing during next planned shutdown window",
                "7. Use accelerometer on motor housing for ongoing monitoring"
            ],
            "urgency": "MEDIUM — Controlled failure mode. Replace bearing within 14 days."
        },
        "Bearing Outer Race Fault": {
            "severity": "warning",
            "cause": "The outer race of the bearing has developed pitting due to overloading, contamination, or inadequate lubrication.",
            "steps": [
                "1. Confirm fault via vibration analysis — outer race frequency is load-zone dependent",
                "2. Inspect bearing housing for correct fit (loose housing causes race spinning)",
                "3. Verify correct bearing selection for load and speed",
                "4. Check lubricant specification and relubrication interval",
                "5. Inspect seals for contamination ingress",
                "6. Schedule bearing replacement in next maintenance window",
                "7. Review equipment alignment and coupling condition"
            ],
            "urgency": "MEDIUM — Monitor closely. Replace bearing within 14 days."
        },
        "Shaft Misalignment": {
            "severity": "warning",
            "cause": "The motor shaft is not collinear with the driven shaft due to incorrect installation, thermal growth, or soft foot conditions.",
            "steps": [
                "1. Shut down equipment and perform laser shaft alignment check",
                "2. Record angular and offset misalignment in both horizontal and vertical planes",
                "3. Correct soft foot condition before performing final alignment",
                "4. Re-align coupling to within manufacturer's specified tolerance",
                "5. Inspect flexible coupling elements for wear or damage due to misalignment",
                "6. Check for pipe strain on pump casings that can cause post-alignment shift",
                "7. Document alignment readings and recheck after first 24 hours of operation"
            ],
            "urgency": "MEDIUM — Accelerated bearing and coupling wear. Align within 48 hours."
        },
        "Rotor Imbalance": {
            "severity": "warning",
            "cause": "Uneven mass distribution on the rotor due to erosion, deposits, missing balance weights, or bent shaft.",
            "steps": [
                "1. Measure vibration at motor bearings — 1× running speed dominates for imbalance",
                "2. Inspect rotor for material build-up, erosion, or missing balance weights",
                "3. Check shaft for bending using a dial gauge at multiple axial positions",
                "4. Remove rotor and perform dynamic balancing to ISO 1940 Grade G2.5",
                "5. Inspect coupling and driven equipment for imbalance contribution",
                "6. Clean fan blades and rotors of accumulated debris",
                "7. Monitor vibration trend after balancing to verify correction"
            ],
            "urgency": "MEDIUM — Progressive bearing damage. Balance rotor within 7 days."
        },
        "Mechanical Overload": {
            "severity": "critical",
            "cause": "The mechanical load on the motor exceeds its rated torque capacity due to process changes, blocked equipment, or coupling failure.",
            "steps": [
                "1. Stop the motor immediately and investigate the mechanical load path",
                "2. Check for jammed, seized, or blocked driven equipment",
                "3. Measure no-load current vs full-load current to quantify overload level",
                "4. Inspect coupling and gearbox for damage caused by overload torque",
                "5. Reduce process load or upgrade motor to higher rated power",
                "6. Verify overload relay set-point is correctly configured",
                "7. Install torque limiters or fluid couplings for overload protection"
            ],
            "urgency": "HIGH — Motor burnout risk. Investigate cause before restart."
        },
        "Stator Overheating": {
            "severity": "critical",
            "cause": "Stator winding temperature has exceeded rated class limits due to overloading, blocked ventilation, or cooling system failure.",
            "steps": [
                "1. Reduce load on the motor immediately by at least 30%",
                "2. Inspect motor ventilation paths for blockages or accumulated dust",
                "3. Check cooling fan operation and airflow direction",
                "4. Verify ambient temperature is within motor design limits",
                "5. Measure winding resistance — elevated temperature will show higher resistance",
                "6. Inspect thermal protection sensors (PT100, thermistors) for correct operation",
                "7. Allow motor to cool fully before restarting; investigate root cause first"
            ],
            "urgency": "HIGH — Insulation lifespan reduced exponentially. Address within 24 hours."
        },
        "Bearing Overheating": {
            "severity": "critical",
            "cause": "Bearing temperature has reached critical levels due to excessive lubrication, insufficient lubrication, overloading, or bearing defect.",
            "steps": [
                "1. Shut down immediately if bearing temperature exceeds 95°C",
                "2. Allow bearing to cool and check lubricant type, quantity, and contamination",
                "3. Purge and regrease if over-lubrication is suspected (blocked drain plug)",
                "4. Verify bearing is not overloaded beyond dynamic load rating",
                "5. Check shaft alignment — misalignment generates additional bearing heat",
                "6. Inspect bearing for signs of smearing, flaking, or discolouration",
                "7. Replace bearing and investigate root cause before restart"
            ],
            "urgency": "CRITICAL — Bearing seizure risk. Shut down immediately."
        },
        "Cooling Failure": {
            "severity": "critical",
            "cause": "The motor or system cooling mechanism has failed — fan damage, coolant loss, blocked heat exchanger, or TEFC enclosure breach.",
            "steps": [
                "1. Stop equipment immediately to prevent thermal runaway",
                "2. Inspect cooling fan for damage, reversal, or obstruction",
                "3. Check coolant level and flow in water-cooled systems",
                "4. Inspect heat exchanger for fouling or blockage",
                "5. Verify cooling system control circuits and thermostats are functional",
                "6. Check motor enclosure integrity — dust or debris ingress can block air flow",
                "7. Do not restart until cooling system is verified fully operational"
            ],
            "urgency": "CRITICAL — Temperature will rise rapidly. Shut down until cooling is restored."
        },
        "Overload with Overheating": {
            "severity": "critical",
            "cause": "The motor is simultaneously overloaded mechanically and thermally stressed — a compounded failure condition accelerating winding degradation.",
            "steps": [
                "1. IMMEDIATELY reduce load and shut down if temperature keeps rising",
                "2. Measure current draw and compare to nameplate FLA",
                "3. Inspect mechanical load path for jams or excessive friction",
                "4. Check ambient temperature and ventilation around the motor",
                "5. Allow motor to cool completely — minimum 30 minutes before restart attempt",
                "6. Perform insulation resistance test before restarting",
                "7. Review duty cycle — motor may need to be upsized for the application"
            ],
            "urgency": "CRITICAL — Combined stresses causing rapid insulation degradation. Shutdown now."
        },
        "Bearing Fault with Speed Drop": {
            "severity": "critical",
            "cause": "Advanced bearing degradation is causing mechanical drag that reduces rotor speed below synchronous, increasing slip and heating.",
            "steps": [
                "1. Measure shaft speed with a tachometer and compare to rated RPM",
                "2. Check vibration spectrum for bearing defect frequencies (BPFI, BPFO, BSF)",
                "3. Inspect bearing for seized or heavily worn race surfaces",
                "4. Verify lubricant has not solidified or been contaminated",
                "5. Check if speed drop is consistent with increased mechanical load",
                "6. Replace bearing immediately — speed drop indicates advanced failure stage",
                "7. Inspect shaft for wear at bearing seat after removal"
            ],
            "urgency": "CRITICAL — Bearing is near seizure. Replace immediately."
        },
        "Voltage Unbalance with Rotor Fault": {
            "severity": "critical",
            "cause": "A compound condition where voltage imbalance causes elevated negative-sequence currents that interact with existing rotor bar faults, amplifying heating and torque ripple.",
            "steps": [
                "1. Correct voltage imbalance at the supply first (highest priority)",
                "2. Measure three-phase voltages and calculate imbalance percentage",
                "3. Perform MCSA (Motor Current Signature Analysis) to assess rotor bar condition",
                "4. Reduce load significantly to limit thermal stress on both stator and rotor",
                "5. Plan motor removal and rotor inspection at earliest opportunity",
                "6. Install phase imbalance protection relay if not present",
                "7. Consider motor replacement if both faults are confirmed severe"
            ],
            "urgency": "CRITICAL — Compounded fault greatly accelerates failure. Act within 24 hours."
        },
        "Insulation Breakdown with Ground Leakage": {
            "severity": "critical",
            "cause": "Insulation failure has progressed to the point where current is leaking to earth — indicating conductor-to-ground contact through damaged cable sheath or winding.",
            "steps": [
                "1. IMMEDIATELY isolate the circuit at the main breaker",
                "2. Test ground fault current using a clamp meter on the earth conductor",
                "3. Perform Megger insulation test to locate the breakdown point",
                "4. Inspect all cable joints, terminations, and conduit entries for damage",
                "5. Check GFCI/RCD devices for operation; test trip function",
                "6. Replace all cables with insulation resistance below 1 MΩ",
                "7. Verify grounding system integrity — earth resistance must be below 5 Ω"
            ],
            "urgency": "CRITICAL — Electric shock hazard present. Isolate immediately."
        },
        "Electrical and Mechanical Combined Failure": {
            "severity": "critical",
            "cause": "Simultaneous electrical fault (winding/insulation) and mechanical fault (bearing/alignment) — likely caused by prolonged neglect or a severe overload event.",
            "steps": [
                "1. Immediately de-energize and lock-out tag-out (LOTO) the equipment",
                "2. Perform full electrical assessment: insulation resistance, winding resistance, supply quality",
                "3. Perform full mechanical assessment: bearing condition, alignment, coupling, shaft",
                "4. Document all findings with measurements and photographs",
                "5. Send motor to specialist repair shop for rewinding and bearing replacement",
                "6. Inspect driven equipment for damage caused by mechanical fault propagation",
                "7. Implement a predictive maintenance programme to prevent recurrence"
            ],
            "urgency": "EMERGENCY — Equipment is unsafe to operate. Isolate and quarantine immediately."
        },
        "Catastrophic System Failure": {
            "severity": "critical",
            "cause": "Multiple simultaneous critical faults have caused or are about to cause complete system breakdown — thermal, electrical, and mechanical integrity all compromised.",
            "steps": [
                "1. EMERGENCY STOP — Activate e-stop and isolate all power immediately",
                "2. Do NOT attempt restart under any circumstances",
                "3. Evacuate personnel from the immediate area and check for fire/smoke",
                "4. Contact emergency maintenance and engineering teams",
                "5. Perform full site safety inspection before re-entering the zone",
                "6. Document all pre-fault sensor readings and event logs",
                "7. Commission a full root-cause analysis before any repair work begins",
                "8. Replacement of entire motor and drive system is likely required"
            ],
            "urgency": "EMERGENCY — Life safety risk. Emergency response required immediately."
        }
    }

    # Clean inputs
    fault_clean = str(fault_type).strip() if fault_type else "Unknown"
    combo_clean = str(combination).strip() if combination else "-"

    # Find matching solution — direct match first
    solution_data = None
    matched_fault = fault_clean

    if fault_clean in solutions:
        solution_data = solutions[fault_clean]
    else:
        # Partial match on fault type
        for key, data in solutions.items():
            if key.lower() in fault_clean.lower() or fault_clean.lower() in key.lower():
                solution_data = data
                matched_fault = key
                break

    # Try combination string if still no match
    if not solution_data and combo_clean not in ['-', 'Normal', 'No Fault', 'Normal Operation']:
        for key, data in solutions.items():
            if key.lower() in combo_clean.lower():
                solution_data = data
                matched_fault = key
                break

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not solution_data:
        # Generic fallback
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

    severity_label = solution_data['severity'].upper()
    subject = f"[{severity_label}] Machine Fault Detected: {matched_fault} — Immediate Action Required"

    body = (
        f"Dear Maintenance Team,\n\n"
        f"⚠️  A {severity_label} fault has been detected by the AurisPower AI Monitoring System.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"FAULT DETAILS\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  Fault Type  : {fault_clean}\n"
        f"  Combination : {combo_clean}\n"
        f"  Detected At : {timestamp}\n"
        f"  Severity    : {severity_label}\n\n"
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
    )

    return {
        "fault_type": fault_clean,
        "combination": combo_clean,
        "severity": solution_data["severity"],
        "subject": subject,
        "body": body,
        "timestamp": timestamp
    }


def generate_solution_with_ai(fault_type: str, combination: str, sensor_readings: dict = None) -> dict:
    """
    Primary entry point — tries Gemini AI first for a dynamic, sensor-aware solution.
    Falls back to the hardcoded solutions database if Gemini is unavailable.

    Args:
        fault_type: Detected fault type string
        combination: Sensor combination pattern string
        sensor_readings: Dict of live sensor values {voltage, current, temperature, etc.}

    Returns:
        Solution dict with subject, body, severity, timestamp, and ai_generated flag.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Try Gemini AI first
    try:
        from genai.chatbot import generate_ai_fault_solution
        ai_result = generate_ai_fault_solution(fault_type, combination, sensor_readings)

        if ai_result.get('success'):
            severity = ai_result.get('severity', 'warning')
            severity_label = severity.upper()
            steps_text = '\n'.join(f'  {s}' for s in ai_result.get('steps', []))
            cause = ai_result.get('cause', 'AI-detected anomaly.')
            urgency = ai_result.get('urgency', 'Investigate promptly.')

            # Build sensor readings section
            sensor_section = ''
            if sensor_readings:
                sr_lines = '\n'.join(f'  {k}: {v}' for k, v in sensor_readings.items() if v is not None)
                sensor_section = (
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"LIVE SENSOR READINGS AT TIME OF FAULT\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{sr_lines}\n\n"
                )

            subject = f"[{severity_label}] AI Alert: {fault_type} — Action Required"
            body = (
                f"Dear Maintenance Team,\n\n"
                f"⚠️  A {severity_label} fault has been detected by the AurisPower AI Monitoring System.\n"
                f"✨  This analysis was generated by Gemini AI based on live sensor data.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"FAULT DETAILS\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  Fault Type  : {fault_type}\n"
                f"  Combination : {combination}\n"
                f"  Detected At : {timestamp}\n"
                f"  Severity    : {severity_label}\n\n"
                f"{sensor_section}"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"AI ROOT CAUSE ANALYSIS\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  {cause}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"RECOMMENDED CORRECTIVE ACTIONS (AI Generated)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{steps_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"URGENCY\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  {urgency}\n\n"
                f"Please acknowledge this alert and update the maintenance log.\n\n"
                f"Best Regards,\n"
                f"AurisPower AI Monitoring System (Powered by Gemini AI)"
            )

            return {
                "fault_type": fault_type,
                "combination": combination,
                "severity": severity,
                "subject": subject,
                "body": body,
                "timestamp": timestamp,
                "ai_generated": True
            }
    except Exception as e:
        print(f'[Gemini] Fault solution generation failed, using fallback: {e}')

    # Fallback to hardcoded solutions
    result = generate_solution(fault_type, combination)
    result['ai_generated'] = False
    return result


if __name__ == "__main__":
    faults = [
        ("Bearing Inner Race Fault", "Vibration + Speed"),
        ("Stator Overheating", "Current + Temperature"),
        ("Catastrophic System Failure", "Voltage + Current + Power + Temperature + Vibration + Speed + Power Factor"),
    ]
    for ft, combo in faults:
        sol = generate_solution(ft, combo)
        print(f"\n{'='*60}")
        print(f"Subject : {sol['subject']}")
        print(f"Severity: {sol['severity']}")
        print(sol['body'][:300])

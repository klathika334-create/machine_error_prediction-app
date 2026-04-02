# chatbot.py
# Gemini-powered conversational assistant for the AURISPOWER predictive maintenance system.

import os
import warnings
import time
import json
import re
warnings.filterwarnings('ignore', category=FutureWarning, module='google')
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_model = None
# Try models in order — each has its own free quota
MODELS_TO_TRY = ['gemini-flash-latest', 'gemini-2.5-flash', 'gemini-2.0-flash-lite', 'gemini-2.0-flash']

SYSTEM_CONTEXT = """You are an expert AI assistant embedded in the AURISPOWER Predictive Maintenance 
Monitoring System for industrial machines. Your role is to help plant operators and maintenance 
engineers understand machine faults, sensor readings, and corrective actions.

Guidelines:
- Be concise and practical — operators need fast, actionable answers
- Use plain language, avoid overly technical jargon unless asked
- If asked about a specific fault, explain its cause, impact, and fix steps
- When sensor readings are provided, reference them in your answer
- Keep responses under 200 words unless a detailed explanation is requested
- Format lists with numbered steps or bullet points for readability
"""


def _get_model():
    """Lazy-load and cache the Gemini model with model fallbacks."""
    global _model
    if _model is None:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return None
        genai.configure(api_key=api_key)
        for model_name in MODELS_TO_TRY:
            try:
                _model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=SYSTEM_CONTEXT
                )
                print(f'[Gemini] Loaded model: {model_name}')
                break
            except Exception:
                continue
    return _model


def _call_with_retry(model, prompt, retries=2, backoff=6):
    """Call Gemini with retry on 429 rate limit errors."""
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            err_str = str(e)
            if '429' in err_str:
                if attempt < retries - 1:
                    time.sleep(backoff)
                    continue
                # All retries exhausted
                raise Exception('rate_limited: ' + err_str[:200])
            raise e
    return None


def chat_with_gemini(user_message: str, fault_history: list = None, sensor_snapshot: dict = None) -> dict:
    """
    Send a message to Gemini and return its response.
    Handles 429 rate limits with retry and backoff.
    """
    model = _get_model()
    if model is None:
        return {
            'success': False,
            'response': '⚠️ Gemini API key not configured. Please add your GEMINI_API_KEY to the .env file.',
            'error': 'No API key'
        }

    try:
        context_parts = []
        if sensor_snapshot:
            sensor_str = ', '.join(f"{k}={v}" for k, v in sensor_snapshot.items() if v is not None)
            if sensor_str:
                context_parts.append(f"Current live sensor readings: {sensor_str}")

        if fault_history:
            history_str = '; '.join(
                f"{f.get('fault_type', 'Unknown')} ({f.get('severity', '?')} at {f.get('timestamp', '?')})"
                for f in fault_history[:5]
            )
            context_parts.append(f"Recent fault history: {history_str}")

        full_prompt = ('\n'.join(context_parts) + '\n\nOperator question: ' + user_message
                       if context_parts else user_message)

        text = _call_with_retry(model, full_prompt)
        return {'success': True, 'response': text}

    except Exception as e:
        err_str = str(e)
        if 'rate_limited' in err_str or '429' in err_str:
            return {
                'success': False,
                'response': '⏳ Gemini free tier quota reached for today. The system will use built-in solutions in the meantime. Try again tomorrow or upgrade to a paid Gemini plan.',
                'error': 'rate_limited'
            }
        return {
            'success': False,
            'response': f'Sorry, I encountered an error: {err_str[:200]}. Please try again.',
            'error': err_str
        }


def generate_trend_insights(sensor_stats: dict, recent_faults: list) -> dict:
    """
    Analyze sensor trends and recent faults to generate 3 predictive insights.
    """
    model = _get_model()
    if model is None:
        return {
            'success': False,
            'insights': ['⚠️ Add GEMINI_API_KEY to .env to enable AI predictive insights.']
        }

    try:
        stats_lines = []
        for col, vals in sensor_stats.items():
            if isinstance(vals, dict):
                stats_lines.append(
                    f"  {col}: avg={vals.get('mean', 0):.2f}, max={vals.get('max', 0):.2f}, "
                    f"min={vals.get('min', 0):.2f}, σ={vals.get('std', 0):.2f}"
                )

        fault_summary = ', '.join(set(recent_faults)) if recent_faults else 'None'

        prompt = f"""You are analyzing industrial machine sensor data for predictive maintenance.

Recent sensor statistics (last 50 readings):
{chr(10).join(stats_lines)}

Recent fault types detected: {fault_summary}

Generate exactly 3 short predictive maintenance insights.
Each insight must:
- Be 1-2 sentences maximum
- Start with an emoji: 🔴 for critical risk, 🟡 for warning, 🟢 for healthy
- Reference specific sensor values where possible

Return ONLY a JSON array of 3 strings. Example format:
["🔴 insight one", "🟡 insight two", "🟢 insight three"]
"""
        text = _call_with_retry(model, prompt)
        text = text.strip()

        match = re.search(r'\[.*?\]', text, re.DOTALL)
        if match:
            insights = json.loads(match.group())
            return {'success': True, 'insights': insights[:3]}
        else:
            lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 5]
            return {'success': True, 'insights': lines[:3]}

    except Exception as e:
        err_str = str(e)
        if 'rate_limited' in err_str or '429' in err_str:
            return {'success': False, 'insights': ['⏳ Gemini quota reached for today. Insights will resume tomorrow or with a paid plan.']}
        return {'success': False, 'insights': [f'⚠️ Insight generation error: {err_str[:100]}']}


def generate_ai_fault_solution(fault_type: str, combination: str, sensor_readings: dict = None) -> dict:
    """
    Generate a dynamic AI-powered fault solution using Gemini.
    """
    model = _get_model()
    if model is None:
        return {'success': False}

    try:
        sensor_str = ''
        if sensor_readings:
            sensor_str = '\n'.join(f"  {k}: {v}" for k, v in sensor_readings.items() if v is not None)

        prompt = f"""An industrial machine has triggered a fault. Provide a maintenance solution.

Fault Type: {fault_type}
Sensor Combination Pattern: {combination}
{"Live Sensor Readings:" + chr(10) + sensor_str if sensor_str else ""}

Respond in this exact JSON format (no markdown, just raw JSON):
{{
  "severity": "critical",
  "cause": "One sentence root cause explanation",
  "steps": ["Step 1: ...", "Step 2: ...", "Step 3: ...", "Step 4: ...", "Step 5: ..."],
  "urgency": "LEVEL — one sentence urgency with timeframe"
}}
"""
        text = _call_with_retry(model, prompt)
        text = text.strip()

        # Strip markdown fences
        text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE).strip()

        data = json.loads(text)
        data['success'] = True
        return data

    except Exception as e:
        return {'success': False, 'error': str(e)}


def generate_ai_report(report_data: dict) -> str:
    """
    Generate a professional narrative report using Gemini.
    """
    model = _get_model()
    if model is None:
        return None

    try:
        fault_lines = '\n'.join(
            f"  - {ft}: {cnt} occurrences"
            for ft, cnt in report_data.get('fault_counts', {}).items()
        )
        metric_lines = '\n'.join(
            f"  - {m}: {v:.3f}" for m, v in report_data.get('metric_averages', {}).items()
        )

        prompt = f"""Write a professional predictive maintenance report for an industrial facility.

Report Period: {report_data.get('period', 'Unknown')}
Plant/Scope: {report_data.get('plant', 'All Plants')}
Total Records Analyzed: {report_data.get('total_records', 0)}
Generated At: {report_data.get('generated_at', 'N/A')}

Average Sensor Metrics:
{metric_lines}

Fault Occurrences:
{fault_lines if fault_lines else '  - No faults recorded'}

Write a report with these 5 sections:
1. EXECUTIVE SUMMARY (2-3 sentences)
2. KEY OBSERVATIONS (3-4 bullet points referencing actual numbers)
3. RISK ASSESSMENT (top fault types and their business impact)
4. RECOMMENDED ACTIONS (4-5 prioritised maintenance actions for the next period)
5. CONCLUSION (1-2 sentences)

Use professional language. Keep it under 500 words.
"""
        text = _call_with_retry(model, prompt)
        return text

    except Exception as e:
        return None

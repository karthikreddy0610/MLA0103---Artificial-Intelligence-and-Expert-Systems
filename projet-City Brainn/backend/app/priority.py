"""
CityBrain Intelligent Priority & Municipal Department Classification Engine
=============================================================================
Powered by the Multi-Layer NLP Prompt Analyzer & Semantic Understanding Algorithm.
Extracts incident intent, real-world entity hazards, urgency sentiment, and departmental routing.
"""

from typing import Tuple, Dict, Any, Optional
from .nlp_analyzer import nlp_analyzer, analyze_prompt, get_priority_and_department


def generate_priority(text: str, category: str = None) -> Tuple[str, str]:
    """
    Evaluates grievance text and optional category to return (Priority, Department).
    Maintains 100% backward-compatibility across all CityBrain API routes and dispatch logic.
    """
    if not text:
        return "MEDIUM", "General Administration"

    priority, department = get_priority_and_department(text, category)
    return priority, department


def analyze_grievance_prompt(text: str, category: Optional[str] = None) -> Dict[str, Any]:
    """
    Full diagnostic prompt analysis returning intent, priority, department,
    confidence score, extracted entities, and dispatch recommendations.
    """
    return analyze_prompt(text, category)

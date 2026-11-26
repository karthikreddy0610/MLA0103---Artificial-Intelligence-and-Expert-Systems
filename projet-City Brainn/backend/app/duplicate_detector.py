"""
CityBrain Multi-Factor Duplicate Detection Engine
=================================================
Pipeline Position:
User Complaint -> NLP Analyzer (Root Issue & Dept) -> Duplicate Detector -> Priority Hub

Multi-Factor Duplicate Scoring (0 - 100 Points):
1. Active Status Filter: Compares only active issues (Pending Review, Assigned, In Progress).
   Ignores resolved or rejected past tickets.
2. Root Issue Match (40 Points):
   Matches core civic infrastructure category (e.g. ROAD_POTHOLE == ROAD_POTHOLE).
3. Location Comparison (30 Points):
   Normalized text address comparison + GPS coordinate proximity check (< 200m).
4. Text Similarity (30 Points):
   Lexical sequence similarity via SequenceMatcher (similarity * 30).

Threshold: Score >= 70 points flags a suspected duplicate.
"""

from difflib import SequenceMatcher
import re
from typing import List, Dict, Any, Optional, Tuple


ACTIVE_STATUSES = {
    "PENDING REVIEW",
    "PENDING_REVIEW",
    "SUBMITTED",
    "ASSIGNED",
    "IN PROGRESS",
    "IN_PROGRESS"
}


def normalize_text(text: Optional[str]) -> str:
    """Cleans, normalizes, and strips redundant punctuation and whitespace."""
    if not text:
        return ""
    clean = re.sub(r"[^\w\s]", " ", text.lower())
    return " ".join(clean.split())


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Computes normalized text sequence similarity ratio (0.0 to 1.0)."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    if not norm1 or not norm2:
        return 0.0
    return SequenceMatcher(None, norm1, norm2).ratio()


def compare_locations(loc1: str, loc2: str, lat1: Optional[float] = None, lng1: Optional[float] = None, lat2: Optional[float] = None, lng2: Optional[float] = None) -> Tuple[bool, float]:
    """
    Evaluates location equality using address text normalization and GPS coordinate proximity.
    Returns (is_match, confidence_factor between 0.0 and 1.0).
    """
    # 1. GPS Proximity Check (~250 meters)
    if lat1 is not None and lng1 is not None and lat2 is not None and lng2 is not None:
        dist = abs(lat1 - lat2) + abs(lng1 - lng2)
        if dist < 0.0025:  # Within ~250m
            return True, 1.0
        elif dist < 0.005:   # Within ~500m
            return True, 0.75

    # 2. Textual Location Match
    norm_loc1 = normalize_text(loc1)
    norm_loc2 = normalize_text(loc2)

    if not norm_loc1 or not norm_loc2:
        return False, 0.0

    if norm_loc1 == norm_loc2:
        return True, 1.0

    # Substring / partial road name matching
    sim = SequenceMatcher(None, norm_loc1, norm_loc2).ratio()
    if sim >= 0.75:
        return True, sim

    # Check shared landmark tokens (e.g. "government school", "market street", "elm st")
    words1 = set(norm_loc1.split())
    words2 = set(norm_loc2.split())
    common = words1.intersection(words2)
    significant_common = [w for w in common if len(w) > 3]

    if len(significant_common) >= 2:
        return True, 0.85

    return False, 0.0


def check_duplicate(new_complaint: Dict[str, Any], existing_complaints: List[Dict[str, Any]], threshold: float = 70.0) -> List[Dict[str, Any]]:
    """
    Executes multi-factor duplicate detection against existing complaints.
    
    new_complaint dict requires:
      - text: str (complaint description)
      - location: str (address)
      - root_issue: str (identified by nlp_analyzer)
      - lat, lng: Optional[float]
    """
    matches = []

    new_text = new_complaint.get("text") or new_complaint.get("complaint") or ""
    new_loc = new_complaint.get("location") or new_complaint.get("address") or ""
    new_root = new_complaint.get("root_issue") or ""
    new_lat = new_complaint.get("lat")
    new_lng = new_complaint.get("lng")

    for complaint in existing_complaints:
        raw_status = complaint.get("status", "").upper()
        # Step 1: Active status check (Skip resolved or rejected historical items)
        if raw_status not in ACTIVE_STATUSES:
            continue

        score = 0.0
        breakdown = {}

        # Step 2: Root Issue Comparison (40 Points)
        existing_root = (
            complaint.get("root_issue") or
            (complaint.get("triage_result", {}).get("root_issue")) or
            complaint.get("category") or
            ""
        )

        root_match = False
        if new_root and existing_root:
            norm_new_root = normalize_text(new_root)
            norm_ext_root = normalize_text(existing_root)
            if norm_new_root == norm_ext_root or norm_new_root in norm_ext_root or norm_ext_root in norm_new_root:
                root_match = True
                score += 40.0
                breakdown["root_issue_points"] = 40.0

        # Step 3: Location Comparison (30 Points)
        existing_loc = complaint.get("address") or complaint.get("location") or ""
        existing_lat = complaint.get("lat")
        existing_lng = complaint.get("lng")

        loc_match, loc_factor = compare_locations(
            new_loc, existing_loc,
            new_lat, new_lng,
            existing_lat, existing_lng
        )
        if loc_match:
            loc_points = 30.0 * loc_factor
            score += loc_points
            breakdown["location_points"] = round(loc_points, 1)

        # Step 4: Text Similarity (30 Points)
        existing_text = complaint.get("complaint") or complaint.get("complaint_text") or ""
        similarity = calculate_text_similarity(new_text, existing_text)
        text_points = similarity * 30.0
        score += text_points
        breakdown["text_similarity_points"] = round(text_points, 1)
        breakdown["similarity_ratio"] = round(similarity, 3)

        # Step 5: Duplicate Threshold Evaluation
        if score >= threshold:
            matches.append({
                "complaint_id": complaint.get("uid"),
                "status": complaint.get("status"),
                "duplicate_score": round(score, 1),
                "similarity": round(similarity, 2),
                "root_issue": existing_root or complaint.get("department"),
                "location": existing_loc,
                "text_snippet": existing_text[:120] + ("..." if len(existing_text) > 120 else ""),
                "score_breakdown": breakdown
            })

    # Sort descending by duplicate score
    matches.sort(key=lambda m: m["duplicate_score"], reverse=True)
    return matches

import uuid
import re
from typing import List
from sentence_transformers import SentenceTransformer, util

# ---------------- LOAD MULTILINGUAL MODEL ----------------
model = SentenceTransformer("sentence-transformers/distiluse-base-multilingual-cased-v1")

# ---------------- CRITICAL TERMS (STRONG MULTILINGUAL) ----------------
CRITICAL_TERMS = [

    # English
    "fire", "explosion", "blast", "gas leak",
    "collapse", "building collapse",
    "oxygen", "people trapped", "trapped",
    "rescue", "emergency", "life threatening",

    # Hindi
    "आग", "भीषण आग", "धमाका", "विस्फोट",
    "लोग फंसे", "अंदर फंसे", "आपात",
    "गैस रिसाव", "बिल्डिंग गिर",

    # Tamil
    "தீ", "பெரிய தீ", "வெடிப்பு",
    "மக்கள் சிக்கினர்", "உள்ளே சிக்கினர்",
    "கேஸ் லீக்", "கட்டிடம் இடிந்து",

    # Telugu
    "అగ్ని", "పేలుడు", "గ్యాస్ లీక్",
    "ప్రజలు చిక్కుకున్నారు"
]

INFO_TERMS = [
    "information", "update", "working hours",
    "inquiry", "process", "status"
]

# ---------------- SPAM DETECTION ----------------
def is_spam(text: str):
    text = text.strip()

    if len(text) < 6:
        return True

    if re.fullmatch(r"(.)\1{4,}", text):
        return True

    if re.fullmatch(r"\d{5,}", text):
        return True

    if not re.search(r"[a-zA-Zஅஆஇஈஉஊएऐओऔఅఆఇఈఉఊ]", text):
        return True

    return False


# ---------------- ROUTING ----------------
def route_department(text: str):
    t = text.lower()

    if any(word in t for word in ["fire", "blast", "explosion", "தீ", "आग", "అగ్ని"]):
        return "Fire Department"

    if any(word in t for word in ["water", "sewage", "drain", "tanker", "पानी"]):
        return "Water Department"

    if any(word in t for word in ["electric", "transformer", "power", "pole"]):
        return "Electricity Department"

    if any(word in t for word in ["hospital", "oxygen", "medical"]):
        return "Health Department"

    if any(word in t for word in ["road", "pothole", "collapse"]):
        return "Public Works Department"

    if any(word in t for word in ["garbage", "sanitation"]):
        return "Sanitation Department"

    return "General Administration"


# ---------------- CLUSTERING ----------------
def cluster_cases(complaints: List[str]):
    embeddings = model.encode(complaints, convert_to_tensor=True)

    cluster_map = {}
    cluster_id = 1
    assigned = {}

    for i in range(len(complaints)):
        if i in assigned:
            continue

        cluster_map[i] = cluster_id
        assigned[i] = cluster_id

        for j in range(i + 1, len(complaints)):
            sim = util.cos_sim(embeddings[i], embeddings[j]).item()
            if sim > 0.85:
                cluster_map[j] = cluster_id
                assigned[j] = cluster_id

        cluster_id += 1

    return cluster_map


# ---------------- MAIN ENGINE ----------------
def process_complaints(complaints: List[str]):

    cluster_map = cluster_cases(complaints)
    results = []

    for idx, text in enumerate(complaints):

        uid = "CB-" + uuid.uuid4().hex[:6].upper()

        if is_spam(text):
            results.append({
                "uid": uid,
                "complaint": text,
                "priority": "INVALID",
                "score": 0,
                "reason": ["Spam detected"],
                "department": "N/A",
                "cluster_id": cluster_map.get(idx),
                "rank": None
            })
            continue

        # ---------------- CRITICAL OVERRIDE (UNICODE SAFE) ----------------
        if any(term in text for term in CRITICAL_TERMS):
            priority = "CRITICAL"
            score = 98
            reason = ["Critical Safety Override"]

        # ---------------- INFORMATIONAL ----------------
        elif any(term in text.lower() for term in INFO_TERMS):
            priority = "LOW"
            score = 30
            reason = ["Informational request"]

        else:
            severity_refs = [
                "life threatening emergency",
                "serious public infrastructure failure",
                "minor inconvenience issue"
            ]

            ref_emb = model.encode(severity_refs, convert_to_tensor=True)
            text_emb = model.encode(text, convert_to_tensor=True)

            sims = util.cos_sim(text_emb, ref_emb)[0]

            critical_score = sims[0].item()
            high_score = sims[1].item()
            low_score = sims[2].item()

            max_score = max(critical_score, high_score, low_score)
            final_score = round(55 + (max_score * 40), 2)

            if max_score == critical_score and final_score > 80:
                priority = "HIGH"
            elif max_score == high_score:
                priority = "HIGH"
            elif final_score > 65:
                priority = "MEDIUM"
            else:
                priority = "LOW"

            score = final_score
            reason = ["Semantic Civic AI Analysis"]

        department = route_department(text)

        results.append({
            "uid": uid,
            "complaint": text,
            "priority": priority,
            "score": score,
            "reason": reason,
            "department": department,
            "cluster_id": cluster_map.get(idx),
            "rank": None
        })

    weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INVALID": 0}

    results.sort(key=lambda x: (weight[x["priority"]], x["score"]), reverse=True)

    for i, r in enumerate(results):
        r["rank"] = i + 1

    return {
        "total_complaints": len(complaints),
        "cluster_count": len(set(cluster_map.values())),
        "ranked_results": results
    }
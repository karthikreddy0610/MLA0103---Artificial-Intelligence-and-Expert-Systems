import pandas as pd
import re

# ==========================
# CityBrain Feature Builder
# Adds AI-ready attributes to 911_cleaned.csv
# ==========================

INPUT_PATH = r"C:\Users\HP\Desktop\City Brain\911_cleaned.csv"
OUTPUT_PATH = r"C:\Users\HP\Desktop\City Brain\911_citybrain_ready.csv"


def clean_text(s: str) -> str:
    """Basic text cleaning for NLP."""
    if pd.isna(s):
        return ""
    s = str(s).lower()
    s = re.sub(r"[^a-z0-9\s:/\-]", " ", s)  # keep basic separators
    s = re.sub(r"\s+", " ", s).strip()
    return s


def get_time_block(hour: int) -> str:
    if pd.isna(hour):
        return "Unknown"
    hour = int(hour)
    if 0 <= hour <= 5:
        return "LateNight"
    elif 6 <= hour <= 11:
        return "Morning"
    elif 12 <= hour <= 16:
        return "Afternoon"
    elif 17 <= hour <= 21:
        return "Evening"
    else:
        return "Night"


def get_shift(hour: int) -> str:
    """Simple 3-shift style grouping."""
    if pd.isna(hour):
        return "Unknown"
    hour = int(hour)
    if 6 <= hour < 14:
        return "Shift-1"
    elif 14 <= hour < 22:
        return "Shift-2"
    else:
        return "Shift-3"


def severity_from_text(category: str, subcat: str, desc: str) -> tuple:
    """
    Returns:
      severity_score (1-10),
      reason_keywords (comma separated),
      explain_reason (short text)
    """
    category = "" if pd.isna(category) else str(category).upper()
    subcat_clean = "" if pd.isna(subcat) else str(subcat).upper()
    desc_clean = "" if pd.isna(desc) else str(desc).upper()

    text = f"{subcat_clean} {desc_clean}"

    # 🔥 CityBrain severity keywords (customizable)
    keywords_critical = [
        "CARDIAC", "HEART", "UNCONSCIOUS", "NOT BREATHING", "BREATHING PROBLEM",
        "SEIZURE", "STROKE", "OVERDOSE", "SHOOTING", "GUN", "FIRE", "EXPLOSION",
        "CHOKING", "UNRESPONSIVE", "DROWNING", "CPR"
    ]

    keywords_high = [
        "CHEST PAIN", "DIFFICULTY BREATHING", "DIABETIC", "BLEEDING",
        "ASSAULT", "MVA", "ACCIDENT", "CRASH", "VEHICLE ACCIDENT",
        "GAS", "GAS LEAK", "ODOR", "ODOR OF GAS", "FALL VICTIM"
    ]

    keywords_medium = [
        "INJURY", "BACK PAINS", "DIZZINESS", "NAUSEA", "SICK",
        "HEAD INJURY", "FAINT", "SYNCOPAL", "ANIMAL BITE"
    ]

    hit = []
    score = 3  # base score

    # Base per category
    if category == "FIRE":
        score = 6
    elif category == "TRAFFIC":
        score = 5
    elif category == "EMS":
        score = 5

    # Keyword boosts
    for k in keywords_critical:
        if k in text:
            hit.append(k)
            score = max(score, 10)

    if score < 10:
        for k in keywords_high:
            if k in text:
                hit.append(k)
                score = max(score, 8)

    if score < 8:
        for k in keywords_medium:
            if k in text:
                hit.append(k)
                score = max(score, 6)

    # Explainability
    if len(hit) > 0:
        reason_keywords = ", ".join(sorted(set(hit))[:5])
        explain_reason = f"Priority boosted due to keywords: {reason_keywords}"
    else:
        reason_keywords = ""
        explain_reason = "Priority based on category pattern"

    # Clamp
    score = max(1, min(10, int(score)))
    return score, reason_keywords, explain_reason


def priority_from_score(score: int) -> str:
    if score >= 9:
        return "Critical"
    elif score >= 7:
        return "High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"


def department_routing(category: str) -> tuple:
    category = "" if pd.isna(category) else str(category).upper()

    if category == "EMS":
        return "Health/Ambulance", "Ambulance", "Send ambulance, provide medical assistance"
    elif category == "FIRE":
        return "Fire Department", "Fire Truck", "Dispatch fire unit, assess fire/gas risk"
    elif category == "TRAFFIC":
        return "Police/Traffic", "Traffic Patrol", "Dispatch police, manage traffic & safety"
    else:
        return "General", "Response Team", "Route to control room for manual assignment"


def estimate_response_time(score: int, hotspot_score: float) -> int:
    """
    Estimated response time (minutes), simple heuristic.
    Higher severity -> faster target
    More hotspot -> slightly longer due to congestion
    """
    base = 30

    if score >= 9:
        base = 8
    elif score >= 7:
        base = 12
    elif score >= 5:
        base = 18
    else:
        base = 25

    # hotspot effect (0 to ~100+)
    extra = int(min(10, hotspot_score // 50))
    return int(base + extra)


def resource_need_score(category: str, score: int) -> int:
    """
    Resource need (1-10).
    Fire incidents usually require more resources.
    """
    category = "" if pd.isna(category) else str(category).upper()
    base = score

    if category == "FIRE":
        base = min(10, base + 2)
    if category == "TRAFFIC" and score >= 7:
        base = min(10, base + 1)

    return int(max(1, min(10, base)))


def required_team(score: int) -> int:
    """
    Suggested number of units/team size.
    """
    if score >= 9:
        return 4
    elif score >= 7:
        return 3
    elif score >= 5:
        return 2
    else:
        return 1


def main():
    print("✅ Loading cleaned dataset...")
    df = pd.read_csv(INPUT_PATH)

    print("✅ Loaded:", df.shape)
    print(df.head(3))

    # Ensure timeStamp is datetime
    df["timeStamp"] = pd.to_datetime(df["timeStamp"], errors="coerce")

    # ----------------------------
    # 1) Add text columns for NLP
    # ----------------------------
    print("✅ Creating text_raw + text_clean + desc_length...")
    df["text_raw"] = (
        df["title"].astype(str) + " | " +
        df["desc"].astype(str) + " | " +
        df["twp"].astype(str) + " | " +
        df["addr"].astype(str)
    )
    df["text_clean"] = df["text_raw"].apply(clean_text)
    df["desc_length"] = df["desc"].astype(str).apply(len)

    # ----------------------------
    # 2) DayType / TimeBlock / Shift
    # ----------------------------
    print("✅ Creating day_type + time_block + shift...")
    df["DayName"] = df["timeStamp"].dt.day_name()
    df["day_type"] = df["DayName"].apply(
        lambda x: "Weekend" if x in ["Saturday", "Sunday"] else "Weekday"
    )
    df["Hour"] = df["timeStamp"].dt.hour
    df["time_block"] = df["Hour"].apply(get_time_block)
    df["shift"] = df["Hour"].apply(get_shift)

    # ----------------------------
    # 3) geo_hash + time_bucket + incident_id
    # ----------------------------
    print("✅ Creating geo_hash + time_bucket_10min + incident_id...")
    df["geo_hash"] = (
        df["lat"].round(3).astype(str) + "_" + df["lng"].round(3).astype(str)
    )
    df["time_bucket_10min"] = df["timeStamp"].dt.floor("10min")

    df["incident_id"] = (
        df["Category"].astype(str) + "_" +
        df["geo_hash"].astype(str) + "_" +
        df["time_bucket_10min"].astype(str)
    )

    # Duplicate candidate (same incident_id repeated)
    incident_counts = df["incident_id"].value_counts()
    df["incident_call_count"] = df["incident_id"].map(incident_counts)
    df["is_duplicate_candidate"] = df["incident_call_count"].apply(lambda x: 1 if x > 1 else 0)

    # ----------------------------
    # 4) Hotspot score (geo frequency)
    # ----------------------------
    print("✅ Creating hotspot_score + is_hotspot...")
    geo_counts = df["geo_hash"].value_counts()
    df["hotspot_score"] = df["geo_hash"].map(geo_counts)

    # Hotspot: Top 5% locations
    threshold = df["hotspot_score"].quantile(0.95)
    df["is_hotspot"] = df["hotspot_score"].apply(lambda x: 1 if x >= threshold else 0)

    # ----------------------------
    # 5) Severity, Priority, Explainability
    # ----------------------------
    print("✅ Creating severity_score + priority_level + explain_reason...")
    sev_out = df.apply(
        lambda row: severity_from_text(row.get("Category"), row.get("SubCategory"), row.get("desc")),
        axis=1
    )

    df["severity_score"] = [x[0] for x in sev_out]
    df["reason_keywords"] = [x[1] for x in sev_out]
    df["explain_reason"] = [x[2] for x in sev_out]
    df["priority_level"] = df["severity_score"].apply(priority_from_score)

    # ----------------------------
    # 6) Department Routing + Recommendations
    # ----------------------------
    print("✅ Creating department + suggested_unit + recommended_action...")
    dept_out = df["Category"].apply(department_routing)
    df["department"] = [x[0] for x in dept_out]
    df["suggested_unit"] = [x[1] for x in dept_out]
    df["recommended_action"] = [x[2] for x in dept_out]

    # ----------------------------
    # 7) Estimated response time + resource allocation attributes
    # ----------------------------
    print("✅ Creating estimated_response_time_min + resource_need_score + required_team...")
    df["estimated_response_time_min"] = df.apply(
        lambda row: estimate_response_time(row["severity_score"], row["hotspot_score"]),
        axis=1
    )
    df["resource_need_score"] = df.apply(
        lambda row: resource_need_score(row["Category"], row["severity_score"]),
        axis=1
    )
    df["required_team"] = df["severity_score"].apply(required_team)

    # ----------------------------
    # 8) Final Save
    # ----------------------------
    print("✅ Saving CityBrain ready dataset...")
    df.to_csv(OUTPUT_PATH, index=False)

    print("\n✅ DONE ✅")
    print("Saved:", OUTPUT_PATH)
    print("Final Shape:", df.shape)

    print("\n📌 Sample columns:")
    print(df.columns)

    print("\n📌 Priority Distribution:")
    print(df["priority_level"].value_counts())


if __name__ == "__main__":
    main()

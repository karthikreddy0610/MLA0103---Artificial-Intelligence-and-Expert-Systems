"""
CityBrain Intelligent Priority & Municipal Department Classification Engine
=============================================================================
Context-Aware Entity, Complication & Impact Analysis:
1. Root Problem Comprehension: Identifies the responsible municipal authority based
   on the core infrastructure/civic asset (PWD, Water, Electricity, Sanitation, Police, etc.),
   never confusing incidental injury mentions with ambulance dispatch.
2. Multi-Factor Complication Analysis: Evaluates 5 dimensions of real-world complications:
   - Life Hazard & Bodily Harm (Active fires, collapses, gas leaks, live wires, cardiac crises)
   - Vulnerable Location Multipliers (Schools, hospitals, elderly homes, transit hubs)
   - Scale & Area Magnitude (Entire neighborhood, arterial highway, flooding homes)
   - Urgency Escalation & Persistence (Active worsening, recurrent accidents, days unaddressed)
   - Routine & Cosmetic Dampeners (Single bulb, minor drip, paint, billing/info inquiries)
3. Calibrated Priority Decision:
   CRITICAL | HIGH | MEDIUM | LOW with explainable rationale and dispatch SLA.
"""

import re
from typing import Dict, List, Tuple, Optional, Any

# Domain Routing Taxonomies
CATEGORY_TO_DEPT = {
    "roads": "Public Works Department (PWD)",
    "water": "Water Supply & Sewerage Board",
    "electricity": "Electricity & Power Board",
    "sanitation": "Public Health & Sanitation Department",
    "ambulance": "Emergency Healthcare & Ambulance Services",
    "police": "Police & Law Enforcement",
    "emergency": "Fire & Rescue Services",
    "general": "General Administration"
}

DEPT_INTENTS = {
    "Fire & Rescue Services": "Disaster & Fire Rescue Emergency",
    "Emergency Healthcare & Ambulance Services": "Acute Medical Life-Risk & Healthcare Dispatch",
    "Police & Law Enforcement": "Public Safety & Law Enforcement Threat",
    "Electricity & Power Board": "Electrical Grid & Power Infrastructure",
    "Public Works Department (PWD)": "Roads, Bridges & Civil Infrastructure (PWD)",
    "Water Supply & Sewerage Board": "Water Supply Distribution & Sewerage Network",
    "Public Health & Sanitation Department": "Public Health, Sanitation & Solid Waste Management",
    "Public Transport & Transit Authority": "Public Transit & Fleet Operations",
    "General Administration": "Municipal Administration & Civic Governance"
}


class IntelligentPriorityEngine:
    """
    Intelligent Priority & Department Classification Engine.
    Accurately understands the root problem and its complications before deciding priority.
    """

    def classify_department(self, text: str, category: Optional[str] = None) -> Tuple[str, float]:
        """
        Determines the correct municipal department responsible for addressing the root problem.
        Returns (Department_Name, Confidence_Score).
        """
        t = (text or "").lower()
        cat = (category or "").lower().strip()

        # 1. FIRE, DISASTER & STRUCTURAL COLLAPSE
        if (re.search(r"\b(fire|flames?|blaze|explosion|blast|gas leak|cylinder leak|cylinder blast|building collaps\w*|wall collaps\w*|bridge collaps\w*|landslide|drowning|drowned|mantalu|agni|koolipoindi)\b", t) or re.search(r"(మంటలు|అగ్ని|అగ్నిప్రమాదం|గ్యాస్ లీక్|సిలిండర్ పేలింది)", t)):
            # If the mention of fire is incidental to snapped wires / electrical sparks, route to Electricity & Power Board
            if not (re.search(r"\b(wire|cable|transformer|power line|electric pole|theega|theegalu|live wire)\b", t) and not re.search(r"\b(active fire|building on fire|house on fire|flames|blaze|explosion|cylinder blast)\b", t)):
                return "Fire & Rescue Services", 0.98

        # 2. ELECTRICITY, POWER & HIGH VOLTAGE
        if re.search(r"\b(electric\w*|power|transformer|live wire|hanging wire|open cable|high voltage|short circuit|blackout|voltage|street lights?|electric pole|electrocution|sparks?|sparking|power cut|load shedding|meter box|current|carant|vidyuth|theega|theegalu|thegipoyindi|tegindi|lightlu|cheekati|velagadam ledu|velagatledu|current poindi|current ledu)\b", t) or re.search(r"(కరెంట్|విద్యుత్|తీగ|తీగలు|వైర్|ట్రాన్స్‌ఫార్మర్|లైట్లు|స్ట్రీట్ లైట్లు|వెలగడం లేదు|వెలగట్లేదు|చీకటి|పవర్ కట్|కరెంట్ పోయింది|స్పార్క్స్)", t):
            return "Electricity & Power Board", 0.95

        # 3. WATER SUPPLY & SEWERAGE
        if re.search(r"\b(water|pipe(line)?|leak\w*|burst|taps?|sewers?|sewerage|drains?|drainage|gutters?|flooding|muddy water|dirty water|no water|water supply|drinking water|borewell|water tank|neellu|neeru|manchi neellu|manchineellu|thaguneeru|pagilipoindi|leakej|vrudha|ravatledu|ravadam ledu|raledu|muriki neellu|kalushitha|murugu|kaaluva|kaluva|muruguneeru|kampu|durvaasana|mootha ledu|open manhole)\b", t) or re.search(r"(నీళ్లు|నీరు|మంచినీళ్లు|మంచినీటి|తాగునీరు|పైపు|పైప్‌లైన్|పగిలిపోయింది|లీకేజ్|వృధా|రావడం లేదు|రావట్లేదు|మురుగు|కాలువ|డ్రైనేజీ|డ్రైనేజ్|మ్యాన్‌హోల్|మ్యాన్ హోల్|మూత లేదు|కంపు|మురుగునీరు)", t):
            return "Water Supply & Sewerage Board", 0.95

        # 4. ROADS & INFRASTRUCTURE (PWD)
        if re.search(r"\b(roads?|potholes?|traffic|signals?|traffic light|bridges?|flyovers?|footpaths?|sidewalks?|manholes?|sinkholes?|craters?|tar|asphalt|pavement|cave[- ]?in|caved in|road divider|gunta|guntalu|gothulu|rahadari|paadaipoindi|padaipoyindi|debbathindi|guntalo)\b", t) or re.search(r"(గుంత|గుంతలు|గోతులు|రహదారి|పాడైపోయింది|దెబ్బతింది)", t):
            return "Public Works Department (PWD)", 0.95

        # 5. SANITATION & SOLID WASTE
        if re.search(r"\b(garbage|trash|waste|dumps?|dumping|dustbins?|stench|smell|foul|filth|dead animal|carcass|sanitation|sweeper|litter|debris|drain smell|unhygienic|chetha|chethakuppalu|kuppalu|perukupoindi|durvaasana|vasana|dhomalu|chachina janthuvu|clean cheyaledu|theeyatledu)\b", t) or re.search(r"(చెత్త|చెత్తకుప్పలు|కుప్పలు|పేరుకుపోయింది|దుర్వాసన|వాసన|దోమలు|చచ్చిన జంతువు|కళేబరం)", t):
            return "Public Health & Sanitation Department", 0.94

        # 6. POLICE, CRIME & PUBLIC SAFETY
        if re.search(r"\b(police|theft|thief|robber\w*|burglary|assault|fight|violence|harass\w*|stolen|eve[- ]teasing|drugs?|weapon|murder|gunshot|stabbing|knife|gang|crime|illegal|threat|rowdies|dongathanam|godava|daadi|bhayam|rowdielu|bedirimpu)\b", t) or re.search(r"(దొంగతనం|గొడవ|దాడి|భయం|రౌడీలు|బెదిరింపు)", t):
            return "Police & Law Enforcement", 0.94

        # 7. MEDICAL & AMBULANCE (When primary intent is medical rescue or clinical transport)
        if re.search(r"\b(ambulance|hospital|patient|doctor|clinic|medic(al|ine)?|paramedic|healthcare|icu|first aid|casualty|dengue|malaria|maternity)\b", t):
            return "Emergency Healthcare & Ambulance Services", 0.92

        # 8. PUBLIC TRANSPORT & TRANSIT
        if re.search(r"\b(buses?|metro|transit|trains?|bus stop|auto rickshaw|bus fare|depot)\b", t):
            return "Public Transport & Transit Authority", 0.90

        # 9. CATEGORY FALLBACK
        if cat in CATEGORY_TO_DEPT:
            return CATEGORY_TO_DEPT[cat], 0.85
        for key, dept in CATEGORY_TO_DEPT.items():
            if key in cat:
                return dept, 0.85

        return "General Administration", 0.65

    def identify_root_civic_asset(self, text: str, department: str) -> str:
        """Identifies the primary physical infrastructure asset or civic subject."""
        t = (text or "").lower()
        if re.search(r"\b(open manhole|deep manhole|sinkhole|cave[- ]?in|mootha ledu|open ga undi)\b", t) or re.search(r"(మ్యాన్‌హోల్|మ్యాన్ హోల్|మూత లేదు)", t):
            return "Severe Roadway Structural Hazard (Open Manhole / Sinkhole)"
        if re.search(r"\b(potholes?|craters?|road damage|broken road|tar|asphalt|gunta|guntalu|gothulu|paadaipoindi|padaipoyindi|debbathindi)\b", t) or re.search(r"(గుంత|గుంతలు|గోతులు|పాడైపోయింది|దెబ్బతింది)", t):
            return "Road Infrastructure Disrepair (Pothole / Crater)"
        if re.search(r"\b(bridges?|flyovers?)\b", t):
            return "Major Civil Structure (Bridge / Flyover Disrepair)"
        if re.search(r"\b(signals?|traffic light)\b", t):
            return "Traffic Regulation Asset (Signal / Light Failure)"
        if re.search(r"\b(footpaths?|sidewalks?)\b", t):
            return "Pedestrian Infrastructure (Damaged Footpath)"
        if re.search(r"\b(live wire|hanging wire|open cable|high voltage|sparking wire|snapped wire|wire snapped|electric wire|theega|theegalu|thegipoyindi|tegindi)\b", t) or re.search(r"(తీగ|తీగలు|స్పార్క్స్|షాక్)", t):
            return "High-Voltage Lethal Wire Hazard"
        if re.search(r"\b(transformers?|exploding transformer|sparking transformer)\b", t) or "ట్రాన్స్‌ఫార్మర్" in t:
            return "Power Grid Transformer Malfunction"
        if re.search(r"\b(street lights?|bulb|lightlu|velagadam ledu|velagatledu)\b", t) or re.search(r"(స్ట్రీట్ లైట్లు|లైట్లు|వెలగడం లేదు|వెలగట్లేదు)", t):
            return "Municipal Street Lighting Asset"
        if re.search(r"\b(blackout|power cut|load shedding|current poindi|current ledu)\b", t) or re.search(r"(పవర్ కట్|కరెంట్ పోయింది|కరెంట్ లేదు)", t):
            return "Area Grid Power Outage"
        if re.search(r"\b(pipe(line)?|burst pipe|water leak|pipe burst|main burst|pagilipoindi|vrudha)\b", t) or re.search(r"(పైపు|పగిలిపోయింది|వృధా)", t):
            return "Water Distribution Pipeline Rupture"
        if re.search(r"\b(sewers?|sewerage|drains?|drainage|gutters?|murugu|kaaluva|kaluva|muruguneeru)\b", t) or re.search(r"(మురుగు|కాలువ|డ్రైనేజీ|డ్రైనేజ్)", t):
            return "Sewerage & Drainage Network Choke / Overflow"
        if re.search(r"\b(drinking water|dirty water|muddy water|contaminated|muriki neellu|kalushitha)\b", t) or re.search(r"(మురికి నీళ్లు|కలుషిత)", t):
            return "Drinking Water Contamination Hazard"
        if re.search(r"\b(no water|low pressure|water pressure|ravadam ledu|ravatledu)\b", t) or re.search(r"(నీళ్లు రావడం లేదు|రావట్లేదు|నీరు లేదు)", t):
            return "Municipal Water Supply Scarcity"
        if re.search(r"\b(dead animal|carcass|chachina|janthuvu)\b", t) or re.search(r"(చచ్చిన జంతువు|కళేబరం)", t):
            return "Public Health Hazard (Animal Carcass)"
        if re.search(r"\b(garbage|trash|waste|dumps?|dustbins?|chetha|chethakuppalu|kuppalu|perukupoindi|durvaasana)\b", t) or re.search(r"(చెత్త|చెత్తకుప్పలు|కుప్పలు|పేరుకుపోయింది|దుర్వాసన)", t):
            return "Solid Waste Accumulation & Sanitation Hazard"
        if re.search(r"\b(fire|flames?|blaze|explosion|gas leak|mantalu|agni)\b", t) or re.search(r"(మంటలు|అగ్ని|అగ్నిప్రమాదం)", t):
            return "Active Fire / Explosion / Disaster Hazard"
        if re.search(r"\b(cardiac|heart attack|stroke|ambulance|unconscious)\b", t):
            return "Emergency Healthcare / Critical Patient Transport"
        if re.search(r"\b(theft|burglary|robbery|assault|crime|dongathanam|godava|daadi)\b", t) or re.search(r"(దొంగతనం|గొడవ|దాడి)", t):
            return "Law & Order Infraction / Public Safety Threat"

        return f"{department} Operational Maintenance"

    def analyze_complications(self, text: str, department: str) -> Dict[str, Any]:
        """
        Deep multi-factor complication analysis:
        1. Life Hazard & Bodily Danger (0-10)
        2. Vulnerable Locations & Demographic Sensitivity (0-10)
        3. Impact Scale & Geographic Disruption (0-10)
        4. Urgency & Worsening Escalation (0-10)
        5. Routine / Cosmetic / Administrative Dampener (0-10)
        """
        t = (text or "").lower()

        detected_complications: List[str] = []
        life_hazard = 0
        vulnerability = 0
        scale_impact = 0
        urgency_escalation = 0
        routine_dampener = 0

        # --- Dimension 1: Life Hazard & Bodily Danger ---
        if re.search(r"\b(fire|flames?|blaze|explosion|blast|gas leak|cylinder blast|building collaps\w*|wall collaps\w*|drowning|people trapped|trapped inside)\b", t):
            life_hazard = 10
            detected_complications.append("Active Disaster / Physical Collapse / Casualty Risk")
        elif re.search(r"\b(heart attack|cardiac arrest|stroke|unconscious|not breathing|heavy bleeding|fatal injury|dying|choking)\b", t):
            life_hazard = 10
            detected_complications.append("Acute Life-Threatening Medical Crisis")
        elif re.search(r"\b(weapon|gun|knife|murder|stabbing|armed robbery|shoot(ing)?)\b", t):
            life_hazard = 9
            detected_complications.append("Armed Violent Crime / Active Threat to Life")
        elif re.search(r"\b(live wire|hanging wire|open cable|electrocution|exploding transformer|high voltage|sparking wire|snapped wire|theega|theegalu|thegipoyindi|tegindi)\b", t) or re.search(r"(తీగ|తీగలు|స్పార్క్స్|షాక్)", t):
            life_hazard = 9
            detected_complications.append("Exposed Lethal High-Voltage Electrical Hazard")
        elif re.search(r"\b(open manhole|deep manhole|sinkhole|bridge crack|cave[- ]?in|caved in|mootha ledu|open ga undi)\b", t) or re.search(r"(మ్యాన్‌హోల్|మ్యాన్ హోల్|మూత లేదు)", t):
            life_hazard = 8
            detected_complications.append("Lethal Roadway Collapse / Deep Uncovered Manhole")
        elif re.search(r"\b(people are getting injured|people getting injured|severe accident|fatal accident|fell|fell into|injured|bike slipped|slipped|broken bones?|blood|crashed|padipotunnaru|padipotunnayi|padipothunnaru)\b", t) or re.search(r"(పడిపోతున్నారు|పడిపోతున్నాయి|ప్రమాదం|గాయపడ్డారు)", t):
            life_hazard = 7
            detected_complications.append("Active Bodily Injury & Physical Accidents Reported")

        # --- Dimension 2: Vulnerable Location & Demographics ---
        if re.search(r"\b(school|high school|elementary school|kindergarten|primary school|daycare|college|students?|children|kids|pillalu)\b", t) or "పిల్లలు" in t:
            vulnerability = max(vulnerability, 9)
            detected_complications.append("High Vulnerability Zone: School / Children Proximity")
        if re.search(r"\b(hospital|clinic|nursing home|icu|emergency room|patients?|old age home|elderly|pregnant)\b", t) or "ఆసుపత్రి" in t:
            vulnerability = max(vulnerability, 9)
            detected_complications.append("Sensitive Zone: Hospital / Patient / Healthcare Facility")
        if re.search(r"\b(bus stand|bus stop|metro station|railway station|train station|crowded market|bazaar|junction|pedestrian crossing)\b", t):
            vulnerability = max(vulnerability, 6)
            detected_complications.append("High-Density Public Transit / Pedestrian Corridor")

        # --- Dimension 3: Scale & Geographic Disruption ---
        if re.search(r"\b(entire (area|neighborhood|colony|ward|street|road|block)|whole (street|neighborhood|colony|area)|all houses|multiple (houses|homes|families|apartments)|hundreds of families|multiple families)\b", t):
            scale_impact = max(scale_impact, 8)
            detected_complications.append("Widespread Impact: Entire Corridor / Multiple Residences Affected")
        if re.search(r"\b(highway|expressway|arterial|main road|key junction|traffic (completely )?blocked|gridlock|prayaanam kastam)\b", t) or "కష్టంగా" in t or "జామ్" in t:
            scale_impact = max(scale_impact, 8)
            detected_complications.append("Critical Transit Disruption: Arterial Corridor / Highway Blocked")
        if re.search(r"\b(flooding|flood|submerged|houses|homes|illaloki|illoki)\b", t) or "ఇళ్లలోకి" in t:
            if re.search(r"\b(flooding (the entire|the road|all|multiple)|water entered|submerged|flooding inside|illaloki|illoki)\b", t) or "ఇళ్లలోకి" in t:
                scale_impact = max(scale_impact, 8)
                detected_complications.append("Inundation Risk: Flooding Roadway & Infiltrating Dwellings")
        if re.search(r"\b(drinking water (is )?(contaminated|muddy|black|smelling|poisonous)|sewage mixed with drinking|kalushitha|muriki neellu)\b", t) or "మురికి నీళ్లు" in t:
            scale_impact = max(scale_impact, 9)
            detected_complications.append("Critical Health Risk: Contaminated Drinking Water Supply")

        # --- Dimension 4: Urgency & Escalation ---
        if re.search(r"\b(spreading|sparks flying|getting worse|rapidly rising|crater getting bigger|multiple vehicles damaged)\b", t):
            urgency_escalation = max(urgency_escalation, 8)
            detected_complications.append("Active Escalation: Condition Rapidly Deteriorating")
        if re.search(r"\b(for (\d+|several|many) (days|weeks)|past month|repeated complaints|no action taken|still not fixed)\b", t):
            urgency_escalation = max(urgency_escalation, 6)
            detected_complications.append("Persistent Chronic Grievance: Multi-Day Neglected Failure")
        if re.search(r"\b(dead animal|carcass|rotting|maggots|dengue|malaria hotspot|dhomalu|kampu|durvaasana)\b", t) or re.search(r"(దోమలు|కంపు|దుర్వాసన)", t):
            urgency_escalation = max(urgency_escalation, 7)
            detected_complications.append("Epidemiological Threat: Rotting Vector / Disease Risk")

        # --- Dimension 5: Routine / Cosmetic / Administrative Dampeners ---
        if re.search(r"\b(name board|signboard|faded|peeling paint|painting|park bench|flower bed|grass cutting|tree pruning)\b", t) and life_hazard == 0:
            routine_dampener = max(routine_dampener, 9)
            detected_complications.append("Cosmetic Aesthetic Disrepair: Non-Hazardous Maintenance")
        if re.search(r"\b(receipt|tax enquiry|bill enquiry|status enquiry|procedure|fee|feedback|suggestion|working hours)\b", t) and life_hazard == 0:
            routine_dampener = max(routine_dampener, 9)
            detected_complications.append("Administrative / Informational Query")
        if re.search(r"\b(single (bulb|street light)|one street light|dim light|flickering|flickering bulb|tap (is )?dripping|slight drip|minor leak|small pothole)\b", t) and life_hazard == 0 and vulnerability < 5:
            routine_dampener = max(routine_dampener, 6)
            detected_complications.append("Localized Isolated Defect: Routine Single-Asset Maintenance")

        # Aggregate Complication Score (0 - 100)
        raw_score = (
            life_hazard * 4.5 +
            vulnerability * 2.2 +
            scale_impact * 2.0 +
            urgency_escalation * 1.5 -
            routine_dampener * 3.5
        )
        final_score = int(max(5, min(100, round(raw_score))))

        return {
            "score": final_score,
            "life_hazard": life_hazard,
            "vulnerability": vulnerability,
            "scale_impact": scale_impact,
            "urgency_escalation": urgency_escalation,
            "routine_dampener": routine_dampener,
            "detected": detected_complications
        }

    def assess_priority(self, text: str, department: str) -> Tuple[str, str, Dict[str, Any]]:
        """
        Synthesizes the problem understanding and complication analysis into an actionable priority:
        CRITICAL | HIGH | MEDIUM | LOW.
        Returns (Priority, Decision_Reason, Complications_Dict).
        """
        complications = self.analyze_complications(text, department)
        life_h = complications["life_hazard"]
        vuln = complications["vulnerability"]
        scale = complications["scale_impact"]
        damp = complications["routine_dampener"]
        comp_score = complications["score"]

        # ---------------- LEVEL 1: CRITICAL (Imminent Hazard / Active Life Risk) ----------------
        if life_h >= 8:
            reasons = [c for c in complications["detected"] if any(k in c for k in ["Lethal", "Disaster", "Medical", "Armed", "Casualty"])]
            reason_text = reasons[0] if reasons else "Imminent active threat to life and public safety"
            return "CRITICAL", f"Critical Hazard: {reason_text}", complications

        if life_h >= 6 and vuln >= 6:
            return "CRITICAL", "Critical Hazard: Exposed physical danger in high-vulnerability school or hospital zone", complications

        if life_h >= 6 and scale >= 7:
            return "CRITICAL", "Critical Hazard: Severe compound hazard with widespread public endangerment", complications

        # ---------------- LEVEL 2: HIGH (Major Disruption / Severe Public Hazard) ----------------
        if life_h >= 6:
            return "HIGH", "High Priority: Recurrent injury risk or physical trauma reported", complications

        if scale >= 7:
            return "HIGH", "High Priority: Extensive public impact across entire neighborhood or arterial corridor", complications

        if vuln >= 7:
            return "HIGH", "High Priority: Infrastructure disrepair directly compromising school or healthcare access", complications

        if any(any(k in c for k in ["Contaminated", "Inundation", "Epidemiological", "Blocked"]) for c in complications["detected"]):
            return "HIGH", "High Priority: Severe environmental health hazard or vital corridor blockage", complications

        if department in ["Police & Law Enforcement"]:
            return "HIGH", "High Priority: Active law and order infraction requiring police intervention", complications

        if comp_score >= 50:
            return "HIGH", "High Priority: Compound infrastructure complication with elevated public risk", complications

        # ---------------- LEVEL 4: LOW (Cosmetic Disrepair / General Inquiries) ----------------
        if damp >= 7 and life_h == 0 and scale <= 2 and vuln <= 3:
            if any("Administrative" in c for c in complications["detected"]):
                return "LOW", "Routine Inquiry: Administrative query or public information request", complications
            return "LOW", "Cosmetic Maintenance: Non-hazardous aesthetic repair or minor park upkeep", complications

        # ---------------- LEVEL 3: MEDIUM (Standard Routine Maintenance) ----------------
        # Standard default when there is no life risk and no high complication
        return "MEDIUM", "Standard Operational Maintenance: Routine ward-level civic maintenance", complications

    def analyze(self, text: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        AI Triage Engine (Steps 1 -> 5):
        STEP 1 -> Complaint Understanding & Semantic Extraction
        STEP 2 -> Root Civic Asset & Problem Identification
        STEP 3 -> Municipal Department Routing
        STEP 4 -> Complication & Contextual Severity Assessment
        STEP 5 -> Priority Decision with Operational SLA
        """
        clean_text = (text or "").strip()
        if not clean_text:
            return {
                "root_issue": "Awaiting Incident Details",
                "recommended_department": "General Administration",
                "priority": "MEDIUM",
                "explanation": "No text provided for evaluation.",
                "status": "PENDING REVIEW",
                "department": "General Administration",
                "intent": "Awaiting Incident Details",
                "confidence": 0.0,
                "reason": "No text provided",
                "sla": "Standard Queue",
                "complications": {
                    "score": 0,
                    "detected": ["Awaiting input"]
                },
                "recommendation": "Enter incident details to trigger automated municipal triage."
            }

        # Step 1, 2, 3: Department Recommendation & Root Civic Asset
        department, confidence = self.classify_department(clean_text, category)
        root_asset = self.identify_root_civic_asset(clean_text, department)

        # Step 4 & 5: Complication Analysis & Priority Decision
        priority, reason, complications = self.assess_priority(clean_text, department)
        intent = DEPT_INTENTS.get(department, "Municipal Service Routing")

        # Tailored SLA and dispatch recommendations
        if priority == "CRITICAL":
            sla = "< 30 Minutes"
            recommendation = f"Immediate Emergency Dispatch: Alert {department} Rapid Action Team with {sla} SLA. {reason}."
        elif priority == "HIGH":
            sla = "4 Hours"
            recommendation = f"High-Priority Work Order: Route ticket to {department} field division with {sla} SLA. {reason}."
        elif priority == "MEDIUM":
            sla = "24-48 Hours"
            recommendation = f"Standard Maintenance Queue: Assign to {department} local ward supervisor with {sla} SLA."
        else:
            sla = "5-7 Days"
            recommendation = f"Routine Processing: Route to {department} administrative queue with {sla} SLA."

        return {
            "root_issue": root_asset,
            "recommended_department": department,
            "priority": priority,
            "explanation": reason,
            "status": "PENDING REVIEW",
            "sla": sla,
            "recommendation": recommendation,
            "complications": complications,
            "steps": {
                "step_1_complaint_understanding": {
                    "summary": f"Analyzed incident semantics: Identified '{root_asset}' under {department}.",
                    "intent": intent,
                    "confidence": round(confidence, 2)
                },
                "step_2_root_civic_asset": root_asset,
                "step_3_department_recommendation": department,
                "step_4_complications_and_impact": {
                    "complication_score": complications["score"],
                    "complications_detected": complications["detected"],
                    "severity_assessment": reason
                },
                "step_5_priority_assessment": priority
            },
            # Backwards compatibility fields
            "department": department,
            "intent": intent,
            "confidence": round(confidence, 2),
            "reason": reason,
            "engine": "CityBrain Intelligent AI Triage Engine (v3.2)"
        }


# Global singleton instance
priority_engine = IntelligentPriorityEngine()
nlp_analyzer = priority_engine

def analyze_prompt(text: str, category: Optional[str] = None) -> Dict[str, Any]:
    """Helper function to analyze an incident prompt."""
    return priority_engine.analyze(text, category)

def get_priority_and_department(text: str, category: Optional[str] = None) -> Tuple[str, str]:
    """Helper function returning (priority, department) tuple."""
    res = priority_engine.analyze(text, category)
    return res["priority"], res["department"]

def synthesize_civic_meaning(literal_en: str, raw_orig: str = "") -> str:
    """
    Translates raw colloquial, emotional, regional (Telugu, Hindi, Tamil, Kannada),
    or machine-translated citizen speech into a formal, high-clarity municipal civic statement
    reflecting the true physical MEANING, civic defect, and hazard rather than literal word-by-word phrasing.
    """
    text_primary = (literal_en or "").strip()
    text_orig = (raw_orig or "").strip()
    if not text_primary and not text_orig:
        return ""

    combined = f"{text_primary} {text_orig}".lower().strip()

    # 1. CORE CIVIC ISSUE IDENTIFICATION
    defect = ""
    dept_action = ""

    # Check for Pipe / Water Leak / Outage vs Pothole
    is_water_term = bool(
        re.search(r"\b(water|pipe|pipeline|leak\w*|burst|taps?|borewell|water supply|drinking water|potable water)\b", combined) or
        re.search(r"\b(neellu|neeru|manchi neellu|manchineellu|thaguneeru|taguneeru|pagilipoindi|pagilipoyindi|leakej|vrudha|ravatledu|ravadam ledu|ravadamledhu|raledu|muriki neellu|kalushitha)\b", combined) or
        re.search(r"(నీళ్లు|నీరు|మంచినీళ్లు|మంచినీటి|తాగునీరు|పైపు|పైప్‌లైన్|పగిలిపోయింది|లీకేజ్|వృధా|రావడం లేదు|రావట్లేదు|మురికి నీళ్లు|కలుషిత)", combined)
    )

    is_drainage_term = bool(
        re.search(r"\b(drain|drainage|sewer|sewerage|gutter|gutters|manhole|sewage|foul water|sludge)\b", combined) or
        re.search(r"\b(murugu|kaaluva|kaluva|muruguneeru|kampu|durvaasana|mootha ledu|open manhole)\b", combined) or
        re.search(r"(మురుగు|కాలువ|డ్రైనేజీ|డ్రైనేజ్|మ్యాన్‌హోల్|మ్యాన్ హోల్|మూత లేదు|కంపు|మురుగునీరు)", combined)
    )

    is_pothole_term = bool(
        re.search(r"\b(potholes?|craters?|sinkholes?|cave[- ]?in|caved in|road collapse|cratered road)\b", combined) or
        re.search(r"\b(gunta|guntalu|gothulu|guntalo)\b", combined) or
        re.search(r"(గుంత|గుంతలు|గోతులు)", combined) or
        ((re.search(r"\b(road|roads|rahadari)\b", combined) or "రోడ్డు" in combined or "రహదారి" in combined) and
         (re.search(r"\b(damage|damaged|broken|destroyed|collapse|collapsed|paadaipoindi|padaipoyindi|debbathindi|guntalu paddayi)\b", combined) or
          re.search(r"(పాడైపోయింది|దెబ్బతింది|కూలిపోయింది)", combined)))
    ) and not (is_water_term and not re.search(r"\b(potholes?|gunta|గుంత)\b", combined))

    is_electric_term = bool(
        re.search(r"\b(electric\w*|power|transformer|live wire|hanging wire|open cable|high voltage|sparking|snapped wire|power cut|street lights?|streetlights?|bulb|blackout)\b", combined) or
        re.search(r"\b(current|carant|vidyuth|theega|theegalu|wire|thegipoyindi|tegindi|transformer|lightlu|street light|velagadam ledu|velagatledu|cheekati|cheekatiga|power cut|current poindi|current ledu)\b", combined) or
        re.search(r"(కరెంట్|విద్యుత్|తీగ|తీగలు|వైర్|ట్రాన్స్‌ఫార్మర్|లైట్లు|స్ట్రీట్ లైట్లు|వెలగడం లేదు|వెలగట్లేదు|చీకటి|పవర్ కట్|కరెంట్ పోయింది|స్పార్క్స్)", combined)
    )

    is_garbage_term = bool(
        re.search(r"\b(garbage|trash|waste|dump|dumps|dustbin|dustbins|stench|smell|dead animal|carcass|sanitation|debris)\b", combined) or
        re.search(r"\b(chetha|chethakuppalu|kuppalu|perukupoindi|durvaasana|vasana|dhomalu|chachina janthuvu|clean cheyaledu|theeyatledu)\b", combined) or
        re.search(r"(చెత్త|చెత్తకుప్పలు|కుప్పలు|పేరుకుపోయింది|దుర్వాసన|వాసన|దోమలు|చచ్చిన జంతువు|కళేబరం)", combined)
    )

    is_fire_term = bool(
        re.search(r"\b(fire|blaze|flames?|smoke|explosion|blast|gas leak|cylinder blast)\b", combined) or
        re.search(r"\b(mantalu|agni|cylinder blast|koolipoindi)\b", combined) or
        re.search(r"(మంటలు|అగ్ని|అగ్నిప్రమాదం|గ్యాస్ లీక్|సిలిండర్)", combined)
    )

    is_police_term = bool(
        re.search(r"\b(theft|burglary|robbery|assault|fight|violence|harass|stolen|weapon|knife|threat|rowdies)\b", combined) or
        re.search(r"\b(dongathanam|godava|daadi|bhayam|rowdielu|bedirimpu)\b", combined) or
        re.search(r"(దొంగతనం|గొడవ|దాడి|భయం|రౌడీలు|బెదిరింపు)", combined)
    )

    # A. FIRE & DISASTER
    if is_fire_term:
        defect = "Active fire outbreak and hazardous disaster emergency"
        dept_action = "Urgent Fire & Rescue Services deployment and emergency suppression required"

    # B. ELECTRICITY & STREETLIGHTING
    elif is_electric_term:
        if bool(re.search(r"\b(street lights?|streetlights?|bulb|lights?|lightlu)\b", combined)) and (
            bool(re.search(r"\b(velagadam ledu|velagatledu|not glowing|not working|off|dark|no lights|broken bulb)\b", combined)) or
            "వెలగడం లేదు" in combined or "వెలగట్లేదు" in combined or "చీకటి" in combined or "cheekati" in combined
        ):
            defect = "Non-functional municipal street lighting network causing dark, hazardous road corridor"
            dept_action = "Urgent municipal electrical maintenance and street light restoration required"
        elif bool(re.search(r"\b(transformer)\b", combined)) or "ట్రాన్స్‌ఫార్మర్" in combined:
            defect = "Municipal power grid transformer malfunction and electrical breakdown"
            dept_action = "Urgent Electricity Board technical intervention and transformer replacement required"
        elif bool(re.search(r"\b(wire|theega|cable|line|spark|sparks|live wire|snapped)\b", combined)) or "తీగ" in combined or "స్పార్క్స్" in combined:
            defect = "Exposed live high-voltage electrical power cable snapped and fallen on public roadway, posing lethal electrocution danger"
            dept_action = "Immediate Electricity Board emergency power shutdown and hazardous cable clearance required"
        else:
            defect = "Severe municipal electrical grid failure causing localized blackout and power outage"
            dept_action = "Urgent Electricity Board line restoration and power grid stabilization required"

    # C. ROADS & INFRASTRUCTURE
    elif is_pothole_term:
        if bool(re.search(r"\b(sinkhole|cave[- ]?in|structural collapse)\b", combined)) or "కూలిపోయింది" in combined:
            defect = "Severe roadway structural collapse with hazardous deep sinkhole crater"
            dept_action = "Urgent PWD emergency structural barricading, road rebuild, and asphalt paving required"
        else:
            defect = "Major roadway deterioration with dangerous deep potholes and craters"
            dept_action = "Urgent municipal road repair, safety barricading, and asphalt resurfacing required"

    # D. DRAINAGE & SEWERAGE
    elif is_drainage_term:
        if bool(re.search(r"\b(manhole|mootha ledu|open manhole|deep manhole|uncovered)\b", combined)) or "మ్యాన్‌హోల్" in combined or "మూత లేదు" in combined:
            defect = "Dangerous uncovered municipal sewer manhole on public thoroughfare posing fatal fall hazard"
            dept_action = "Immediate municipal manhole replacement, heavy-duty safety covering, and hazard perimeter cordoning required"
        else:
            defect = "Clogged municipal drainage network causing foul raw sewage overflow and hazardous standing wastewater"
            dept_action = "Urgent municipal drainage desilting, sewer clearance, and sanitization required"

    # E. WATER SUPPLY & DRINKING WATER
    elif is_water_term:
        if bool(re.search(r"\b(burst|pagilipoindi|rupture|broken pipe|pipe broke|pipe broken|leak|waste|vrudha|flooding|river|flowing)\b", combined)) or "పగిలిపోయింది" in combined or "వృధా" in combined:
            defect = "Pressurized municipal drinking water distribution pipeline rupture causing massive potable water wastage"
            dept_action = "Urgent Water Supply & Sewerage Board emergency pipeline repair and valve shutdown required"
        elif bool(re.search(r"\b(ravadam ledu|ravatledu|no water|water is not coming|supply cut|scarcity|shortage|dry|outage)\b", combined)) or "రావడం లేదు" in combined or "రావట్లేదు" in combined:
            defect = "Complete outage and severe disruption of municipal drinking water supply to the locality"
            dept_action = "Urgent Water Board municipal supply line restoration and emergency water tanker deployment required"
        elif bool(re.search(r"\b(dirty|muddy|contaminated|muriki|smell|foul|yellow|turbid)\b", combined)) or "మురికి" in combined or "కలుషిత" in combined:
            defect = "Severe municipal drinking water contamination with turbid and unsafe domestic water supply"
            dept_action = "Urgent Water Quality Board pipeline flushing, contamination isolation, and sample testing required"
        else:
            defect = "Municipal drinking water distribution infrastructure defect and continuous leakage"
            dept_action = "Urgent Water Supply & Sewerage Board inspection and maintenance required"

    # F. SANITATION & SOLID WASTE
    elif is_garbage_term:
        if bool(re.search(r"\b(animal|carcass|janthuvu|kukka|dog|dead)\b", combined)) or "చచ్చిన" in combined or "జంతువు" in combined or "కళేబరం" in combined:
            defect = "Decomposing animal carcass on public pathway posing acute biohazard and public health emergency"
            dept_action = "Immediate public health and veterinary sanitation dispatch for safe biohazard removal required"
        else:
            defect = "Heavy accumulation of uncollected municipal solid waste emitting severe foul stench and attracting stray animals"
            dept_action = "Urgent municipal solid waste clearance, sanitation compactor dispatch, and chemical disinfection required"

    # G. POLICE & PUBLIC SAFETY
    elif is_police_term:
        defect = "Active public safety disturbance and threat to community security"
        dept_action = "Immediate Police and Law Enforcement patrol dispatch required"

    else:
        # Fallback to general clean summary
        clean = text_primary.replace(r'[.\s]+$', '').strip()
        defect = clean[:1].upper() + clean[1:] if clean else "Municipal civic infrastructure disrepair"
        dept_action = "Urgent municipal inspection and corrective action required"

    # 2. OBSERVED IMPACTS & REAL-WORLD CONSEQUENCES
    impacts = []
    if bool(re.search(r"\b(accident|accidents|bikes?|vehicles?|motorcycle|scooter|fall|falling|fell|slip|slipped|crash|crashed|injured|injuries|damage|padipotunnaru|padipotunnayi|padipothunnaru)\b", combined)) or "పడిపోతున్నారు" in combined or "పడిపోతున్నాయి" in combined or "ప్రమాదం" in combined:
        impacts.append("causing active two-wheeler skids, commuter accidents, and severe injury risk")
    if bool(re.search(r"\b(spark|sparks|shock|electrocution|fire hazard|sparks coming)\b", combined)) or "స్పార్క్స్" in combined or "షాక్" in combined:
        impacts.append("emitting hazardous electrical sparks with imminent electrocution and fire hazard")
    if bool(re.search(r"\b(flood|flooding|water entered|homes|houses|dwelling|dwellings|shops|inside|illaloki|illoki)\b", combined)) or "ఇళ్లలోకి" in combined:
        impacts.append("inundating adjacent residential dwellings and disrupting local access")
    if bool(re.search(r"\b(stench|smell|foul|unbearable|mosquito|mosquitoes|dhomalu|dengue|malaria|hygiene|unhygienic|disease|kampukoduthondi|kampu)\b", combined)) or "దుర్వాసన" in combined or "దోమలు" in combined or "కంపు" in combined:
        impacts.append("generating unbearable foul stench, vector-borne disease breeding threats (dengue/malaria), and acute unhygienic conditions")
    if bool(re.search(r"\b(school|children|students|kids|pillalu)\b", combined)) or "పిల్లలు" in combined:
        impacts.append("situated in high-vulnerability school zone endangering students and pedestrians")
    if bool(re.search(r"\b(hospital|clinic|patient|patients|ambulance)\b", combined)) or "ఆసుపత్రి" in combined:
        impacts.append("obstructing critical emergency access route to healthcare facilities")
    if bool(re.search(r"\b(traffic|block|blocked|gridlock|jam|traffic jam|prayaanam kastam|travel is difficult)\b", combined)) or "జామ్" in combined or "కష్టంగా" in combined:
        impacts.append("creating severe traffic gridlock and transit obstruction across the primary thoroughfare")
    if bool(re.search(r"\b(dark|theft|unsafe|danger|women|night|night-time|cheekati|cheekatiga)\b", combined)) or "చీకటి" in combined or "భయంగా" in combined:
        impacts.append("severely compromising pedestrian and commuter safety during night hours")

    # 3. CONSTRUCT FORMAL MEANING STATEMENT
    statement = defect
    if impacts:
        statement += ", " + ", ".join(impacts)
    if dept_action:
        statement += f". {dept_action}."
    elif not statement.endswith("."):
        statement += "."

    return statement

def assess_detection(confidence: float) -> dict:
    """
    Rule-based severity and risk assessment.

    Confidence thresholds are based on the VisionInspect
    project specification.
    """
    if confidence >= 0.95:
        return {
            "severity": "CRITICAL",
            "risk": "HIGH",
            "recommendation": "Reject PCB",
        }

    if confidence >= 0.85:
        return {
            "severity": "HIGH",
            "risk": "HIGH",
            "recommendation": "Rework Required",
        }

    if confidence >= 0.70:
        return {
            "severity": "MEDIUM",
            "risk": "MEDIUM",
            "recommendation": "Manual Inspection",
        }

    return {
        "severity": "LOW",
        "risk": "LOW",
        "recommendation": "Accept / Review",
    }


def assess_inspection(detections: list[dict]) -> dict:
    """
    Aggregate detection-level assessments into an inspection decision.
    """

    if not detections:
        return {
            "severity": "NONE",
            "risk": "LOW",
            "decision": "PASS",
            "recommendation": "No defects detected",
        }

    assessments = [
        assess_detection(detection["confidence"])
        for detection in detections
    ]

    severity_priority = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    highest = max(
        assessments,
        key=lambda item: severity_priority[item["severity"]],
    )

    if highest["severity"] == "CRITICAL":
        decision = "REJECT"
    elif highest["severity"] == "HIGH":
        decision = "REWORK_REQUIRED"
    elif highest["severity"] == "MEDIUM":
        decision = "MANUAL_INSPECTION"
    else:
        decision = "REVIEW"

    return {
        "severity": highest["severity"],
        "risk": highest["risk"],
        "decision": decision,
        "recommendation": highest["recommendation"],
    }
SEVERITY_WEIGHTS={
    "low":5,
    "medium":15,
    "high":30,
    "critical":50
}

def calculate_risk(issues,ml_result):
    static_score=min(
        80,
        sum(
            SEVERITY_WEIGHTS.get(issue.get("severity"), 0) for issue in issues
        )
    )
    ml_score=20 if ml_result["prediction"]==1 else 0
    score=min(100,static_score+ml_score)

    if score>=80:
        priority="critical"
    elif score>=50:
        priority="high"
    elif score>=20:
        priority="medium"
    else:
        priority="low"

    return {
        "score":score,
        "priority":priority,
        "static_score":static_score,
        "ml_score":ml_score
    }
def generate_recommendation(parsed, ats_score):
    skills = parsed.get("skills", [])

    if ats_score >= 85:
        return "Highly Recommended"
    elif ats_score >= 70:
        return "Recommended"
    else:
        return "Needs Review"

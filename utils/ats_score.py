def calculate_ats_score(parsed, jd):
    skills = [s.lower() for s in parsed.get("skills", [])]

    if not jd:
        return 75

    jd_words = jd.lower().split()
    matched = sum(1 for skill in skills if skill in jd_words)

    score = min(100, 50 + matched * 10)
    return score

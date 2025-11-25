import re

def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()

def evaluate_teach_back(concept_summary, user_explanation):
    summary_tokens = set(tokenize(concept_summary))
    user_tokens = tokenize(user_explanation)
    overlap = summary_tokens.intersection(user_tokens)

    overlap_score = int(len(overlap) / max(1, len(summary_tokens)) * 70)
    length_bonus = min(30, max(0, len(user_tokens) - 5))

    score = min(100, overlap_score + length_bonus)

    if score >= 80:
        feedback = "Great explanation — clear and detailed!"
    elif score >= 50:
        feedback = "Decent attempt — add more technical points."
    else:
        feedback = "Needs more depth. Include more key ideas next time."

    return {"score": score, "feedback": feedback}

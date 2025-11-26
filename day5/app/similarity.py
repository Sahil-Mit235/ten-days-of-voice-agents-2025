import re

def tokenize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.split()

def similarity_score(a, b):
    a_tokens = set(tokenize(a))
    b_tokens = set(tokenize(b))
    if not a_tokens or not b_tokens:
        return 0.0
    common = a_tokens.intersection(b_tokens)
    # Jaccard-like simple score
    score = len(common) / float(len(a_tokens.union(b_tokens)))
    return score

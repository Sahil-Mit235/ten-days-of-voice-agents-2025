import random
from evaluate_teach_back import evaluate_teach_back

def pick_concept(concepts):
    print("Available concepts:")
    for i, c in enumerate(concepts, 1):
        print(f"{i}. {c['title']} (id: {c['id']})")
    idx = input("Pick concept number (or Enter for random): ").strip()
    try:
        if idx == "":
            return random.choice(concepts)
        idx = int(idx) - 1
        return concepts[idx]
    except Exception:
        print("Invalid choice, selecting random.")
        return random.choice(concepts)

def simulate_voice(voice_name, text):
    print(f"\n[{voice_name} voice] {text}\n")

def learn_mode(concepts):
    concept = pick_concept(concepts)
    simulate_voice("Matthew", f"Learn mode — {concept['title']}")
    simulate_voice("Matthew", concept["summary"])
    print("End of explanation.")

def quiz_mode(concepts):
    concept = pick_concept(concepts)
    simulate_voice("Alicia", f"Quiz mode — {concept['title']}")
    simulate_voice("Alicia", concept["sample_question"])
    answer = input("Your answer> ").strip()

    if len(answer.split()) < 3:
        simulate_voice("Alicia", "Short answer — add more detail next time.")
    else:
        simulate_voice("Alicia", "Nice! Try giving an example too.")

def teach_back_mode(concepts):
    concept = pick_concept(concepts)
    simulate_voice("Ken", f"Teach-back mode — {concept['title']}")
    simulate_voice("Ken", f"Explain this in your own words: {concept['sample_question']}")
    explanation = input("Your explanation> ").strip()

    result = evaluate_teach_back(concept["summary"], explanation)
    simulate_voice("Ken", f"Feedback: {result['feedback']} (score: {result['score']}/100)")

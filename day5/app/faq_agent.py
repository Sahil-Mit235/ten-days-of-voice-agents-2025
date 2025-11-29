import json
import os
from similarity import similarity_score

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'shared-data', 'day5_faq.json')
LEADS_PATH = os.path.join(os.path.dirname(__file__), '..', 'leads', 'leads.json')

def load_faq():
    with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def find_best_faq(user_question, faqs):
    best = None
    best_score = 0.0
    for f in faqs:
        s = similarity_score(user_question, f['question'] + " " + f.get('answer', ''))
        if s > best_score:
            best = f
            best_score = s
    return best, best_score

def save_lead(lead):
    os.makedirs(os.path.dirname(LEADS_PATH), exist_ok=True)
    leads = []
    if os.path.exists(LEADS_PATH):
        try:
            with open(LEADS_PATH, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        except:
            leads = []
    leads.append(lead)
    with open(LEADS_PATH, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2)

def simulate_voice(agent, text):
    print(f"[{agent.upper()} VOICE] {text}")

def faq_flow():
    faqs = load_faq()
    simulate_voice("Alicia", "Welcome to the Day 5 FAQ + Lead Capture demo.")
    print("Type a question, or 'lead' to capture contact, or 'exit' to quit.")

    while True:
        q = input("\nAsk (or 'lead' / 'exit')> ").strip()
        if not q:
            continue

        if q.lower() == "exit":
            simulate_voice("Ken", "Goodbye.")
            break

        if q.lower() == "lead":
            name = input("Name> ").strip()
            email = input("Email> ").strip()
            phone = input("Phone (optional)> ").strip()
            note = input("Note (optional)> ").strip()
            save_lead({"name": name, "email": email, "phone": phone, "note": note})
            print("Lead saved to day5/leads/leads.json")
            continue

        best, score = find_best_faq(q, faqs)
        if best and score > 0.12:
            print(f"\nBest match (score {score:.2f}):")
            print(f"Q: {best['question']}")
            print(f"A: {best['answer']}")
        else:
            simulate_voice("Alicia", "No good match found.")
            choice = input("Would you like to save your details? (yes/no)> ").strip().lower()
            if choice.startswith("y"):
                name = input("Name> ").strip()
                email = input("Email> ").strip()
                phone = input("Phone (optional)> ").strip()
                save_lead({"name": name, "email": email, "phone": phone, "note": f"from FAQ: {q}"})
                print("Lead saved.")
            else:
                print("Okay, try asking another question.")


import json, os
from similarity import similarity_score

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'shared-data', 'day5_faq.json')
LEADS_PATH = os.path.join(os.path.dirname(__file__), '..', 'leads', 'leads.json')

def load_faq():
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_best_faq(user_question, faqs):
    best = None
    best_score = 0.0
    for f in faqs:
        s = similarity_score(user_question, f['question'] + ' ' + f.get('answer',''))
        if s > best_score:
            best = f
            best_score = s
    return best, best_score

def save_lead(lead):
    os.makedirs(os.path.dirname(LEADS_PATH), exist_ok=True)
    leads = []
    if os.path.exists(LEADS_PATH):
        try:
            with open(LEADS_PATH,'r',encoding='utf-8') as f:
                leads = json.load(f)
        except Exception:
            leads = []
    leads.append(lead)
    with open(LEADS_PATH,'w',encoding='utf-8') as f:
        json.dump(leads, f, indent=2)
    return True

def simulate_voice(agent, text):
    # placeholder for Murf Falcon TTS + LiveKit handoff
    print(f\"[{agent.upper()} VOICE] {text}\")

def faq_flow():
    faqs = load_faq()
    simulate_voice('Alicia', 'Welcome to the Day 5 FAQ + Lead Capture demo (similarity-based).')
    print(\"Type a question, or 'lead' to capture contact, or 'exit' to quit.\")

    while True:
        q = input('\\nAsk (or \\\"lead\\\" / \\\"exit\\\")> ').strip()
        if not q:
            continue
        if q.lower() == 'exit':
            simulate_voice('Ken', 'Goodbye.')
            break
        if q.lower() == 'lead':
            name = input('Name> ').strip()
            email = input('Email> ').strip()
            phone = input('Phone (optional)> ').strip()
            note = input('Note (optional)> ').strip()
            lead = {'name': name, 'email': email, 'phone': phone, 'note': note}
            save_lead(lead)
            print('Lead saved locally to day5/leads/leads.json')
            continue

        best, score = find_best_faq(q, faqs)
        if best and score > 0.12:
            print(f\"Best match (score {score:.2f}):\\nQ: {best['question']}\\nA: {best['answer']}\")
        else:
            simulate_voice('Alicia', 'No good match found.')
            r = input('Would you like to save a lead so someone can contact you? (yes/no) > ').strip().lower()
            if r.startswith('y'):
                name = input('Name> ').strip()
                email = input('Email> ').strip()
                phone = input('Phone (optional)> ').strip()
                note = f\"From FAQ: {q}\"
                lead = {'name': name, 'email': email, 'phone': phone, 'note': note}
                save_lead(lead)
                print('Thanks — lead saved.')
            else:
                print('Okay — try rephrasing your question or ask another one.')

if __name__ == '__main__':
    faq_flow()

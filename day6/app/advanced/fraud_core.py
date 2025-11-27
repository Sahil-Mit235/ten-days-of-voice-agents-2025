import json
import os
import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'shared-data', 'fraud_cases.json')
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')

def load_cases():
    with open(DATA_PATH, 'r', encoding='utf-8-sig') as f:
        return json.load(f)

def save_cases(cases):
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2)
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f'fraud_log_{datetime.date.today().isoformat()}.log')
    with open(log_file, 'a', encoding='utf-8') as lf:
        lf.write(f\"[{datetime.datetime.now().isoformat()}] Cases saved\\n\")

def find_case_by_username(username, cases):
    for c in cases:
        if c.get('userName','').lower() == username.lower():
            return c
    return None

def update_case_status(case, result, note=''):
    if result == 'safe':
        case['status'] = 'confirmed_safe'
        case['outcomeNote'] = note or 'Customer confirmed transaction as legitimate.'
    elif result == 'fraud':
        case['status'] = 'confirmed_fraud'
        case['outcomeNote'] = note or 'Customer reported transaction as fraudulent. Action: card blocked, dispute raised (mock).'
    elif result == 'failed_verification':
        case['status'] = 'verification_failed'
        case['outcomeNote'] = note or 'Verification failed; could not proceed.'
    case['lastUpdated'] = datetime.datetime.now().isoformat()

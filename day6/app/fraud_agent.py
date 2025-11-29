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
        lf.write(f"[{datetime.datetime.now().isoformat()}] Cases saved\\n")

def simulate_voice(voice_name, text):
    # placeholder for Murf Falcon TTS + LiveKit
    print(f"[{voice_name} VOICE] {text}")

def find_case_by_username(username, cases):
    for c in cases:
        if c.get('userName','').lower() == username.lower():
            return c
    return None

def verify_user(case):
    simulate_voice('Ken', 'Before we proceed, please answer a simple security question.')
    simulate_voice('Ken', case.get('securityQuestion','(no question provided)'))
    answer = input('Your answer> ').strip().lower()
    if answer == case.get('securityAnswer','').lower():
        simulate_voice('Ken', 'Verification passed.')
        return True
    else:
        simulate_voice('Ken', 'Verification failed. For your protection we cannot proceed.')
        return False

def present_transaction(case):
    simulate_voice('Alicia', f"We detected a suspicious transaction on card ending {case.get('cardEnding')}.")
    simulate_voice('Alicia', f"Merchant: {case.get('transactionName')} | Amount: {case.get('transactionAmount')} | Source: {case.get('transactionSource')} | Time: {case.get('transactionTime')}")
    print('\\nDo you recognize and confirm this transaction? (yes/no)')

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

def fraud_call_flow():
    cases = load_cases()
    simulate_voice('Ken', 'Hello, this is the Fraud Department calling on behalf of YourBank (demo).')
    username = input('Please enter your full name to locate your case> ').strip()
    case = find_case_by_username(username, cases)
    if not case:
        simulate_voice('Ken', 'We could not find a case for that name. Please contact support via the app.')
        return

    verified = verify_user(case)
    if not verified:
        update_case_status(case, 'failed_verification')
        save_cases(cases)
        simulate_voice('Ken', 'The call will end now. Please contact our support to verify your identity.')
        return

    present_transaction(case)
    ans = input('Answer (yes/no)> ').strip().lower()
    if ans in ('yes','y'):
        update_case_status(case, 'safe', note='Customer confirmed transaction as legitimate.')
        simulate_voice('Ken', 'Thank you. We have marked the transaction as safe. No further action required.')
    elif ans in ('no','n'):
        update_case_status(case, 'fraud', note='Customer denied the transaction. Mock actions: card blocked and dispute raised.')
        simulate_voice('Ken', 'We have flagged the transaction as fraudulent. We will block the card and raise a dispute (mock).')
    else:
        simulate_voice('Ken', 'Response not understood. Ending call for security.')
        update_case_status(case, 'verification_failed', note='Unclear response from customer.')

    save_cases(cases)
    simulate_voice('Ken', f"Case {case.get('caseId')} updated. Current status: {case.get('status')}")
    print('\\nFinal case record:')
    print(json.dumps(case, indent=2))

if __name__ == '__main__':
    fraud_call_flow()

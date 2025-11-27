import os
from advanced.fraud_core import load_cases, save_cases, find_case_by_username, update_case_status
from advanced.murf_tts import synthesize_to_file

def simulate_call_flow(username):
    # Emulator: runs the same conversation but prints what would be played/sent as audio.
    cases = load_cases()
    case = find_case_by_username(username, cases)
    if not case:
        print('No case found for', username)
        return

    # 1: Intro
    intro_text = f\"Hello {case['userName']}, this is the Fraud Department of DemoBank calling about a suspicious transaction.\"
    audio = synthesize_to_file(intro_text, voice='Ken')
    print('[EMULATOR PLAY]', audio, '->', intro_text)

    # 2: Verification
    q = case.get('securityQuestion','Please verify.')
    audio = synthesize_to_file('Please answer: ' + q, voice='Ken')
    print('[EMULATOR PLAY]', audio, '->', q)
    ans = input('Emulator - type the user answer: ').strip().lower()
    if ans != case.get('securityAnswer','').lower():
        update_case_status(case, 'failed_verification')
        save_cases(cases)
        print('Verification failed. Case updated.')
        return

    # 3: Present transaction
    tx = f\"Merchant: {case.get('transactionName')} | Amount: {case.get('transactionAmount')} | Card: ending {case.get('cardEnding')}\"
    audio = synthesize_to_file(tx, voice='Alicia')
    print('[EMULATOR PLAY]', audio, '->', tx)

    # 4: Ask yes/no
    audio = synthesize_to_file('Did you make this transaction? Answer yes or no.', voice='Alicia')
    print('[EMULATOR PLAY]', audio, '-> Did you make this transaction?')
    ans2 = input('Emulator - did you make it? (yes/no) ').strip().lower()
    if ans2.startswith('y'):
        update_case_status(case, 'safe', note='Customer confirmed transaction as legitimate (via emulator).')
        print('Marked as safe.')
    else:
        update_case_status(case, 'fraud', note='Customer denied transaction (via emulator). Mock actions executed.')
        print('Marked as fraud.')

    save_cases(cases)
    print('Final case:')
    print(case)

# LIVEKIT TELEPHONY STUB - where to integrate for real calls
def livekit_telephony_handler(livekit_call_object):
    \"\"\"PSEUDO-CODE / STUB:
    - livekit_call_object: object representing an incoming call/session
    Steps:
      1) Use Murf Falcon to synthesize the intro/verification/transaction text -> get audio bytes
      2) Stream audio into the LiveKit participant (play)
      3) Capture audio from caller -> transcribe (use speech-to-text) OR use LiveKit VAD/turns
      4) Map transcribed text to verification answers / yes/no
      5) Update case via fraud_core and persist
    Implementation is specific to your LiveKit server/client SDK and telephony gateway (Twilio/Plivo/SIP).
    \"\"\"
    raise NotImplementedError('Replace with LiveKit Telephony integration here.')

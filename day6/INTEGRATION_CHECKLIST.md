LiveKit + Murf Integration Checklist:

1) Get LiveKit Telephony credentials and SIP/phone configuration.
2) Get Murf Falcon API key / SDK access.
3) Replace synthesize_to_file in murrf_tts.py with real Murf TTS (return audio bytes or a path).
4) Implement livekit_telephony_handler in telephony_adapter.py:
   - On incoming call, run fraud flow, synthesize audio pieces, stream to caller, capture response, transcribe.
5) Use secure logging and never request real card/PIN.

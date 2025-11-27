import sys
from advanced.telephony_adapter import simulate_call_flow

def main():
    if len(sys.argv) < 2:
        print('Usage: python telephony_runner.py <username>')
        print('Example: python telephony_runner.py \"John Doe\"')
        sys.exit(1)
    username = sys.argv[1]
    simulate_call_flow(username)

if __name__ == '__main__':
    main()

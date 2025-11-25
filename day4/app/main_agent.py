import json
import os
from tutor_agent import learn_mode, quiz_mode, teach_back_mode

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "shared-data", "day4_tutor_content.json")

def load_concepts():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def choose_mode_loop(concepts):
    print("Hi! I'm your Active Recall Coach. Which mode would you like? (learn / quiz / teach_back / exit)")
    mode = input("mode> ").strip().lower()
    while mode != "exit":
        if mode == "learn":
            learn_mode(concepts)
        elif mode == "quiz":
            quiz_mode(concepts)
        elif mode == "teach_back":
            teach_back_mode(concepts)
        else:
            print("Unknown mode. Choose learn / quiz / teach_back / exit.")
        print("\nSwitch mode? (learn / quiz / teach_back / exit)")
        mode = input("mode> ").strip().lower()
    print("Goodbye — session ended.")

if __name__ == "__main__":
    concepts = load_concepts()
    choose_mode_loop(concepts)

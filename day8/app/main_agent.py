"""
main_agent.py
Day 8 - Voice Game Master (Primary + Advanced)
Run: python main_agent.py
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENT_YAML = ROOT / "agent.yaml"
SAVE_FILE = ROOT / "save_game.json"

# ---------- Utilities ----------
def load_universe_presets():
    # simple YAML parse without external libs (works for our small file)
    import yaml  # If yaml not available, fallback to manual parse below.
    try:
        with open(AGENT_YAML, "r", encoding="utf8") as f:
            data = yaml.safe_load(f)
            return data
    except Exception:
        # fallback minimal parser (only for this file structure)
        return {}

def now_str():
    return datetime.utcnow().isoformat() + "Z"

# ---------- Game State (JSON world) ----------
DEFAULT_STATE = {
    "meta": {"started_at": None, "universe": "fantasy"},
    "player": {"name": None, "hp": 10, "max_hp": 10, "attributes": {"strength": 1, "intelligence": 1, "luck": 1}, "inventory": []},
    "location": {"name": "Edge of Emberfall", "desc": "A whispering forest where runes glow faintly."},
    "npcs": {},
    "events": [],
    "quests": {"active": [], "completed": []},
    "history": []  # stores short transcript of turns
}

# ---------- Game Master ----------
class GameMaster:
    def __init__(self, universe="fantasy"):
        self.presets = load_universe_presets()
        self.state = json.loads(json.dumps(DEFAULT_STATE))  # deep copy
        self.set_universe(universe)
        self.state['meta']['started_at'] = now_str()

    def set_universe(self, universe):
        self.universe = universe
        self.system_prompt = self._get_system_prompt_for(universe)
        self.state['meta']['universe'] = universe

    def _get_system_prompt_for(self, universe):
        # load from YAML if possible
        try:
            import yaml
            with open(AGENT_YAML, "r", encoding="utf8") as f:
                data = yaml.safe_load(f)
            return data['universes'][universe]['system_prompt']
        except Exception:
            # fallback: a concise generic prompt
            return "You are the Game Master. Tone: Dramatic but friendly. Ask the player what they do next."

    # ---------- State helpers ----------
    def save(self, path=SAVE_FILE):
        with open(path, "w", encoding="utf8") as f:
            json.dump(self.state, f, indent=2)
        print(f"[saved] -> {path}")

    def load(self, path=SAVE_FILE):
        if not path.exists():
            print("[load] save file not found.")
            return False
        self.state = json.loads(path.read_text(encoding="utf8"))
        print(f"[loaded] <- {path}")
        return True

    # ---------- World interactions ----------
    def add_history(self, speaker, text):
        entry = {"time": now_str(), "speaker": speaker, "text": text}
        self.state['history'].append(entry)
        # keep last 100 entries
        self.state['history'] = self.state['history'][-100:]

    def roll_d20(self, modifier=0):
        r = random.randint(1, 20)
        total = r + modifier
        return {"roll": r, "modifier": modifier, "total": total, "success": total >= 10, "crit": r == 20, "fumble": r == 1}

    # ---------- Simple text-generation stub ----------
    def gm_speak(self, text, tts=True):
        """
        Core: GM describes scene and asks a question.
        We print text and optionally call TTS hook.
        """
        print("\n--- GM ---")
        print(text)
        if tts:
            self.tts_speak(text)
        self.add_history("GM", text)

    def tts_speak(self, text):
        """
        TTS hook: by default uses system TTS (where available) or prints a note.
        Replace this function to call Murf Falcon TTS API or other TTS service.
        """
        # simple Windows TTS using PowerShell 'Add-Type' approach
        if sys.platform.startswith("win"):
            try:
                import subprocess, shlex
                ps = f'Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak("{text.replace(\'"\', \'\\\\"\')}");'
                subprocess.call(["powershell", "-Command", ps])
                return
            except Exception:
                pass
        # fallback: print a divider telling user to speak or use their TTS
        print("[TTS placeholder] (replace with Murf Falcon TTS integration)")

    # ---------- Gameplay logic ----------
    def start_session(self):
        # Starting GM message: uses system prompt style + asks for name
        intro = self.system_prompt.strip().splitlines()[0]
        opening = "Welcome to the adventure. " + intro
        opening += " What is your character's name?"
        self.gm_speak(opening)

    def handle_player(self, player_text):
        """
        Process player's input, update state, and produce next GM output.
        This is a simple but extendable story engine.
        """
        self.add_history("Player", player_text)

        # if player hasn't set name yet, use first response as name
        if not self.state['player']['name']:
            name = player_text.strip().splitlines()[0].strip().split()[0]
            self.state['player']['name'] = name
            self.state['npcs']['elder'] = {"name": "Elder Mira", "status": "friendly"}
            self.state['quests']['active'].append({"id": "crystal", "desc": "Find the Crystal of Emberfall", "started_at": now_str()})
            s = f"Well met, {name}. The village elder, Elder Mira, says shadow creatures stole the Crystal of Emberfall. The elder gives you a small silver dagger. What do you do next?"
            # give dagger
            self.state['player']['inventory'].append("small silver dagger")
            self.gm_speak(s)
            return

        # small parser for dice-checked actions
        low = player_text.lower()
        if any(p in low for p in ["attack", "hit", "strike", "fight"]):
            mod = self.state['player']['attributes'].get("strength", 1)
            result = self.roll_d20(modifier=mod)
            desc = f"You attempt to attack. Roll: {result['roll']} + {mod} = {result['total']}."
            if result['crit']:
                desc += " Critical hit! You slay the foe instantly."
                self.state['events'].append({"event": "critical_hit", "time": now_str()})
            elif result['success']:
                desc += " You hit the enemy and wound it."
            else:
                desc += " You miss and the enemy counters."
                # reduce some HP
                self.state['player']['hp'] -= 1
            desc += " What do you do now?"
            self.gm_speak(desc)
            return

        if "inventory" in low or "what do i have" in low or "what's in my bag" in low:
            inv = self.state['player']['inventory'] or ["(empty)"]
            s = f"You check your inventory: {', '.join(inv)}. What do you do next?"
            self.gm_speak(s)
            return

        if any(x in low for x in ["save game", "save", "save my progress"]):
            self.save()
            self.gm_speak("Game saved. What do you do next?")
            return

        if any(x in low for x in ["load game", "load"]):
            ok = self.load()
            if ok:
                self.gm_speak("Save loaded. Where were we? What do you do next?")
            else:
                self.gm_speak("No saved game found. What do you do next?")
            return

        if any(x in low for x in ["look", "examine", "inspect"]):
            s = f"You look around: {self.state['location']['desc']}. You see an old altar and a path deeper into the woods. What do you do?"
            self.gm_speak(s)
            return

        # fallback: creative action accepted — influence story
        # add a small branching effect
        if "befriend" in low or "calm" in low or "talk" in low:
            # chance of success using luck
            luck = self.state['player']['attributes'].get("luck", 1)
            r = random.randint(1, 6) + luck
            if r >= 5:
                s = "Your gentle action succeeds. The creature becomes an ally and guides you to a hidden path. What do you do next?"
                # add a small item or event
                self.state['player']['inventory'].append("guiding feather")
                self.state['events'].append({"event": "befriended_creature", "time": now_str()})
            else:
                s = "Your attempt to befriend fails and the creature growls. What do you do now?"
            self.gm_speak(s)
            return

        # default continuation — small advancement of the mini-arc
        # if the quest is active and not completed, nudge story toward finding an item
        if any(q['id']=="crystal" for q in self.state['quests']['active']):
            s = "A faint glow appears beneath a pile of leaves. You sense the Crystal of Emberfall nearby. Do you dig, call for help, or leave it?"
            self.gm_speak(s)
            return

        # ultimate fallback
        self.gm_speak("I don't understand that exactly, but it creates a new twist: the ground trembles. What do you do next?")

# ---------- CLI Demo ----------
def cli_loop():
    gm = GameMaster(universe=os.environ.get("DAY8_UNIVERSE", "fantasy"))
    print(f"[Universe] {gm.universe}")
    gm.start_session()
    turns = 0
    # ensure at least 8-15 turns for a full demo, but user can quit earlier
    while True:
        user = input("\nYou: ").strip()
        if not user:
            continue
        if user.lower() in ("quit", "exit"):
            print("Session ended. You can save the game with 'save game' before quitting.")
            break
        if user.lower() in ("switch universe:fantasy", "switch:fantasy"):
            gm.set_universe("fantasy")
            print("[changed universe -> fantasy]")
            continue
        if user.lower() in ("switch universe:cyberpunk", "switch:cyberpunk"):
            gm.set_universe("cyberpunk")
            print("[changed universe -> cyberpunk]")
            continue
        if user.lower() in ("switch universe:space", "switch:space"):
            gm.set_universe("space")
            print("[changed universe -> space]")
            continue

        gm.handle_player(user)
        turns += 1

        if turns >= 15:
            # wrap up a mini-arc
            gm.gm_speak("The mini-arc concludes: you found a clue that points to a larger adventure. Save or continue? What do you do next?")
            # stop after the user responds with 'save' or 'quit' in the next loop
        # continue until user quits

if __name__ == "__main__":
    cli_loop()

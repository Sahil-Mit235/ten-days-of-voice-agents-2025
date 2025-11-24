import os, json, uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

APP_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(APP_DIR, "static")
AUDIO_DIR = os.path.join(STATIC_DIR, "audio")
LOG_PATH = os.path.join(APP_DIR, "wellness_log.json")
os.makedirs(AUDIO_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static", static_url_path="/static")

def load_log():
    if not os.path.exists(LOG_PATH):
        return []
    try:
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_log(entries):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/history', methods=['GET'])
def history():
    return jsonify(load_log())

@app.route('/api/checkin', methods=['POST'])
def checkin():
    data = request.json or {}
    entries = load_log()
    now = datetime.now().isoformat()
    entry = {
        'id': str(uuid.uuid4()),
        'datetime': now,
        'mood_text': data.get('mood_text',''),
        'mood_score': data.get('mood_score'),
        'energy': data.get('energy',''),
        'objectives': data.get('objectives',[]),
        'agent_summary': data.get('agent_summary','')
    }
    entries.append(entry)
    save_log(entries)
    return jsonify({'status':'ok','entry':entry})

@app.route('/api/respond', methods=['POST'])
def respond():
    data = request.json or {}
    user_text = (data.get('text') or '').strip()
    if not user_text:
        return jsonify({'reply_text':'I did not hear anything.','audio_url':None}), 400

    # Simple deterministic reply (keeps it local & reliable)
    reply_text = f"Thanks — I heard: {user_text}. Small suggestion: try a 5-minute break."

    # create audio via gTTS (fallback, no external Murf required)
    uid = str(uuid.uuid4())
    out_path = os.path.join(AUDIO_DIR, f"{uid}.mp3")
    try:
        tts = gTTS(reply_text[:4000], lang='en', slow=False)
        tts.save(out_path)
    except Exception as e:
        return jsonify({'error':'tts_failed','detail':str(e)}), 500

    # also lightly persist the utterance to history for continuity
    entries = load_log()
    entries.append({'id':str(uuid.uuid4()), 'datetime': datetime.now().isoformat(), 'mood_text': user_text, 'mood_score': None, 'energy':'','objectives':[]})
    if len(entries) > 500: entries = entries[-500:]
    save_log(entries)

    audio_url = f"/static/audio/{uid}.mp3"
    return jsonify({'reply_text': reply_text, 'audio_url': audio_url})

# serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

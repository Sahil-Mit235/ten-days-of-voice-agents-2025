require("dotenv").config();
const express = require("express");
const cors = require("cors");
const { AccessToken } = require("livekit-server-sdk");
const axios = require("axios");
const fs = require("fs").promises;
const path = require("path");

const app = express();
app.use(express.json());
app.use(cors());

const {
  LIVEKIT_API_KEY,
  LIVEKIT_API_SECRET,
  LIVEKIT_URL,
  MURF_API_KEY,
  PORT = 4000
} = process.env;

let scenarios = [];
async function loadScenarios() {
  try {
    const p = path.join(__dirname, "scenarios.json");
    const raw = await fs.readFile(p, "utf8");
    scenarios = JSON.parse(raw);
  } catch (e) {
    console.error("Failed to load scenarios.json", e);
  }
}
loadScenarios();

const sessions = {};

// token endpoint for browser
app.get("/api/token", (req, res) => {
  const identity = req.query.identity || `player_${Date.now()}`;
  const at = new AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, { identity });
  at.addGrant({ room: "*" });
  at.ttl = 60 * 60;
  const token = at.toJwt();
  res.json({ url: LIVEKIT_URL, token });
});

// create or load session
app.post("/api/session", (req, res) => {
  const { sessionId, name, maxRounds = 3 } = req.body || {};
  const id = sessionId || `sess_${Date.now()}`;
  sessions[id] = sessions[id] || {
    player_name: name || null,
    current_round: 0,
    max_rounds,
    rounds: [],
    phase: "intro",
    current_scenario: null
  };
  res.json({ sessionId: id, state: sessions[id] });
});

// start new round
app.post("/api/start-round", (req, res) => {
  const { sessionId } = req.body;
  const s = sessions[sessionId];
  if (!s) return res.status(400).json({ error: "invalid sessionId" });
  s.current_round += 1;
  s.phase = "awaiting_improv";
  s.current_scenario = scenarios[Math.floor(Math.random() * scenarios.length)].scenario;
  res.json({ scenario: s.current_scenario, current_round: s.current_round });
});

// submit transcript
app.post("/api/submit-turn", async (req, res) => {
  try {
    const { sessionId, transcript } = req.body;
    const s = sessions[sessionId];
    if (!s) return res.status(400).json({ error: "invalid sessionId" });

    const text = (transcript || "").trim();
    const reaction = generateReaction(
      s.player_name || "Player",
      s.current_scenario,
      text,
      s.current_round
    );

    s.rounds.push({
      scenario: s.current_scenario,
      player_text: text,
      host_reaction: reaction
    });
    s.phase = "reacting";

    const tts = await synthesizeMurf(reaction);

    let done = false;
    if (s.current_round >= s.max_rounds) {
      s.phase = "done";
      done = true;
    } else {
      s.phase = "waiting_next";
    }

    res.json({ reaction, tts, done });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "server error" });
  }
});

// reaction generator (simple)
function generateReaction(playerName, scenario, playerText, roundNumber) {
  const rand = Math.random();
  let tone = "supportive";
  if (rand > 0.7) tone = "mildly critical";
  else if (rand > 0.4) tone = "neutral";

  const snippet = playerText
    ? '"' + playerText.split(".").slice(0, 1).join(".") + '"'
    : "that choice";

  if (tone === "supportive") {
    return `Loved the energy, ${playerName} — especially the line ${snippet}. Bold choice.`;
  } else if (tone === "neutral") {
    return "Solid idea; you established the premise quickly. Try to linger on one detail more. Good setup.";
  } else {
    return "Clever, but the pace felt rushed — you could have milked that reaction longer. Pace up.";
  }
}

// Murf TTS
async function synthesizeMurf(text) {
  if (!MURF_API_KEY) {
    return { error: "MURF_API_KEY not configured" };
  }
  try {
    const resp = await axios.post(
      "https://api.murf.ai/v1/tts/falcon",
      {
        text,
        voice: "alloy"
      },
      {
        headers: { Authorization: `Bearer ${MURF_API_KEY}` },
        responseType: "arraybuffer"
      }
    );

    const base64 = Buffer.from(resp.data, "binary").toString("base64");
    return {
      audio_base64: base64,
      mime: resp.headers["content-type"] || "audio/mpeg"
    };
  } catch (err) {
    console.error("Murf TTS failed", err.message || err);
    return { error: "tts_failed" };
  }
}

app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
});

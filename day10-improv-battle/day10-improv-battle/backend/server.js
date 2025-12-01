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

let scenarios = [];
async function loadScenarios() {
  const p = path.join(__dirname, "scenarios.json");
  const raw = await fs.readFile(p, "utf8");
  scenarios = JSON.parse(raw);
}
loadScenarios();

const sessions = {};

app.post("/api/session", (req, res) => {
  const { name } = req.body;
  const id = "sess_" + Date.now();
  sessions[id] = {
    player_name: name,
    current_round: 0,
    max_rounds: 3,
    rounds: [],
    phase: "intro",
    current_scenario: null
  };
  res.json({ sessionId: id, state: sessions[id] });
});

app.post("/api/start-round", (req, res) => {
  const { sessionId } = req.body;
  const s = sessions[sessionId];
  s.current_round += 1;
  s.current_scenario =
    scenarios[Math.floor(Math.random() * scenarios.length)].scenario;
  s.phase = "awaiting_improv";
  res.json({ scenario: s.current_scenario });
});

app.post("/api/submit-turn", async (req, res) => {
  const { sessionId, transcript } = req.body;
  const s = sessions[sessionId];

  const reaction = "Nice improv! You said: " + transcript;
  s.rounds.push({ scenario: s.current_scenario, reaction });

  res.json({ reaction, done: s.current_round >= s.max_rounds });
});

module.exports = app;

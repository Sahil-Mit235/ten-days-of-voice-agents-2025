# Day 7 — Food & Grocery Ordering Voice Agent (Primary + Advanced)

Run locally:
1) python day7\\app\\main_agent.py
2) Commands: catalog | add <id_or_name> [qty] | recipe <key> [servings] | cart | remove <id> | update <id> <qty> | place | orders | track <orderId> | reorder <orderId> | advance <orderId> | quit

Advanced:
- Use python day7\\app\\advance_status.py to advance all pending orders (simulate time-based changes).
- Orders are persisted in day7/orders/orders.json.

Integration:
- Replace simulate_voice(...) with Murf Falcon TTS calls and integrate with LiveKit for voice handoff if desired.


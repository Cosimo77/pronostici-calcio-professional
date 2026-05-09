#!/usr/bin/env python3
"""Check if batch updated CSV"""
import datetime
import json

with open("/tmp/tracking_now.json") as f:
    data = json.load(f)

csv_content = data.get("csv_content", "")
lines = [l for l in csv_content.split("\n") if l.strip() and not l.startswith("Data,")]

print(f"📊 CSV lines DOPO batch: {len(lines)}")

today = datetime.datetime.now().strftime("%Y-%m-%d")
today_preds = [l for l in lines if l.startswith(today)]

print(f"📅 Predizioni oggi ({today}): {len(today_preds)}")

if today_preds:
    print("\n✅ Prime 5 predizioni di oggi:")
    for l in today_preds[:5]:
        parts = l.split(",")
        if len(parts) >= 5:
            print(f"  {parts[2]} vs {parts[3]} ({parts[4]})")
else:
    print("\n❌ NESSUNA predizione salvata per oggi!")
    print("\n   Questo significa che auto-tracking NON sta salvando su disco.")
    print("   Possibili cause:")
    print("   1. File tracking_predictions_live.csv non writable su Render")
    print("   2. Filesystem effimero su Render (non persistente)")
    print("   3. Errore in track_prediction() che viene ignorato")

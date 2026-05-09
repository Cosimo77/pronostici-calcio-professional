#!/usr/bin/env python3
"""Check if tracking CSV on Render was updated with today's predictions"""
import json
import sys

with open("/tmp/render_tracking.json") as f:
    data = json.load(f)

total = data.get("total_predictions", 0)
csv_content = data.get("csv_content", "")
lines = [l for l in csv_content.split("\n") if l.strip()]

print(f"📊 Total predictions: {total}")
print(f"📄 CSV lines: {len(lines)}")

# Cerca predizioni del 18 aprile
pred_18 = [l for l in lines if "2026-04-18" in l]
print(f"\n🔍 Predizioni 18/04/2026: {len(pred_18)}")

if pred_18:
    print("\n✅ Ultime 3 pred del 18/04:")
    for p in pred_18[-3:]:
        parts = p.split(",")
        if len(parts) >= 9:
            print(f"  {parts[2]} vs {parts[3]}: {parts[5]} (EV {parts[8]}%)")
else:
    print("\n❌ NESSUNA predizione del 18/04 trovata!")

print(f"\n📅 Ultima predizione nel CSV:")
if lines:
    last = lines[-1].split(",")
    if len(last) > 3:
        print(f"  Data: {last[0]}")
        print(f"  Match: {last[2]} vs {last[3]}")
        if len(last) > 12:
            print(f"  Note: {last[-1][:80]}")

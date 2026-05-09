#!/usr/bin/env python3
"""Debug tracking count mismatch"""
import json
from collections import Counter
from datetime import datetime, timedelta

with open("/tmp/tracking_now.json") as f:
    data = json.load(f)

csv_content = data.get("csv_content", "")
lines = [l for l in csv_content.split("\n") if l.strip() and not l.startswith("Data,")]

print(f"📊 TRACKING CSV SU RENDER (ORA):")
print(f"  Total lines: {len(lines)}")

# Conta per data
dates = [l.split(",")[0] for l in lines if len(l.split(",")) > 0]
date_counts = Counter(dates)

print(f"\n📅 Predizioni per data (ultime 10):")
for date, count in sorted(date_counts.items())[-10:]:
    print(f"  {date}: {count} predizioni")

# Check pending
pending = [l for l in lines if len(l.split(",")) >= 10 and not l.split(",")[9].strip()]
print(f"\n⏳ Predizioni PENDING: {len(pending)}")

# Pending ultimi 30 giorni
cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
pending_30d = [l for l in pending if l.split(",")[0] >= cutoff]
print(f"⏳ Pending ultimi 30 giorni: {len(pending_30d)}")

if len(pending_30d) > 0:
    print("\n  Prime 5 pending recenti:")
    for l in pending_30d[:5]:
        parts = l.split(",")
        if len(parts) >= 5:
            print(f"  {parts[0]}: {parts[2]} vs {parts[3]} ({parts[4]})")

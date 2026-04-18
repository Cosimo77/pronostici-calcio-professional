import json
import re
from datetime import datetime, timedelta
from io import StringIO

import pandas as pd

# Scarica CSV
with open("/tmp/raw_response.txt") as f:
    data = json.load(f)

csv_content = data["csv_content"]

print(f"📊 CSV originale: {csv_content.count(chr(10))} righe (newlines)")

# Pulisci Note field: rimuovi serializzazione pandas
# Pattern: "Strategia: 0        FASE2_OVER_UNDER\n1        FASE2_OVER_UNDER\n..."
cleaned_csv = re.sub(r" \| Strategia: [\s\S]*?Name: Strategia, dtype: object", "", csv_content)

print(f"✅ CSV pulito: {cleaned_csv.count(chr(10))} righe")

# Salva
with open("/tmp/tracking_cleaned.csv", "w") as f:
    f.write(cleaned_csv)

# Verifica parsing
df = pd.read_csv(StringIO(cleaned_csv))
df["Data"] = pd.to_datetime(df["Data"], errors="coerce")

print(f"\n📈 DataFrame parsed: {len(df)} righe")
print(f"❌ Righe con Data=NaT: {df['Data'].isna().sum()}")
print(f"✅ Righe valide: {(~df['Data'].isna()).sum()}")

# Conta pending
thirty_days_ago = datetime.now() - timedelta(days=30)
df_pending = df[df["Risultato_Reale"].isna() | (df["Risultato_Reale"] == "")]
df_pending_30d = df_pending[df_pending["Data"] >= thirty_days_ago]

print(f"\n🔄 Pending totali: {len(df_pending)}")
print(f"🔄 Pending ultimi 30gg: {len(df_pending_30d)}")

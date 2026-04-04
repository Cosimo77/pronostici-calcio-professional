import pandas as pd

# Carica dataset originale
df = pd.read_csv("data/dataset_features.csv")

print("🔧 FEATURE ENGINEERING - EQUILIBRIO SQUADRE (Pre-Match)")
print("=" * 70)

# Conta features iniziali
initial_features = [c for c in df.columns if c not in ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
print(f"\nFeatures iniziali: {len(initial_features)}")

# 1. EQUILIBRIO PUNTI (squadre simili in classifica → più pareggi)
if "casa_forma_media_punti" in df.columns and "trasferta_forma_media_punti" in df.columns:
    df["punti_diff"] = abs(df["casa_forma_media_punti"] - df["trasferta_forma_media_punti"])
    df["squadre_equilibrate"] = (df["punti_diff"] < 0.5).astype(int)  # Diff < 0.5 ppp
    print("✅ Equilibrio punti creato")

# 2. EQUILIBRIO GOL FATTI (attacchi simili → imprevedibile → pareggio)
if "casa_forma_media_gol_fatti" in df.columns and "trasferta_forma_media_gol_fatti" in df.columns:
    df["gol_fatti_diff"] = abs(df["casa_forma_media_gol_fatti"] - df["trasferta_forma_media_gol_fatti"])
    df["attacco_equilibrato"] = (df["gol_fatti_diff"] < 0.3).astype(int)
    print("✅ Equilibrio gol fatti creato")

# 3. DIFESE SOLIDE ENTRAMBE (pochi gol → pareggio)
if "casa_forma_media_gol_subiti" in df.columns and "trasferta_forma_media_gol_subiti" in df.columns:
    df["difese_solide"] = (
        (df["casa_forma_media_gol_subiti"] < 1.0) & (df["trasferta_forma_media_gol_subiti"] < 1.0)
    ).astype(int)
    print("✅ Difese solide creato")

# 4. ATTACCHI DEBOLI ENTRAMBI (pochi gol segnati → pareggio 0-0)
if "casa_forma_media_gol_fatti" in df.columns and "trasferta_forma_media_gol_fatti" in df.columns:
    df["attacchi_deboli"] = (
        (df["casa_forma_media_gol_fatti"] < 1.0) & (df["trasferta_forma_media_gol_fatti"] < 1.0)
    ).astype(int)
    print("✅ Attacchi deboli creato")

# 5. MATCH LOW-SCORING EXPECTED (somma gol attesi bassa → pareggio)
if "casa_forma_media_gol_fatti" in df.columns and "trasferta_forma_media_gol_fatti" in df.columns:
    df["gol_attesi_totali"] = df["casa_forma_media_gol_fatti"] + df["trasferta_forma_media_gol_fatti"]
    df["match_low_scoring"] = (df["gol_attesi_totali"] < 2.0).astype(int)
    print("✅ Match low-scoring creato")

# 6. EQUILIBRIO CASA vs TRASFERTA (casa non dominante)
if "casa_home_media_punti" in df.columns and "trasferta_away_media_punti" in df.columns:
    df["vantaggio_casa"] = df["casa_home_media_punti"] - df["trasferta_away_media_punti"]
    df["no_home_advantage"] = (abs(df["vantaggio_casa"]) < 0.3).astype(int)
    print("✅ No home advantage creato")

# Salva
final_features = [c for c in df.columns if c not in ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]]
print(f"\nFeatures finali: {len(final_features)} (+{len(final_features) - len(initial_features)} nuove)")

# Correlazioni con pareggi
df_temp = df.copy()
df_temp["IS_DRAW"] = (df["FTR"] == "D").astype(int)

new_features = [
    "squadre_equilibrate",
    "attacco_equilibrato",
    "difese_solide",
    "attacchi_deboli",
    "match_low_scoring",
    "no_home_advantage",
]

print("\n📊 Correlazione con Pareggi:")
for feat in new_features:
    if feat in df_temp.columns:
        corr = df_temp[[feat, "IS_DRAW"]].corr().iloc[0, 1]
        print(f"   {feat:<25} {corr:>6.3f}")

df.to_csv("data/dataset_features_enhanced.csv", index=False)
print("\n✅ Salvato: dataset_features_enhanced.csv")

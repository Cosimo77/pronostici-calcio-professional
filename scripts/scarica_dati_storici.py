import requests
import os
import pandas as pd

# Lista URL CSV da scaricare
links_da_scaricare = [
    'https://www.football-data.co.uk/mmz4281/2526/I1.csv',
    'https://www.football-data.co.uk/mmz4281/2425/I1.csv',
    'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
    'https://www.football-data.co.uk/mmz4281/2223/I1.csv',
    'https://www.football-data.co.uk/mmz4281/2122/I1.csv',
    'https://www.football-data.co.uk/mmz4281/2021/I1.csv'
]

os.makedirs("data", exist_ok=True)

# Scarica e salva file con nome univoco basato sull'anno
for url in links_da_scaricare:
    anno = url.split("/")[-2]
    filename = f"I1_{anno}.csv"
    filepath = os.path.join("data", filename)
    if not os.path.exists(filepath):
        print(f"Scaricando {filename} da {url} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(r.content)
        print(f"✅ {filename} scaricato con successo!")
    else:
        print(f"⏭️  {filename} già presente, salto download.")
        # Verifica se è la stagione corrente e mostra info
        if anno == "2526":
            try:
                df_check = pd.read_csv(filepath, parse_dates=["Date"], dayfirst=True, encoding="latin1")
                ultima_data = df_check['Date'].max()
                print(f"   📅 Ultima partita nel file esistente: {ultima_data.strftime('%d/%m/%Y')}")
                print(f"   📊 Totale partite: {len(df_check)}")
                print(f"   💡 Usa 'python3 scripts/aggiorna_stagione_corrente.py' per forzare l'aggiornamento")
            except Exception as e:
                print(f"   ⚠️  Errore nella lettura del file: {e}")

print("\n" + "="*60)

# Unisci tutti i CSV nel DataFrame unico
df_list = []
for file in os.listdir("data"):
    if file.endswith(".csv"):
        path = os.path.join("data", file)
        print(f"Caricando {file}...")
        df_parziale = pd.read_csv(path, parse_dates=["Date"], dayfirst=True, encoding="latin1")
        df_list.append(df_parziale)

df_unificato = pd.concat(df_list, ignore_index=True)

print(f"Totale righe dati unificati: {len(df_unificato)}")
print(df_unificato.head())

import requests
import os
import pandas as pd

def aggiorna_stagione_corrente():
    """
    Scarica e sovrascrive solo il file della stagione corrente 2025-26
    
    ⚠️  ATTENZIONE: Questo script SOVRASCRIVE sempre il file I1_2526.csv
    - Usa questo script quando vuoi forzare l'aggiornamento dei dati della stagione corrente
    - Lo script 'scarica_dati_storici.py' invece salta il download se il file esiste già
    - Non crea duplicazioni: entrambi gli script gestiscono lo stesso file I1_2526.csv
    """
    # URL del campionato in corso
    url_corrente = 'https://www.football-data.co.uk/mmz4281/2526/I1.csv'
    filename = "I1_2526.csv"
    filepath = os.path.join("data", filename)
    
    # Assicurati che la cartella data esista
    os.makedirs("data", exist_ok=True)
    
    print(f"Scaricando dati aggiornati della stagione 2025-26...")
    
    try:
        # Scarica sempre il file, sovrascrivendo quello esistente
        r = requests.get(url_corrente)
        r.raise_for_status()
        
        with open(filepath, "wb") as f:
            f.write(r.content)
        
        print(f"✅ {filename} scaricato e aggiornato con successo!")
        
        # Verifica il contenuto scaricato
        df = pd.read_csv(filepath, parse_dates=["Date"], dayfirst=True, encoding="latin1")
        print(f"📊 Partite nel file aggiornato: {len(df)}")
        
        if len(df) > 0:
            ultima_partita = df['Date'].max()
            print(f"🗓️  Ultima partita nel dataset: {ultima_partita.strftime('%d/%m/%Y')}")
            
            # Mostra le ultime 3 partite
            print("\n🔄 Ultime 3 partite nel dataset:")
            ultime_partite = df.nlargest(3, 'Date')[['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']]
            for _, partita in ultime_partite.iterrows():
                print(f"   {partita['Date'].strftime('%d/%m')} - {partita['HomeTeam']} {partita['FTHG']}-{partita['FTAG']} {partita['AwayTeam']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore durante il download: {e}")
        return False
    except Exception as e:
        print(f"❌ Errore generico: {e}")
        return False

if __name__ == "__main__":
    success = aggiorna_stagione_corrente()
    if success:
        print("\n🎯 Aggiornamento completato! Ora puoi rigenerare le features.")
    else:
        print("\n💥 Aggiornamento fallito.")
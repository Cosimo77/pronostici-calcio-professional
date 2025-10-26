import pandas as pd
import numpy as np
from scripts.modelli_predittivi import PronosticiCalculator
from scripts.feature_engineering import FeatureEngineer
import os
from datetime import datetime, timedelta

class SistemaPronostici:
    def __init__(self):
        self.calculator = PronosticiCalculator()
        self.df_features = None
        self.squadre_disponibili = []
        
    def inizializza(self):
        """Inizializza il sistema caricando modelli e dati"""
        print("🏆 Inizializzazione Sistema Pronostici Serie A...")
        
        # Carica modelli
        if os.path.exists('models/metadata.pkl'):
            self.calculator.carica_modelli()
            print("✅ Modelli caricati con successo")
        else:
            print("❌ Modelli non trovati. Esegui prima modelli_predittivi.py")
            return False
        
        # Carica dataset features
        if os.path.exists('data/dataset_features.csv'):
            self.df_features = pd.read_csv('data/dataset_features.csv')
            self.df_features['Date'] = pd.to_datetime(self.df_features['Date'])
            print(f"✅ Dataset caricato: {len(self.df_features)} partite")
        else:
            print("❌ Dataset features non trovato. Esegui prima feature_engineering.py")
            return False
        
        # Lista squadre disponibili
        squadre_casa = set(self.df_features['HomeTeam'].unique())
        squadre_trasferta = set(self.df_features['AwayTeam'].unique())
        self.squadre_disponibili = sorted(squadre_casa.union(squadre_trasferta))
        print(f"✅ {len(self.squadre_disponibili)} squadre disponibili")
        
        return True
    
    def mostra_squadre(self):
        """Mostra tutte le squadre disponibili"""
        print("\n🏟️  SQUADRE DISPONIBILI:")
        for i, squadra in enumerate(self.squadre_disponibili, 1):
            print(f"{i:2d}. {squadra}")
    
    def predici_partita_interattiva(self):
        """Interfaccia interattiva per predire una partita"""
        print("\n🔮 PREDIZIONE PARTITA")
        
        # Selezione squadra di casa
        print("\nSeleziona la squadra di CASA:")
        self.mostra_squadre()
        
        try:
            scelta_casa = int(input("\nInserisci il numero della squadra di casa: "))
            if 1 <= scelta_casa <= len(self.squadre_disponibili):
                squadra_casa = self.squadre_disponibili[scelta_casa - 1]
            else:
                print("❌ Scelta non valida")
                return
        except ValueError:
            print("❌ Inserisci un numero valido")
            return
        
        # Selezione squadra in trasferta
        print(f"\nHai scelto: {squadra_casa}")
        print("\nSeleziona la squadra in TRASFERTA:")
        squadre_trasferta = [s for s in self.squadre_disponibili if s != squadra_casa]
        
        for i, squadra in enumerate(squadre_trasferta, 1):
            print(f"{i:2d}. {squadra}")
        
        try:
            scelta_trasferta = int(input("\nInserisci il numero della squadra in trasferta: "))
            if 1 <= scelta_trasferta <= len(squadre_trasferta):
                squadra_trasferta = squadre_trasferta[scelta_trasferta - 1]
            else:
                print("❌ Scelta non valida")
                return
        except ValueError:
            print("❌ Inserisci un numero valido")
            return
        
        # Effettua predizione
        print(f"\n⚽ PARTITA: {squadra_casa} vs {squadra_trasferta}")
        print("🤖 Calcolo predizione in corso...")
        
        try:
            pred, prob = self.calculator.predici_partita(squadra_casa, squadra_trasferta, self.df_features)
            
            if pred is None:
                print("❌ Impossibile fare la predizione. Dati insufficienti.")
                return
            
            # Mappa risultati
            risultato_map = {
                'H': f'Vittoria {squadra_casa}',
                'A': f'Vittoria {squadra_trasferta}',
                'D': 'Pareggio'
            }
            
            print(f"\n🎯 PREDIZIONE: {risultato_map[pred]}")
            # Calcola confidenza in modo sicuro
            if isinstance(prob, dict):
                confidenza = max(prob.values())
            else:
                confidenza = 0.0
            print(f"🎲 Confidenza: {confidenza:.1%}")
            
            # Mostra tutte le probabilità
            print(f"\n📊 PROBABILITÀ DETTAGLIATE:")
            prob_labels = ['Casa', 'Trasferta', 'Pareggio']
            for i, (label, p) in enumerate(zip(prob_labels, prob)):
                print(f"   {label}: {p:.1%}")
            
            # Consigli per scommesse
            self.mostra_consigli_scommesse(pred, prob, squadra_casa, squadra_trasferta)
            
        except Exception as e:
            print(f"❌ Errore durante la predizione: {e}")
    
    def mostra_consigli_scommesse(self, pred, prob, squadra_casa, squadra_trasferta):
        """Mostra consigli per le scommesse basati sulla predizione"""
        print(f"\n💡 CONSIGLI SCOMMESSE:")
        
        confidenza = prob.max()
        
        if confidenza >= 0.6:
            print("🟢 ALTA CONFIDENZA - Consigliato scommettere")
        elif confidenza >= 0.45:
            print("🟡 MEDIA CONFIDENZA - Scommessa con cautela")
        else:
            print("🔴 BASSA CONFIDENZA - Sconsigliato scommettere")
        
        # Analizza probabilità per Over/Under
        # Stima semplificata: probabilità alta vittoria = più gol
        if pred != 'D' and confidenza > 0.5:
            print("⚽ SUGGERIMENTO: Possibile Over 2.5 gol")
        elif pred == 'D':
            print("⚽ SUGGERIMENTO: Possibile Under 2.5 gol")
    
    def analizza_forma_squadre(self, squadra_casa, squadra_trasferta):
        """Analizza la forma recente delle due squadre"""
        print(f"\n📈 ANALISI FORMA RECENTE")
        
        # Controllo di sicurezza per df_features
        if self.df_features is None:
            print("❌ Dataset non caricato. Esegui prima inizializza()")
            return
        
        for squadra, tipo in [(squadra_casa, "CASA"), (squadra_trasferta, "TRASFERTA")]:
            print(f"\n🏟️  {squadra} ({tipo}):")
            
            # Strategia intelligente: cerca prima negli ultimi 90 giorni, poi espandi se necessario
            partite_recenti = None
            giorni_ricerca = [90, 180, 365]
            target_partite = 5
            
            for giorni in giorni_ricerca:
                data_limite = self.df_features['Date'].max() - timedelta(days=giorni)
                
                partite_candidati = self.df_features[
                    (self.df_features['Date'] >= data_limite) &
                    ((self.df_features['HomeTeam'] == squadra) | 
                     (self.df_features['AwayTeam'] == squadra))
                ].tail(target_partite)
                
                if len(partite_candidati) >= target_partite:
                    partite_recenti = partite_candidati
                    print(f"   📊 {squadra}: trovate {len(partite_recenti)} partite recenti")
                    break
                elif len(partite_candidati) > 0:
                    partite_recenti = partite_candidati
            
            # Se ancora non abbiamo abbastanza partite, prendiamo le ultime disponibili
            if partite_recenti is None or len(partite_recenti) < 3:
                partite_recenti = self.df_features[
                    ((self.df_features['HomeTeam'] == squadra) | 
                     (self.df_features['AwayTeam'] == squadra))
                ].tail(target_partite)
                
                if len(partite_recenti) > 0:
                    print(f"   📊 {squadra}: trovate {len(partite_recenti)} partite storiche")
                else:
                    print(f"   ❌ {squadra}: nessuna partita trovata!")
                    continue
            
            if len(partite_recenti) > 0:
                punti_totali = 0
                gol_fatti = 0
                gol_subiti = 0
                
                for _, partita in partite_recenti.iterrows():
                    if partita['HomeTeam'] == squadra:
                        gf = partita['FTHG']
                        gs = partita['FTAG']
                        if partita['FTR'] == 'H':
                            punti = 3
                        elif partita['FTR'] == 'D':
                            punti = 1
                        else:
                            punti = 0
                    else:
                        gf = partita['FTAG']
                        gs = partita['FTHG']
                        if partita['FTR'] == 'A':
                            punti = 3
                        elif partita['FTR'] == 'D':
                            punti = 1
                        else:
                            punti = 0
                    
                    punti_totali += punti
                    gol_fatti += gf
                    gol_subiti += gs
                
                media_punti = punti_totali / len(partite_recenti)
                media_gol_fatti = gol_fatti / len(partite_recenti)
                media_gol_subiti = gol_subiti / len(partite_recenti)
                
                print(f"   📊 Media punti: {media_punti:.1f}")
                print(f"   ⚽ Media gol fatti: {media_gol_fatti:.1f}")
                print(f"   🥅 Media gol subiti: {media_gol_subiti:.1f}")
                print(f"   🎯 Ultime {len(partite_recenti)} partite analizzate")
            else:
                print("   ❌ Dati insufficienti")
    
    def menu_principale(self):
        """Menu principale del sistema"""
        while True:
            print("\n" + "="*50)
            print("🏆 SISTEMA PRONOSTICI SERIE A")
            print("="*50)
            print("1. 🔮 Predici una partita")
            print("2. 🏟️  Mostra squadre disponibili")
            print("3. 📈 Analizza forma squadre")
            print("4. ❌ Esci")
            
            try:
                scelta = input("\nSeleziona un'opzione (1-4): ").strip()
                
                if scelta == '1':
                    self.predici_partita_interattiva()
                elif scelta == '2':
                    self.mostra_squadre()
                elif scelta == '3':
                    print("\nInserisci due squadre per analizzare la loro forma:")
                    self.mostra_squadre()
                    try:
                        idx1 = int(input("Squadra 1: ")) - 1
                        idx2 = int(input("Squadra 2: ")) - 1
                        if 0 <= idx1 < len(self.squadre_disponibili) and 0 <= idx2 < len(self.squadre_disponibili):
                            self.analizza_forma_squadre(
                                self.squadre_disponibili[idx1],
                                self.squadre_disponibili[idx2]
                            )
                    except (ValueError, IndexError):
                        print("❌ Selezione non valida")
                elif scelta == '4':
                    print("👋 Arrivederci!")
                    break
                else:
                    print("❌ Opzione non valida. Scegli tra 1-4.")
                    
            except KeyboardInterrupt:
                print("\n👋 Arrivederci!")
                break

def main():
    sistema = SistemaPronostici()
    
    if sistema.inizializza():
        sistema.menu_principale()
    else:
        print("\n❌ Impossibile inizializzare il sistema.")
        print("Assicurati di aver eseguito prima:")
        print("1. scarica_dati_storici.py")
        print("2. analizza_dati.py") 
        print("3. feature_engineering.py")
        print("4. modelli_predittivi.py")

if __name__ == "__main__":
    main()
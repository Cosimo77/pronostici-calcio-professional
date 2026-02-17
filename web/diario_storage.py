"""
Diario Betting Storage Adapter
Interfaccia unificata per PostgreSQL + CSV fallback
"""

import os
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()

# Import condizionale database module
try:
    from database import BetModel, is_db_available
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False


class DiarioStorage:
    """
    Adapter pattern: PostgreSQL se disponibile, altrimenti CSV fallback
    Garantisce funzionamento anche senza database
    """
    
    CSV_FILE = 'tracking_giocate.csv'
    
    @staticmethod
    def _use_database():
        """Check se usare database o CSV"""
        use_db = DB_AVAILABLE and is_db_available()
        logger.info(f"🔍 _use_database() check",
                    DB_AVAILABLE=DB_AVAILABLE,
                    is_db_available=is_db_available() if DB_AVAILABLE else "N/A",
                    result=use_db)
        return use_db
    
    @staticmethod
    def get_all_bets(risultato: Optional[str] = None) -> List[Dict]:
        """Ottieni tutte le bet, opzionalmente filtrate"""
        if DiarioStorage._use_database():
            try:
                return BetModel.get_all(risultato=risultato)
            except Exception as e:
                logger.error("Database query failed, falling back to CSV", error=str(e))
                # Fall through to CSV
        
        # CSV fallback
        if not os.path.exists(DiarioStorage.CSV_FILE):
            return []
        
        df = pd.read_csv(DiarioStorage.CSV_FILE)
        
        if risultato:
            df = df[df['Risultato'] == risultato]
        
        bets = []
        for idx, row in df.iterrows():
            bets.append({
                'id': int(idx),  # type: ignore[arg-type]
                'data': str(row['Data']),
                'partita': str(row['Partita']),
                'mercato': str(row['Mercato']),
                'quota_sistema': float(row['Quota_Sistema']) if pd.notna(row['Quota_Sistema']) else None,
                'quota_sisal': float(row['Quota_Sisal']),
                'ev_modello': str(row['EV_Modello']) if pd.notna(row['EV_Modello']) else 'N/A',
                'ev_realistico': str(row['EV_Realistico']) if pd.notna(row['EV_Realistico']) else 'N/A',
                'stake': str(row['Stake']),
                'risultato': str(row['Risultato']),
                'profit': float(row['Profit']) if pd.notna(row['Profit']) else 0.0,
                'note': str(row['Note']) if pd.notna(row['Note']) else ''
            })
        
        return bets
    
    @staticmethod
    def create_bet(data: Dict) -> int:
        """Crea nuova bet"""
        if DiarioStorage._use_database():
            try:
                # Converti data da stringa a oggetto date Python (supporta ISO e italiano)
                if 'data' in data and isinstance(data['data'], str):
                    try:
                        # Prova prima formato ISO (da HTML input type="date"): YYYY-MM-DD
                        data_obj = datetime.strptime(data['data'], '%Y-%m-%d').date()
                        data['data'] = data_obj
                    except ValueError:
                        try:
                            # Fallback: formato italiano DD/MM/YYYY
                            data_obj = datetime.strptime(data['data'], '%d/%m/%Y').date()
                            data['data'] = data_obj
                        except ValueError:
                            # Ultimo fallback: usa data corrente
                            data['data'] = datetime.now().date()
                            logger.warning(f"⚠️ Formato data non riconosciuto: {data['data']}, uso data odierna")
                
                return BetModel.create(data)
            except Exception as e:
                logger.error("Database insert failed, falling back to CSV", error=str(e))
                # Fall through to CSV
        
        # CSV fallback
        if os.path.exists(DiarioStorage.CSV_FILE):
            df = pd.read_csv(DiarioStorage.CSV_FILE)
        else:
            df = pd.DataFrame(columns=['Data', 'Partita', 'Mercato', 'Quota_Sistema', 'Quota_Sisal',
                                      'EV_Modello', 'EV_Realistico', 'Stake', 'Risultato', 'Profit', 'Note'])
        
        quota = round(float(data['quota_sisal']), 2)
        
        new_row = pd.DataFrame([{
            'Data': data.get('data', datetime.now().strftime('%d/%m/%Y')),
            'Partita': data['partita'],
            'Mercato': data['mercato'],
            'Quota_Sistema': quota,
            'Quota_Sisal': quota,
            'EV_Modello': data.get('ev_modello', 'N/A'),
            'EV_Realistico': data.get('ev_realistico', 'N/A'),
            'Stake': str(data['stake']),
            'Risultato': 'PENDING',
            'Profit': 0.0,
            'Note': data.get('note', '')
        }])
        
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DiarioStorage.CSV_FILE, index=False)
        
        return len(df) - 1  # Row index
    
    @staticmethod
    def update_risultato(bet_id: int, risultato: str) -> float:
        """Aggiorna risultato bet"""
        if DiarioStorage._use_database():
            try:
                return BetModel.update_risultato(bet_id, risultato)
            except Exception as e:
                logger.error("Database update failed, falling back to CSV", error=str(e))
                # Fall through to CSV
        
        # CSV fallback
        df = pd.read_csv(DiarioStorage.CSV_FILE)
        
        if bet_id >= len(df):
            raise ValueError(f"Bet {bet_id} not found")
        
        quota = float(df.at[bet_id, 'Quota_Sisal'])  # type: ignore[arg-type]
        stake_raw = df.at[bet_id, 'Stake']
        
        try:
            stake = float(stake_raw)  # type: ignore[arg-type]
        except ValueError:
            stake = 0.0  # MONITOR
        
        if risultato == 'WIN':
            profit = stake * (quota - 1)
        elif risultato == 'LOSS':
            profit = -stake
        else:  # VOID, SKIP
            profit = 0.0
        
        df.at[bet_id, 'Risultato'] = risultato
        df.at[bet_id, 'Profit'] = round(profit, 2)
        df.to_csv(DiarioStorage.CSV_FILE, index=False)
        
        return profit
    
    @staticmethod
    def update_fields(bet_id: int, updates: Dict):
        """Aggiorna campi bet"""
        if DiarioStorage._use_database():
            try:
                BetModel.update_fields(bet_id, updates)
                return
            except Exception as e:
                logger.error("Database update failed, falling back to CSV", error=str(e))
        
        # CSV fallback
        df = pd.read_csv(DiarioStorage.CSV_FILE)
        
        if 'stake' in updates:
            df.at[bet_id, 'Stake'] = str(updates['stake'])
        if 'quota_sisal' in updates:
            df.at[bet_id, 'Quota_Sisal'] = round(float(updates['quota_sisal']), 2)
        if 'note' in updates:
            df.at[bet_id, 'Note'] = updates['note']
        
        df.to_csv(DiarioStorage.CSV_FILE, index=False)
    
    @staticmethod
    def delete_bet(bet_id: int):
        """Elimina bet"""
        if DiarioStorage._use_database():
            try:
                BetModel.delete(bet_id)
                return
            except Exception as e:
                logger.error("Database delete failed, falling back to CSV", error=str(e))
        
        # CSV fallback
        df = pd.read_csv(DiarioStorage.CSV_FILE)
        df = df.drop(bet_id).reset_index(drop=True)
        df.to_csv(DiarioStorage.CSV_FILE, index=False)
    
    @staticmethod
    def check_duplicate(partita: str, mercato: str) -> Optional[Dict]:
        """Verifica duplicati pending"""
        if DiarioStorage._use_database():
            try:
                return BetModel.check_duplicate(partita, mercato)
            except Exception as e:
                logger.error("Database check failed, falling back to CSV", error=str(e))
        
        # CSV fallback
        df = pd.read_csv(DiarioStorage.CSV_FILE)
        duplicates = df[(df['Partita'] == partita) & 
                       (df['Mercato'] == mercato) & 
                       (df['Risultato'] == 'PENDING')]
        
        if len(duplicates) > 0:
            row = duplicates.iloc[0]
            return {
                'quota': float(row['Quota_Sisal']),
                'stake': str(row['Stake'])
            }
        
        return None

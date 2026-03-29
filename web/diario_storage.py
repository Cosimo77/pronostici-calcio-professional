"""
Diario Betting Storage Adapter
Interfaccia unificata per PostgreSQL + CSV fallback
"""

import os
import shutil
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
        """
        Check se usare database o CSV
        Lazy initialization: se DATABASE_URL presente ma pool non inizializzato, prova init
        """
        if not DB_AVAILABLE:
            logger.info("🔍 _use_database() = False (DB module not available)")
            return False
        
        # Check se pool già inizializzato
        if is_db_available():
            logger.info("🔍 _use_database() = True (pool già attivo)")
            return True
        
        # Lazy init: DATABASE_URL presente ma pool non inizializzato?
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            logger.warning("⚠️ DATABASE_URL presente ma pool non inizializzato - tentativo lazy init...")
            try:
                from database import init_db
                success = init_db()
                if success:
                    logger.info("✅ Lazy init SUCCESS - PostgreSQL attivo")
                    return True
                else:
                    logger.warning("❌ Lazy init FAILED - fallback CSV")
                    return False
            except Exception as e:
                logger.error("❌ Lazy init exception", error=str(e))
                return False
        
        # Nessun DATABASE_URL configurato
        logger.info("🔍 _use_database() = False (no DATABASE_URL)")
        return False
    
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
                'group_id': str(row['group_id']) if pd.notna(row['group_id']) and row['group_id'] != '' else None,
                'bet_number': int(row['bet_number']) if 'bet_number' in row and pd.notna(row['bet_number']) else 1,
                'tipo_bet': str(row['tipo_bet']) if 'tipo_bet' in row and pd.notna(row['tipo_bet']) else 'SINGLE',
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
            df = pd.DataFrame(columns=['group_id', 'bet_number', 'tipo_bet', 'Data', 'Partita', 'Mercato', 
                                      'Quota_Sistema', 'Quota_Sisal', 'EV_Modello', 'EV_Realistico', 
                                      'Stake', 'Risultato', 'Profit', 'Note'])
        
        quota = round(float(data['quota_sisal']), 2)
        
        new_row = pd.DataFrame([{
            'group_id': data.get('group_id', ''),  # Vuoto per bet singole
            'bet_number': data.get('bet_number', 1),
            'tipo_bet': data.get('tipo_bet', 'SINGLE'),
            'Data': data.get('data', datetime.now().strftime('%d/%m/%Y')),
            'Partita': data['partita'],
            'Mercato': data['mercato'],
            'Quota_Sistema': quota,
            'Quota_Sisal': quota,
            'EV_Modello': data.get('ev_modello', 'N/A'),
            'EV_Realistico': data.get('ev_realistico', 'N/A'),
            'Stake': str(data['stake']),
            'Risultato': data.get('risultato', 'PENDING'),
            'Profit': data.get('profit', 0.0),
            'Note': data.get('note', '')
        }])
        
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(DiarioStorage.CSV_FILE, index=False)
        
        return len(df) - 1  # Row index
    
    @staticmethod
    def update_risultato(bet_id: int, risultato: str) -> float:
        """Aggiorna risultato bet (singola o evento multipla)"""
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
        
        # Aggiorna risultato evento
        df.at[bet_id, 'Risultato'] = risultato
        
        # Check se parte di multipla
        tipo_bet = str(df.at[bet_id, 'tipo_bet']) if 'tipo_bet' in df.columns else 'SINGLE'
        
        if tipo_bet == 'MULTIPLA':
            group_id = str(df.at[bet_id, 'group_id'])
            
            # Aggiorna tutti gli eventi della multipla
            df_multipla = df[df['group_id'] == group_id]
            risultati = df_multipla['Risultato'].tolist()
            
            # Logica multipla: basta 1 LOSS → tutta LOSS
            if risultato in ['LOSS', 'SKIP'] or 'LOSS' in risultati or 'SKIP' in risultati:
                # Multipla persa
                stake = float(df_multipla.iloc[0]['Stake'])
                profit = -stake
                
                # Aggiorna tutti gli eventi con profit negativo
                for idx in df_multipla.index:
                    df.at[idx, 'Profit'] = round(profit, 2)
            
            elif all(r == 'WIN' for r in risultati):
                # Multipla vinta: calcola profit totale
                stake = float(df_multipla.iloc[0]['Stake'])  # type: ignore[arg-type]
                quota_totale = 1.0
                for idx in df_multipla.index:
                    quota_totale *= float(df.at[idx, 'Quota_Sisal'])  # type: ignore[arg-type]
                
                profit = stake * (quota_totale - 1)
                
                # Aggiorna tutti gli eventi con profit positivo
                for idx in df_multipla.index:
                    df.at[idx, 'Profit'] = round(profit, 2)
            
            else:
                # Ancora PENDING
                profit = 0.0
                df.at[bet_id, 'Profit'] = 0.0
        
        else:
            # Bet singola: calcolo normale
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
    
    @staticmethod
    def reset_all() -> str:
        """
        Reset completo diario (PERICOLOSO!)
        Crea backup automatico prima di cancellare
        
        Returns:
            Nome file backup creato
        """
        if DiarioStorage._use_database():
            try:
                # TODO: Implementare reset database (DROP TABLE + CREATE TABLE)
                logger.warning("⚠️ Reset database non ancora implementato, fallback to CSV")
                # Fall through to CSV
            except Exception as e:
                logger.error("Database reset failed", error=str(e))
        
        # CSV reset
        if not os.path.exists(DiarioStorage.CSV_FILE):
            raise FileNotFoundError("File diario non trovato")
        
        # Backup con timestamp (microsecondi per evitare collisioni)
        import shutil
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        backup_file = DiarioStorage.CSV_FILE.replace('.csv', f'_backup_{timestamp}.csv')
        
        # Se file esiste già (race condition), aggiungi suffisso
        counter = 1
        while os.path.exists(backup_file):
            backup_file = DiarioStorage.CSV_FILE.replace('.csv', f'_backup_{timestamp}_{counter}.csv')
            counter += 1
            if counter > 100:  # Safety limit
                raise RuntimeError("Impossibile creare file backup univoco")
        
        try:
            shutil.copy2(DiarioStorage.CSV_FILE, backup_file)
            logger.warning(f"⚠️ Backup diario creato: {backup_file}")
        except PermissionError as e:
            # Se fallisce per permessi, prova con nome alternativo
            logger.error(f"Permission error su {backup_file}, provo nome alternativo")
            import time
            time.sleep(0.1)  # Small delay
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            backup_file = DiarioStorage.CSV_FILE.replace('.csv', f'_backup_{timestamp}_alt.csv')
            shutil.copy2(DiarioStorage.CSV_FILE, backup_file)
            logger.warning(f"⚠️ Backup diario creato (alternativo): {backup_file}")
        
        # Reset CSV (solo header)
        header_row = pd.DataFrame(columns=[
            'Data', 'Partita', 'Mercato', 'Quota_Sistema', 'Quota_Sisal',
            'EV_Modello', 'EV_Realistico', 'Stake', 'Risultato', 'Profit', 'Note'
        ])
        header_row.to_csv(DiarioStorage.CSV_FILE, index=False)
        
        logger.warning("🔴 Diario resettato completamente via DiarioStorage")
        
        return os.path.basename(backup_file)
    
    # ==================== SCOMMESSE MULTIPLE ====================
    
    @staticmethod
    def create_multipla(multipla_data: Dict, eventi: List[Dict]) -> str:
        """
        Crea scommessa multipla con eventi associati
        
        Args:
            multipla_data: {
                'data': date | str,
                'nome': str,
                'tipo_multipla': str,
                'quota_totale': float,
                'stake': float,
                'note': str
            }
            eventi: List di dict (come in create_bet) senza risultato
        
        Returns:
            group_id: ID della multipla creata (stringa)
        """
        if DiarioStorage._use_database():
            # Versione PostgreSQL (già implementata)
            pass  # Codice originale segue sotto
        
        try:
            from database.bet_group_model import BetGroupModel
            
            # Converti data se stringa
            if 'data' in multipla_data and isinstance(multipla_data['data'], str):
                try:
                    multipla_data['data'] = datetime.strptime(multipla_data['data'], '%Y-%m-%d').date()
                except ValueError:
                    try:
                        multipla_data['data'] = datetime.strptime(multipla_data['data'], '%d/%m/%Y').date()
                    except ValueError:
                        multipla_data['data'] = datetime.now().date()
            
            # Valida numero eventi
            if len(eventi) < 2:
                raise ValueError("Multipla richiede almeno 2 eventi")
            
            # Calcola tipo multipla automaticamente
            num_eventi = len(eventi)
            tipi = {2: 'doppia', 3: 'tripla', 4: 'quadrupla', 5: 'quintupla', 
                   6: 'sestina', 7: 'settina', 8: 'ottina'}
            tipo_multipla = tipi.get(num_eventi, f'{num_eventi}-pla')
            
            multipla_data['tipo_multipla'] = tipo_multipla
            multipla_data['num_eventi'] = num_eventi
            
            # Crea group
            group_id = BetGroupModel.create(multipla_data)
            
            # Crea eventi associati
            for evento in eventi:
                evento_data = evento.copy()
                evento_data['risultato'] = 'PENDING'
                evento_data['profit'] = 0.0
                evento_data['group_id'] = group_id  # Link a multipla
                
                # Converti data evento
                if 'data' not in evento_data:
                    evento_data['data'] = multipla_data['data']
                elif isinstance(evento_data['data'], str):
                    try:
                        evento_data['data'] = datetime.strptime(evento_data['data'], '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            evento_data['data'] = datetime.strptime(evento_data['data'], '%d/%m/%Y').date()
                        except ValueError:
                            evento_data['data'] = multipla_data['data']
                
                BetModel.create(evento_data)
            
            logger.info("Multipla creata con successo (DB)", group_id=group_id, num_eventi=num_eventi)
            return str(group_id)
            
        except ImportError:
            logger.warning("BetGroupModel non disponibile, fallback to CSV")
            # Fall through to CSV
        except Exception as e:
            logger.error("Errore creazione multipla DB, fallback to CSV", error=str(e))
            # Fall through to CSV
        
        # CSV fallback implementation
        if len(eventi) < 2:
            raise ValueError("Multipla richiede almeno 2 eventi")
        
        # Genera group_id univoco (timestamp + random)
        import uuid
        group_id = f"MULT{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6].upper()}"
        
        # Calcola tipo multipla
        num_eventi = len(eventi)
        tipi = {2: 'doppia', 3: 'tripla', 4: 'quadrupla', 5: 'quintupla', 
               6: 'sestina', 7: 'settina', 8: 'ottina'}
        tipo_multipla = tipi.get(num_eventi, f'{num_eventi}-pla')
        
        # Converti data
        data_str = multipla_data.get('data', datetime.now().strftime('%Y-%m-%d'))
        if isinstance(data_str, str):
            try:
                data_obj = datetime.strptime(data_str, '%Y-%m-%d')
            except ValueError:
                try:
                    data_obj = datetime.strptime(data_str, '%d/%m/%Y')
                except ValueError:
                    data_obj = datetime.now()
            data_str = data_obj.strftime('%Y-%m-%d')
        
        # Crea eventi  multipla nel CSV
        stake_per_evento = float(multipla_data['stake'])
        
        for idx, evento in enumerate(eventi, start=1):
            evento_data = {
                'group_id': group_id,
                'bet_number': idx,
                'tipo_bet': 'MULTIPLA',
                'data': data_str,
                'partita': evento['partita'],
                'mercato': evento['mercato'],
                'quota_sisal': evento['quota_sisal'],
                'ev_modello': evento.get('ev_modello', 'N/A'),
                'ev_realistico': evento.get('ev_realistico', 'N/A'),
                'stake': stake_per_evento,
                'risultato': 'PENDING',
                'profit': 0.0,
                'note': f"{tipo_multipla.upper()} - Quota totale: {multipla_data['quota_totale']:.2f} - {multipla_data.get('note', '')}"
            }
            DiarioStorage.create_bet(evento_data)
        
        logger.info("Multipla creata con successo (CSV)", group_id=group_id, num_eventi=num_eventi, tipo=tipo_multipla)
        return group_id
    
    @staticmethod
    def get_all_multiple(risultato: Optional[str] = None) -> List[Dict]:
        """
        Ottieni tutte le multiple (con eventi nested)
        
        Args:
            risultato: 'PENDING', 'WIN', 'LOSS', 'VOID' (None = tutte)
        
        Returns:
            List di dict con chiave 'eventi' contenente lista eventi
        """
        if DiarioStorage._use_database():
            try:
                from database.bet_group_model import BetGroupModel
                
                groups = BetGroupModel.get_all(risultato=risultato)
                
                # Arricchisci ogni multipla con eventi nested
                for group in groups:
                    group_id = group['id']
                    # Get eventi associati a questa multipla
                    eventi = [bet for bet in DiarioStorage.get_all_bets() if bet.get('group_id') == group_id]
                    group['eventi'] = eventi
                
                logger.info("Multiple recuperate da DB", count=len(groups))
                return groups
                
            except ImportError:
                logger.warning("BetGroupModel non disponibile, fallback to CSV")
                # Fall through to CSV
            except Exception as e:
                logger.error("Errore get multiple DB, fallback to CSV", error=str(e))
                # Fall through to CSV
        
        # CSV fallback implementation
        if not os.path.exists(DiarioStorage.CSV_FILE):
            return []
        
        df = pd.read_csv(DiarioStorage.CSV_FILE)
        
        # Filtra solo bet multiple
        df_multiple = df[df['tipo_bet'] == 'MULTIPLA']
        
        if len(df_multiple) == 0:
            return []
        
        # Raggruppa per group_id
        multiple_dict = {}
        for idx, row in df_multiple.iterrows():
            group_id = str(row['group_id'])
            
            if group_id not in multiple_dict:
                # Estrai info multipla dalla prima riga del gruppo
                note_parts = str(row['Note']).split(' - ')
                tipo_multipla = note_parts[0] if len(note_parts) > 0 else 'multipla'
                quota_totale_str = note_parts[1] if len(note_parts) > 1 else 'Quota totale: 0.00'
                quota_totale = float(quota_totale_str.replace('Quota totale: ', '').replace(',', '.'))
                
                multiple_dict[group_id] = {
                    'id': group_id,
                    'data': str(row['Data']),
                    'tipo_multipla': tipo_multipla.lower(),
                    'quota_totale': quota_totale,
                    'stake': float(row['Stake']),
                    'risultato': str(row['Risultato']),
                    'profit': 0.0,  # Calcolato dopo
                    'note': str(row['Note']),
                    'eventi': []
                }
            
            # Aggiungi evento alla multipla
            evento = {
                'id': int(idx),  # type: ignore[arg-type]
                'bet_number': int(row['bet_number']),
                'partita': str(row['Partita']),
                'mercato': str(row['Mercato']),
                'quota_sisal': float(row['Quota_Sisal']),
                'risultato': str(row['Risultato']),
                'profit': float(row['Profit']) if pd.notna(row['Profit']) else 0.0
            }
            multiple_dict[group_id]['eventi'].append(evento)
        
        # Calcola risultato e profit per ogni multipla
        for group_id, multipla in multiple_dict.items():
            eventi = multipla['eventi']
            
            # Verifica risultati
            risultati = [e['risultato'] for e in eventi]
            
            if 'LOSS' in risultati or 'SKIP' in risultati:
                multipla['risultato'] = 'LOSS'
                multipla['profit'] = -multipla['stake']
            elif all(r == 'WIN' for r in risultati):
                multipla['risultato'] = 'WIN'
                multipla['profit'] = multipla['stake'] * (multipla['quota_totale'] - 1)
            elif 'VOID' in risultati and 'PENDING' not in risultati:
                # Cancella evento VOID, ricalcola quota
                events_valid = [e for e in eventi if e['risultato'] != 'VOID']
                if all(e['risultato'] == 'WIN' for e in events_valid):
                    quota_ridotta = 1.0
                    for e in events_valid:
                        quota_ridotta *= e['quota_sisal']
                    multipla['risultato'] = 'WIN'
                    multipla['profit'] = multipla['stake'] * (quota_ridotta - 1)
                else:
                    multipla['risultato'] = 'LOSS'
                    multipla['profit'] = -multipla['stake']
            else:
                multipla['risultato'] = 'PENDING'
                multipla['profit'] = 0.0
        
        # Filtra per risultato se richiesto
        multiple_list = list(multiple_dict.values())
        if risultato:
            multiple_list = [m for m in multiple_list if m['risultato'] == risultato]
        
        return multiple_list
    
    @staticmethod
    def update_evento_multipla(bet_id: int, risultato: str) -> float:
        """
        Aggiorna risultato di un singolo evento in una multipla
        Poi ricalcola risultato finale della multipla
        
        Args:
            bet_id: ID evento da aggiornare
            risultato: 'WIN', 'LOSS', 'VOID', 'SKIP'
        
        Returns:
            profit: Profit finale della multipla (0.0 se ancora pending)
        """
        if DiarioStorage._use_database():
            # Versione PostgreSQL (già implementata)
            pass  # Codice originale segue
        
        try:
            from database.bet_group_model import BetGroupModel
            
            # Aggiorna singolo evento (profit calcolato automaticamente)
            BetModel.update_risultato(bet_id, risultato)
            
            # Recupera group_id dell'evento
            bet = BetModel.get_by_id(bet_id)
            if not bet or not bet.get('group_id'):
                raise ValueError(f"Evento {bet_id} non appartiene a una multipla")
            
            group_id = bet['group_id']
            
            # Ricalcola risultato multipla
            profit = BetGroupModel.update_risultato(group_id)
            
            logger.info("Evento multipla aggiornato (DB)", bet_id=bet_id, group_id=group_id, 
                       risultato=risultato, profit_finale=profit)
            
            return profit
            
        except ImportError:
            logger.warning("BetGroupModel non disponibile, fallback to CSV")
            # Fall through to CSV
        except Exception as e:
            logger.error("Errore update evento multipla DB, fallback to CSV", bet_id=bet_id, error=str(e))
            # Fall through to CSV
        
        # CSV fallback: usa update_risultato che già gestisce multiple
        profit = DiarioStorage.update_risultato(bet_id, risultato)
        
        logger.info("Evento multipla aggiornato (CSV)", bet_id=bet_id, 
                   risultato=risultato, profit_finale=profit)
        
        return profit
    
    @staticmethod
    def delete_multipla(group_id: str) -> bool:
        """Elimina multipla (CASCADE elimina anche eventi)"""
        if DiarioStorage._use_database():
            # Versione PostgreSQL
            pass  # Codice originale segue
        
        try:
            from database.bet_group_model import BetGroupModel
            return BetGroupModel.delete(int(group_id))  # Convert to int for DB
        except Exception as e:
            logger.error("Errore delete multipla DB, fallback to CSV", group_id=group_id, error=str(e))
            # Fall through to CSV
        
        # CSV fallback
        if not os.path.exists(DiarioStorage.CSV_FILE):
            return False
        
        df = pd.read_csv(DiarioStorage.CSV_FILE)
        
        # Filtra out tutte le righe con questo group_id
        df_filtered = df[df['group_id'] != group_id]
        
        num_deleted = len(df) - len(df_filtered)
        
        if num_deleted > 0:
            df_filtered.to_csv(DiarioStorage.CSV_FILE, index=False)
            logger.info(f"Multipla eliminata (CSV): group_id={group_id}, {num_deleted} eventi rimossi")
            return True
        else:
            logger.warning(f"Multipla non trovata per eliminazione: group_id={group_id}")
            return False

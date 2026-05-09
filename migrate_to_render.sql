-- MIGRAZIONE TRACKING_GIOCATE
-- Esegui questo SQL sul database Render

-- 1. Crea tabella (schema aggiornato per tracking avanzato)
CREATE TABLE IF NOT EXISTS tracking_giocate (
    id SERIAL PRIMARY KEY,
    group_id VARCHAR(50),
    bet_number INTEGER,
    tipo_bet VARCHAR(20),
    data_giocata DATE NOT NULL,
    partita VARCHAR(100) NOT NULL,
    mercato VARCHAR(100),
    quota_sistema DECIMAL(5,2),
    quota_sisal DECIMAL(5,2),
    ev_modello VARCHAR(20),
    ev_realistico VARCHAR(20),
    stake DECIMAL(10,2) NOT NULL,
    risultato VARCHAR(20),
    profit DECIMAL(10,2),
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Inserisci dati

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-14', 'Como vs Fiorentina', 'X2', 2.1, 2.1, '+22.3%', '6.4', 2.0, 'WIN', 2.2, '');

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-15', 'Udinese vs Sassuolo', '1X', 1.36, 1.36, '+20.5%', '+5.9%', 0.0, 'LOSS', -0.0, 'DOUBLE CHANCE - EV 20.5% | Quota aggiornata: 1.5 → 1.36');

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-15', 'Parma vs Verona', '1X', 1.3, 1.3, '+23.4%', '+6.7%', 0.0, 'WIN', 0.0, 'DOUBLE CHANCE - EV 23.4% | Quota aggiornata: 1.45 → 1.30');

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-09', 'Roma vs Cagliari', 'Over/Under 2.5 - Over 2.5', 2.1, 2.1, '+17.7%', '', 10.0, 'LOSS', -10.0, 'Partita finita 2-0 (Under 2.5)');

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-15', 'Cremonese vs Genoa', 'Pareggio', 2.97, 2.97, '+28.4%', '', 10.0, 'WIN', 19.700000000000003, 'Auto-generato 2026-02-12 21:26');

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-15', 'Parma vs Verona', 'Over/Under 2.5 - Over 2.5', 2.48, 2.48, '+25.4%', '', 10.0, 'WIN', 14.8, 'Auto-generato 2026-02-12 21:26');

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-15', 'Parma vs Verona', 'Double Chance - 1X', 1.45, 1.45, '+23.1%', '', 10.0, 'WIN', 4.5, 'Auto-generato 2026-02-12 21:26');

INSERT INTO tracking_giocate (group_id, bet_number, tipo_bet, data_giocata, partita, mercato, quota_sistema, quota_sisal, ev_modello, ev_realistico, stake, risultato, profit, note)
VALUES ('', 1, 'SINGLE', '2026-02-15', 'Napoli vs Roma', 'Double Chance - 1X', 1.44, 1.44, '+17.7%', '', 10.0, 'WIN', 4.399999999999999, 'Auto-generato 2026-02-12 21:26');

-- 3. Verifica
SELECT COUNT(*) as total_records FROM tracking_giocate;
SELECT * FROM tracking_giocate ORDER BY data_giocata DESC LIMIT 5;

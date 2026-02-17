-- Migration 002: Aggiunta tabella bet_groups per scommesse multiple
-- Data: 17/02/2026
-- Descrizione: Supporto per combo/sistemi (doppia, tripla, quadrupla, ecc.)

-- Tabella per rappresentare le scommesse multiple (combo)
CREATE TABLE IF NOT EXISTS bet_groups (
    id SERIAL PRIMARY KEY,
    data DATE NOT NULL,
    nome VARCHAR(255),  -- Nome descrittivo (es. "Tripla Serie A Weekend")
    tipo_multipla VARCHAR(50) NOT NULL,  -- 'doppia', 'tripla', 'quadrupla', 'quintupla', etc.
    num_eventi INT NOT NULL CHECK (num_eventi >= 2),  -- Numero eventi nella combo
    quota_totale DECIMAL(10, 2) NOT NULL CHECK (quota_totale >= 1.01),  -- Quota finale (prodotto)
    stake DECIMAL(10, 2) NOT NULL CHECK (stake > 0),
    risultato VARCHAR(10) NOT NULL DEFAULT 'PENDING',  -- PENDING, WIN, LOSS, VOID
    profit DECIMAL(10, 2) DEFAULT 0.0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggiungi campo group_id alla tabella bets (FK a bet_groups)
ALTER TABLE bets ADD COLUMN IF NOT EXISTS group_id INT REFERENCES bet_groups(id) ON DELETE CASCADE;

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_bet_groups_risultato ON bet_groups(risultato);
CREATE INDEX IF NOT EXISTS idx_bet_groups_data ON bet_groups(data DESC);
CREATE INDEX IF NOT EXISTS idx_bets_group_id ON bets(group_id);

-- Commenti per documentazione
COMMENT ON TABLE bet_groups IS 'Scommesse multiple (combo): doppia, tripla, ecc.';
COMMENT ON COLUMN bet_groups.tipo_multipla IS 'Tipo combo: doppia, tripla, quadrupla, quintupla';
COMMENT ON COLUMN bet_groups.quota_totale IS 'Quota finale calcolata come prodotto delle quote singole';
COMMENT ON COLUMN bets.group_id IS 'Se NULL=singola, se valorizzato=parte di multipla (FK a bet_groups)';

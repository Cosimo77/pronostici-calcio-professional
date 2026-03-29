-- Schema PostgreSQL per Diario Betting Professionale
-- Database: pronostici_calcio_production

-- Drop existing tables (solo per reset completo)
-- DROP TABLE IF EXISTS bets CASCADE;

-- Tabella principale puntate (supporta singole + multiple)
CREATE TABLE IF NOT EXISTS bets (
    id SERIAL PRIMARY KEY,
    
    -- Campi per multiple (opzionali se singola)
    group_id VARCHAR(50),  -- UUID gruppo per bet multiple
    bet_number INTEGER DEFAULT 1,  -- Numero bet nel gruppo (1,2,3...)
    tipo_bet VARCHAR(20) DEFAULT 'SINGLE',  -- SINGLE, DOUBLE, TRIPLE, SYSTEM
    
    -- Campi comuni
    data DATE NOT NULL,
    partita VARCHAR(100) NOT NULL,
    mercato VARCHAR(50) NOT NULL,
    quota_sistema DECIMAL(5,2),
    quota_sisal DECIMAL(5,2) NOT NULL,
    ev_modello VARCHAR(20),
    ev_realistico VARCHAR(20),
    stake VARCHAR(20) NOT NULL,  -- Può essere numero o 'MONITOR'
    risultato VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    profit DECIMAL(10,2) DEFAULT 0.0,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT chk_risultato CHECK (risultato IN ('PENDING', 'WIN', 'LOSS', 'VOID', 'SKIP')),
    CONSTRAINT chk_quota_sisal CHECK (quota_sisal >= 1.01),
    CONSTRAINT chk_tipo_bet CHECK (tipo_bet IN ('SINGLE', 'DOUBLE', 'TRIPLE', 'SYSTEM', 'ACCA'))
);

-- Indici (PostgreSQL richiede CREATE INDEX separato)
CREATE INDEX IF NOT EXISTS idx_risultato ON bets(risultato);
CREATE INDEX IF NOT EXISTS idx_data ON bets(data DESC);
CREATE INDEX IF NOT EXISTS idx_partita ON bets(partita);
CREATE INDEX IF NOT EXISTS idx_group_id ON bets(group_id) WHERE group_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tipo_bet ON bets(tipo_bet);

-- Trigger per auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_bets_updated_at BEFORE UPDATE ON bets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View per statistiche rapide
CREATE OR REPLACE VIEW v_bet_stats AS
SELECT 
    COUNT(*) as total_bets,
    COUNT(CASE WHEN risultato = 'PENDING' THEN 1 END) as pending_bets,
    COUNT(CASE WHEN risultato IN ('WIN', 'LOSS') THEN 1 END) as completed_bets,
    COUNT(CASE WHEN risultato = 'WIN' THEN 1 END) as wins,
    COUNT(CASE WHEN risultato = 'LOSS' THEN 1 END) as losses,
    COUNT(CASE WHEN risultato = 'SKIP' THEN 1 END) as skipped,
    COALESCE(SUM(CASE WHEN risultato IN ('WIN', 'LOSS') THEN profit ELSE 0 END), 0) as total_profit,
    COALESCE(AVG(CASE WHEN risultato IN ('WIN', 'LOSS') THEN profit END), 0) as avg_profit_per_bet
FROM bets;

-- View per equity curve (ordinata per data)
CREATE OR REPLACE VIEW v_equity_curve AS
SELECT 
    id,
    data,
    partita,
    risultato,
    profit,
    SUM(profit) OVER (ORDER BY data, id) as cumulative_profit
FROM bets
WHERE risultato IN ('WIN', 'LOSS')
ORDER BY data, id;

-- Commenti schema
COMMENT ON TABLE bets IS 'Diario betting professionale - Sistema value betting Serie A';
COMMENT ON COLUMN bets.stake IS 'Importo puntato (numerico) o MONITOR per tracking senza stake reale';
COMMENT ON COLUMN bets.ev_modello IS 'Expected Value calcolato dal modello ML (%)';
COMMENT ON COLUMN bets.ev_realistico IS 'Expected Value corretto dopo shrinkage 70% (%)';
COMMENT ON COLUMN bets.risultato IS 'PENDING=in attesa, WIN=vincente, LOSS=persa, VOID=annullata, SKIP=non giocata';

-- Grant permissions (eseguire dopo creazione database Render)
-- GRANT ALL PRIVILEGES ON TABLE bets TO render_user;
-- GRANT ALL PRIVILEGES ON SEQUENCE bets_id_seq TO render_user;
-- GRANT SELECT ON v_bet_stats TO render_user;
-- GRANT SELECT ON v_equity_curve TO render_user;

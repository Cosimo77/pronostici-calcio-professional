-- Schema Database PostgreSQL per Pronostici Calcio Enterprise
-- File: sql/init.sql

-- ============================================
-- TABELLE PRINCIPALI
-- ============================================

-- Squadre Serie A
CREATE TABLE IF NOT EXISTS squadre (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(50) NOT NULL UNIQUE,
    nome_completo VARCHAR(100),
    citta VARCHAR(50),
    fondazione INTEGER,
    stadium VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Partite storiche (migrazione da CSV)
CREATE TABLE IF NOT EXISTS partite (
    id SERIAL PRIMARY KEY,
    data_partita DATE NOT NULL,
    squadra_casa VARCHAR(50) NOT NULL,
    squadra_ospite VARCHAR(50) NOT NULL,
    gol_casa INTEGER,
    gol_ospite INTEGER,
    risultato VARCHAR(1), -- H, D, A
    stagione VARCHAR(10),
    giornata INTEGER,
    
    -- Features calcolate
    media_gol_casa DECIMAL(4,2),
    media_gol_ospite DECIMAL(4,2),
    forma_casa DECIMAL(4,2),
    forma_ospite DECIMAL(4,2),
    streak_casa INTEGER,
    streak_ospite INTEGER,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Predizioni generate
CREATE TABLE IF NOT EXISTS predizioni (
    id SERIAL PRIMARY KEY,
    squadra_casa VARCHAR(50) NOT NULL,
    squadra_ospite VARCHAR(50) NOT NULL,
    predizione VARCHAR(1) NOT NULL, -- H, D, A
    confidenza DECIMAL(5,3) NOT NULL,
    probabilita_h DECIMAL(5,3),
    probabilita_d DECIMAL(5,3), 
    probabilita_a DECIMAL(5,3),
    
    -- Mercati multipli (JSON)
    mercati_multipli JSONB,
    
    -- Metadata
    algoritmo VARCHAR(50) DEFAULT 'deterministic_ml',
    versione VARCHAR(20) DEFAULT '1.0.0',
    ip_richiedente INET,
    user_agent TEXT,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cache deterministiche
CREATE TABLE IF NOT EXISTS cache_predizioni (
    id SERIAL PRIMARY KEY,
    chiave_cache VARCHAR(255) NOT NULL UNIQUE,
    risultato JSONB NOT NULL,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- UTENTI E AUTENTICAZIONE (Business features)
-- ============================================

CREATE TABLE IF NOT EXISTS utenti (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nome VARCHAR(100),
    cognome VARCHAR(100),
    piano VARCHAR(20) DEFAULT 'free', -- free, pro, enterprise
    api_key VARCHAR(255) UNIQUE,
    rate_limit_remaining INTEGER DEFAULT 100,
    rate_limit_reset TIMESTAMP,
    
    -- Stato account
    attivo BOOLEAN DEFAULT true,
    verificato BOOLEAN DEFAULT false,
    ultimo_login TIMESTAMP,
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Log API per analytics
CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    utente_id INTEGER REFERENCES utenti(id),
    endpoint VARCHAR(255) NOT NULL,
    metodo VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    ip_address INET,
    user_agent TEXT,
    payload_size INTEGER,
    
    -- Business metrics
    piano_utente VARCHAR(20),
    costo_richiesta DECIMAL(8,4), -- Per billing
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- METRICHE E MONITORING
-- ============================================

CREATE TABLE IF NOT EXISTS metriche_sistema (
    id SERIAL PRIMARY KEY,
    metrica VARCHAR(100) NOT NULL,
    valore DECIMAL(10,2) NOT NULL,
    unita VARCHAR(20),
    categoria VARCHAR(50), -- performance, business, security
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- INDICI PER PERFORMANCE
-- ============================================

-- Indici partite
CREATE INDEX IF NOT EXISTS idx_partite_squadre ON partite(squadra_casa, squadra_ospite);
CREATE INDEX IF NOT EXISTS idx_partite_data ON partite(data_partita);
CREATE INDEX IF NOT EXISTS idx_partite_stagione ON partite(stagione);

-- Indici predizioni
CREATE INDEX IF NOT EXISTS idx_predizioni_squadre ON predizioni(squadra_casa, squadra_ospite);
CREATE INDEX IF NOT EXISTS idx_predizioni_created ON predizioni(created_at);
CREATE INDEX IF NOT EXISTS idx_predizioni_ip ON predizioni(ip_richiedente);

-- Indici cache
CREATE INDEX IF NOT EXISTS idx_cache_chiave ON cache_predizioni(chiave_cache);
CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache_predizioni(expires_at);

-- Indici utenti
CREATE INDEX IF NOT EXISTS idx_utenti_email ON utenti(email);
CREATE INDEX IF NOT EXISTS idx_utenti_api_key ON utenti(api_key);
CREATE INDEX IF NOT EXISTS idx_utenti_piano ON utenti(piano);

-- Indici API logs
CREATE INDEX IF NOT EXISTS idx_api_logs_utente ON api_logs(utente_id);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_api_logs_timestamp ON api_logs(created_at);

-- ============================================
-- FUNZIONI E TRIGGER
-- ============================================

-- Aggiorna timestamp automatico
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger per auto-update timestamp
CREATE TRIGGER update_squadre_timestamp
    BEFORE UPDATE ON squadre
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_partite_timestamp
    BEFORE UPDATE ON partite  
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER update_utenti_timestamp
    BEFORE UPDATE ON utenti
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- ============================================
-- DATI INIZIALI
-- ============================================

-- Inserisci squadre Serie A 2024-2025
INSERT INTO squadre (nome, nome_completo, citta) VALUES
('Atalanta', 'Atalanta Bergamasca Calcio', 'Bergamo'),
('Bologna', 'Bologna Football Club 1909', 'Bologna'),
('Cagliari', 'Cagliari Calcio', 'Cagliari'),
('Empoli', 'Empoli Football Club', 'Empoli'),
('Fiorentina', 'ACF Fiorentina', 'Firenze'),
('Genoa', 'Genoa Cricket and Football Club', 'Genova'),
('Inter', 'Football Club Internazionale Milano', 'Milano'),
('Juventus', 'Juventus Football Club', 'Torino'),
('Lazio', 'Società Sportiva Lazio', 'Roma'),
('Lecce', 'Unione Sportiva Lecce', 'Lecce'),
('Milan', 'Associazione Calcio Milan', 'Milano'),
('Monza', 'Associazione Calcio Monza', 'Monza'),
('Napoli', 'Società Sportiva Calcio Napoli', 'Napoli'),
('Parma', 'Parma Calcio 1913', 'Parma'),
('Roma', 'Associazione Sportiva Roma', 'Roma'),
('Salernitana', 'Unione Sportiva Salernitana 1919', 'Salerno'),
('Sassuolo', 'Unione Sportiva Sassuolo Calcio', 'Sassuolo'),
('Torino', 'Torino Football Club', 'Torino'),
('Udinese', 'Udinese Calcio', 'Udine'),
('Venezia', 'Venezia Football Club', 'Venezia')
ON CONFLICT (nome) DO NOTHING;

-- Commento finale
-- Schema pronto per migrazione da CSV e features enterprise
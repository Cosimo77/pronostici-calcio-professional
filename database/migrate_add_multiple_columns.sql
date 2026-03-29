-- Migration: Aggiungi colonne per betting multiple
-- Eseguire su database esistente per aggiornare schema

-- 1. Aggiungi colonne per multiple (se non esistono)
DO $$ 
BEGIN
    -- group_id
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='bets' AND column_name='group_id') THEN
        ALTER TABLE bets ADD COLUMN group_id VARCHAR(50);
        RAISE NOTICE 'Aggiunta colonna group_id';
    END IF;
    
    -- bet_number
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='bets' AND column_name='bet_number') THEN
        ALTER TABLE bets ADD COLUMN bet_number INTEGER DEFAULT 1;
        RAISE NOTICE 'Aggiunta colonna bet_number';
    END IF;
    
    -- tipo_bet
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='bets' AND column_name='tipo_bet') THEN
        ALTER TABLE bets ADD COLUMN tipo_bet VARCHAR(20) DEFAULT 'SINGLE';
        RAISE NOTICE 'Aggiunta colonna tipo_bet';
    END IF;
END $$;

-- 2. Aggiungi constraints
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_tipo_bet') THEN
        ALTER TABLE bets ADD CONSTRAINT chk_tipo_bet 
        CHECK (tipo_bet IN ('SINGLE', 'DOUBLE', 'TRIPLE', 'SYSTEM', 'ACCA'));
        RAISE NOTICE 'Aggiunto constraint chk_tipo_bet';
    END IF;
END $$;

-- 3. Aggiungi indici
CREATE INDEX IF NOT EXISTS idx_group_id ON bets(group_id) WHERE group_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_tipo_bet ON bets(tipo_bet);

-- 4. Verifica
SELECT 'Migration completata! Colonne:' as status;
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'bets'
ORDER BY ordinal_position;

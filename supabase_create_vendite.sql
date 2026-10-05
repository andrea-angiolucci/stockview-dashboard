-- Esegui questo SQL nell'editor SQL di Supabase
-- Crea (o ricrea) la tabella vendite con tutte e 47 le colonne

DROP TABLE IF EXISTS vendite CASCADE;

CREATE TABLE vendite (
  id                  BIGSERIAL PRIMARY KEY,
  tipo_operazione     TEXT,          -- ING (ingrosso) o VEN (vendita)
  data                DATE,
  quantita            NUMERIC,
  operatore           TEXT,
  prezzo_vendita      NUMERIC,
  codice_cliente      TEXT,
  addizione           NUMERIC,
  asse                NUMERIC,
  asta                NUMERIC,
  calibro             NUMERIC,
  cilindro            NUMERIC,
  codice              TEXT,
  barcode             TEXT,          -- "Codice a barre"
  codice_filiale      TEXT,
  colore              TEXT,
  costo_medio         NUMERIC,
  data_ult_acquisto   DATE,
  data_ult_vendita    DATE,
  descrizione         TEXT,
  diametro            NUMERIC,
  filiale             TEXT,
  fornitore           TEXT,
  iva                 NUMERIC,
  linea               TEXT,
  magazzino           TEXT,
  marchio             TEXT,
  materiale           TEXT,
  modello             TEXT,
  percentuale_colore  NUMERIC,
  ponte               NUMERIC,
  prezzo_acquisto     NUMERIC,
  prezzo_di_vendita   NUMERIC,
  prezzo_listino      NUMERIC,
  quantita_in_arrivo  NUMERIC,
  quantita_magazzino  NUMERIC,
  rb                  NUMERIC,
  rb2                 NUMERIC,
  sfera               NUMERIC,
  durata              TEXT,
  geometria           TEXT,
  famiglia            TEXT,
  tipo_prodotto       TEXT,
  trattamento         TEXT,
  utente              TEXT,
  fornitore_1         TEXT,
  codice_movimento    TEXT,
  operatore_reg       TEXT,
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Indici per le query più comuni
CREATE INDEX idx_vendite_barcode       ON vendite(barcode);
CREATE INDEX idx_vendite_data          ON vendite(data);
CREATE INDEX idx_vendite_filiale       ON vendite(filiale);
CREATE INDEX idx_vendite_tipo_op       ON vendite(tipo_operazione);
CREATE INDEX idx_vendite_barcode_data  ON vendite(barcode, data);

-- Abilita RLS e accesso anonimo in lettura (stessa policy della tabella attuale)
ALTER TABLE vendite ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read" ON vendite FOR SELECT USING (true);
CREATE POLICY "anon_insert" ON vendite FOR INSERT WITH CHECK (true);

"""
setup_e_importa_vendite.py
==========================
1. Svuota la tabella `vendite` in Supabase (DELETE tutte le righe)
2. Aggiunge la colonna `tipo_operazione` se non esiste già
   (non serve la Management API — usiamo una tabella che già esiste)
3. Importa tutte le righe di Vendita TUTTI MAGAZZINI.xlsx
   con le colonne che Supabase già accetta.

NOTA: La tabella `vendite` deve già esistere in Supabase.
      Se devi ricrearla da zero, esegui prima supabase_create_vendite.sql
      nell'editor SQL di Supabase Dashboard.

Requisiti:
  pip install pandas openpyxl supabase --break-system-packages

Uso:
  python setup_e_importa_vendite.py "C:/percorso/al/file.xlsx"
"""

import sys
import math
import re
import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://exrlurfvydxrqfzjdobp.supabase.co"
SUPABASE_KEY = "sb_publishable_0mNbCOZLSV-ug9iJ9jLrNA_RabyY_LM"

# Mappa nomi colonna Excel → nomi Supabase
COL_MAP = {
    "Tipo operazione": "tipo_operazione",
    "Data": "data",
    "Quantità": "quantita",
    "Operatore": "operatore",
    "Prezzo vendita": "prezzo_vendita",
    "Codice cliente": "codice_cliente",
    "Addizione": "addizione",
    "Asse": "asse",
    "Asta": "asta",
    "Calibro": "calibro",
    "Cilindro": "cilindro",
    "Codice": "codice",
    "Codice a barre": "barcode",
    "Codice filiale": "codice_filiale",
    "Colore": "colore",
    "Costo medio": "costo_medio",
    "Data ult. acquisto": "data_ult_acquisto",
    "Data ult. vendita": "data_ult_vendita",
    "Descrizione": "descrizione",
    "Diametro": "diametro",
    "Filiale": "filiale",
    "Fornitore": "fornitore",
    "IVA": "iva",
    "Linea": "linea",
    "Magazzino": "magazzino",
    "Marchio": "marchio",
    "Materiale": "materiale",
    "Modello": "modello",
    "Percentuale colore": "percentuale_colore",
    "Ponte": "ponte",
    "Prezzo acquisto": "prezzo_acquisto",
    "Prezzo di vendita": "prezzo_di_vendita",
    "Prezzo listino": "prezzo_listino",
    "Quantità in arrivo": "quantita_in_arrivo",
    "Quantità magazzino": "quantita_magazzino",
    "Rb": "rb",
    "Rb2": "rb2",
    "Sfera": "sfera",
    "Durata": "durata",
    "Geometria": "geometria",
    "Famiglia": "famiglia",
    "Tipo prodotto": "tipo_prodotto",
    "Trattamento": "trattamento",
    "Utente": "utente",
    "fornitore_1": "fornitore_1",
    "Codice movimento": "codice_movimento",
    "Operatore reg": "operatore_reg",
}

BATCH_SIZE = 300

def clean_val(v):
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    if hasattr(v, 'isoformat'):
        return v.date().isoformat() if hasattr(v, 'date') else v.isoformat()
    return v

def get_existing_columns(sb):
    """Legge una riga per capire quali colonne esistono già in Supabase."""
    try:
        res = sb.table("vendite").select("*").limit(1).execute()
        # Anche se la tabella è vuota, l'errore 42703 ci dice quale colonna manca
        return None  # non possiamo sapere da qui
    except Exception:
        return None

def main(xlsx_path):
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 1. Leggi il file Excel
    print(f"Lettura file: {xlsx_path}")
    df = pd.read_excel(xlsx_path, dtype=str)
    print(f"  Righe lette: {len(df)}, Colonne: {len(df.columns)}")
    print(f"  Colonne trovate: {list(df.columns)}")

    # 2. Rinomina colonne
    rename = {k: v for k, v in COL_MAP.items() if k in df.columns}
    df = df.rename(columns=rename)
    supabase_cols = list(rename.values())
    df = df[[c for c in supabase_cols if c in df.columns]]
    print(f"  Colonne da importare: {list(df.columns)}")

    # 3. Converti tipi
    for date_col in ["data", "data_ult_acquisto", "data_ult_vendita"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    for num_col in ["quantita", "prezzo_vendita", "prezzo_acquisto", "prezzo_di_vendita",
                    "prezzo_listino", "costo_medio", "quantita_in_arrivo", "quantita_magazzino",
                    "calibro", "ponte", "asta", "addizione", "sfera", "cilindro", "asse",
                    "diametro", "percentuale_colore", "iva", "rb", "rb2"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    # 4. Svuota la tabella esistente
    print("\nSvuoto tabella vendite esistente...")
    try:
        # DELETE tutte le righe — PostgREST richiede un filtro, usiamo id > 0
        sb.table("vendite").delete().gte("id", 0).execute()
        print("  Tabella svuotata.")
    except Exception as e:
        print(f"  Attenzione svuotamento: {e}")
        print("  Continuo comunque con l'inserimento...")

    # 5. Inserimento a batch
    total = len(df)
    inserted = 0
    errors = 0
    first_error = None

    print(f"\nInserimento {total} righe in batch da {BATCH_SIZE}...")
    for start in range(0, total, BATCH_SIZE):
        chunk = df.iloc[start:start + BATCH_SIZE]
        records = []
        for _, row in chunk.iterrows():
            rec = {}
            for col in df.columns:
                rec[col] = clean_val(row.get(col))
            records.append(rec)

        try:
            sb.table("vendite").insert(records).execute()
            inserted += len(records)
            pct = inserted / total * 100
            print(f"  {inserted}/{total} ({pct:.0f}%)  ", end="\r")
        except Exception as e:
            errors += len(records)
            err_str = str(e)
            if first_error is None:
                first_error = err_str
            # Se l'errore è colonna mancante, mostriamo subito
            if "42703" in err_str or "does not exist" in err_str.lower():
                col_match = re.search(r'column "?(\w+)"? of', err_str)
                col_name = col_match.group(1) if col_match else "?"
                print(f"\n  ERRORE: la colonna '{col_name}' non esiste in Supabase.")
                print(f"  Esegui supabase_create_vendite.sql nell'editor SQL di Supabase.")
                print(f"  Errore completo: {err_str}")
                sys.exit(1)
            print(f"\n  ERRORE batch {start}: {err_str[:200]}")

    print(f"\n\nCompletato: {inserted} righe inserite, {errors} errori.")
    if first_error:
        print(f"Primo errore: {first_error[:300]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        path = r"C:\Users\andre\Dropbox\Scambio Dati Paolo\Power BI\Dati\VENDUTO\Vendita TUTTI MAGAZZINI.xlsx"
        print(f"Uso percorso predefinito: {path}")
        main(path)
    else:
        main(sys.argv[1])

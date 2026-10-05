"""
import_vendite.py
Importa Vendita TUTTI MAGAZZINI.xlsx → Supabase tabella `vendite`
con tutte e 47 le colonne originali.

Requisiti:
  pip install pandas openpyxl supabase --break-system-packages

Uso:
  python import_vendite.py "C:/percorso/al/file.xlsx"
"""

import sys
import math
import pandas as pd
from supabase import create_client

SUPABASE_URL = "https://exrlurfvydxrqfzjdobp.supabase.co"
SUPABASE_KEY = "sb_publishable_0mNbCOZLSV-ug9iJ9jLrNA_RabyY_LM"

# Mappa colonne Excel → nomi colonna Supabase (snake_case, senza spazi)
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

BATCH_SIZE = 500

def clean_val(v):
    """Converte NaN/NaT in None, e date in stringa ISO."""
    if v is None:
        return None
    if isinstance(v, float) and math.isnan(v):
        return None
    try:
        # pandas Timestamp
        if hasattr(v, 'isoformat'):
            return v.isoformat()
    except Exception:
        pass
    return v

def main(xlsx_path):
    print(f"Lettura file: {xlsx_path}")
    df = pd.read_excel(xlsx_path, dtype=str)
    print(f"  Righe lette: {len(df)}, Colonne: {len(df.columns)}")

    # Rinomina colonne
    df = df.rename(columns=COL_MAP)
    # Mantieni solo le colonne mappate (scarta colonne non riconosciute)
    keep = [c for c in COL_MAP.values() if c in df.columns]
    df = df[keep]
    print(f"  Colonne mantenute: {len(keep)}")

    # Converti date
    for date_col in ["data", "data_ult_acquisto", "data_ult_vendita"]:
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Converti numerici
    for num_col in ["quantita", "prezzo_vendita", "prezzo_acquisto", "prezzo_di_vendita",
                    "prezzo_listino", "costo_medio", "quantita_in_arrivo", "quantita_magazzino",
                    "calibro", "ponte", "asta", "addizione", "sfera", "cilindro", "asse",
                    "diametro", "percentuale_colore", "iva", "rb", "rb2"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    sb = create_client(SUPABASE_URL, SUPABASE_KEY)

    total = len(df)
    inserted = 0
    errors = 0

    for start in range(0, total, BATCH_SIZE):
        chunk = df.iloc[start:start + BATCH_SIZE]
        records = []
        for _, row in chunk.iterrows():
            rec = {}
            for col in keep:
                rec[col] = clean_val(row.get(col))
            records.append(rec)

        try:
            res = sb.table("vendite").insert(records).execute()
            inserted += len(records)
            pct = inserted / total * 100
            print(f"  Inserite {inserted}/{total} righe ({pct:.1f}%)", end="\r")
        except Exception as e:
            errors += len(records)
            print(f"\n  ERRORE batch {start}-{start+BATCH_SIZE}: {e}")

    print(f"\nImportazione completata: {inserted} righe inserite, {errors} errori.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python import_vendite.py <percorso_file.xlsx>")
        sys.exit(1)
    main(sys.argv[1])

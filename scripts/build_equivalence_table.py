"""
build_equivalence_table.py

Cruza el GeoJSON de polígonos (`fid`, `NOMBRE_DEL`) contra el catálogo oficial
de delegaciones (`No. Delegación`, `Nombre Delegación`) por nombre normalizado,
para producir una tabla de equivalencia `fid -> No. Delegación`.

El cruce se hace en dos pasadas:
  1. Coincidencia EXACTA por nombre normalizado (sin acentos, mayúsculas).
  2. Para lo que no calzó exacto, coincidencia APROXIMADA (difflib) solo
     contra los nombres del catálogo que ningún polígono reclamó todavía.
     Así se evita que un nombre parecido "robe" el match de otro fid que
     sí coincide exacto (p. ej. "YACHIHUALTEPEC" vs "YACHIHUACALTEPEC").

Cualquier fila que no quede en "exacto" se marca para revisión manual.

Uso:
    cd scripts/
    python build_equivalence_table.py

Lee:
    data/raw/POLIGONOS_DELEGACIONES_UNIFICADO.geojson
    data/raw/Delegaciones_Subdelegaciones_Toluca.xlsx

Escribe:
    data/processed/equivalencia_fid_delegacion.csv
"""

import difflib
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
GEOJSON_PATH = BASE / "data/raw/POLIGONOS_DELEGACIONES_UNIFICADO.geojson"
XLSX_PATH = BASE / "data/raw/Delegaciones_Subdelegaciones_Toluca.xlsx"
OUT_PATH = BASE / "data/processed/equivalencia_fid_delegacion.csv"

FUZZY_CUTOFF = 0.6  # mínimo de similitud (0-1) para aceptar un match aproximado


def normalize(name: str) -> str:
    """Mayúsculas, sin acentos, sin símbolos ni espacios repetidos."""
    name = unicodedata.normalize("NFKD", str(name))
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[^A-Za-z0-9 ]", " ", name)
    name = re.sub(r"\s+", " ", name).strip().upper()
    return name


def load_geojson(path: Path) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rows = [
        {"fid": feat["properties"]["fid"], "nombre_geojson": feat["properties"]["NOMBRE_DEL"]}
        for feat in data["features"]
    ]
    return pd.DataFrame(rows)


def load_catalogo(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    cat = (
        df[["No. Delegación", "Nombre Delegación"]]
        .drop_duplicates()
        .rename(columns={"No. Delegación": "no_delegacion", "Nombre Delegación": "nombre_excel"})
        .sort_values("no_delegacion")
        .reset_index(drop=True)
    )
    return cat


def match(geo_df: pd.DataFrame, cat_df: pd.DataFrame) -> pd.DataFrame:
    geo_df = geo_df.copy()
    cat_df = cat_df.copy()
    geo_df["norm"] = geo_df["nombre_geojson"].apply(normalize)
    cat_df["norm"] = cat_df["nombre_excel"].apply(normalize)

    norm_to_no = dict(zip(cat_df["norm"], cat_df["no_delegacion"]))
    no_to_nombre = dict(zip(cat_df["no_delegacion"], cat_df["nombre_excel"]))

    used_norms = set()
    fid_to_no = {}

    # --- Pasada 1: coincidencias exactas ---
    for _, row in geo_df.iterrows():
        norm = row["norm"]
        if norm in norm_to_no:
            fid_to_no[row["fid"]] = ("exacto", norm_to_no[norm], 1.0)
            used_norms.add(norm)

    # --- Pasada 2: coincidencias aproximadas, solo contra lo que sobró ---
    pendientes = [n for n in norm_to_no if n not in used_norms]
    for _, row in geo_df.iterrows():
        if row["fid"] in fid_to_no:
            continue
        norm = row["norm"]
        disponibles = [n for n in pendientes if n not in used_norms]
        cercanos = difflib.get_close_matches(norm, disponibles, n=1, cutoff=FUZZY_CUTOFF)
        if cercanos:
            mejor = cercanos[0]
            ratio = difflib.SequenceMatcher(None, norm, mejor).ratio()
            fid_to_no[row["fid"]] = ("aproximado — revisar", norm_to_no[mejor], round(ratio, 2))
            used_norms.add(mejor)
        else:
            fid_to_no[row["fid"]] = ("sin coincidencia — revisar", None, 0.0)

    # --- Armar tabla de salida ---
    filas = []
    for _, row in geo_df.iterrows():
        tipo, no_deleg, confianza = fid_to_no[row["fid"]]
        filas.append({
            "fid": row["fid"],
            "nombre_geojson": row["nombre_geojson"],
            "no_delegacion_sugerido": no_deleg,
            "nombre_excel": no_to_nombre.get(no_deleg),
            "tipo_match": tipo,
            "confianza": confianza,
        })

    # Delegaciones del catálogo que ningún polígono reclamó (no tienen geometría)
    for norm in norm_to_no:
        if norm not in used_norms:
            no_deleg = norm_to_no[norm]
            filas.append({
                "fid": None,
                "nombre_geojson": None,
                "no_delegacion_sugerido": no_deleg,
                "nombre_excel": no_to_nombre[no_deleg],
                "tipo_match": "delegación sin polígono en el geojson",
                "confianza": 0.0,
            })

    out = pd.DataFrame(filas)
    out["__orden"] = out["fid"].fillna(out["no_delegacion_sugerido"])
    out = out.sort_values("__orden").drop(columns="__orden").reset_index(drop=True)
    return out


def main():
    geo_df = load_geojson(GEOJSON_PATH)
    cat_df = load_catalogo(XLSX_PATH)
    tabla = match(geo_df, cat_df)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(OUT_PATH, index=False, encoding="utf-8")

    exactos = (tabla["tipo_match"] == "exacto").sum()
    revisar = len(tabla) - exactos
    print(f"Tabla de equivalencia escrita en: {OUT_PATH}")
    print(f"  {exactos} coincidencias exactas")
    print(f"  {revisar} filas que requieren revisión manual")


if __name__ == "__main__":
    main()

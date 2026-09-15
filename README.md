# Delegaciones y Subdelegaciones de Toluca 🗺️

Mapa interactivo y repositorio de datos abiertos sobre la división territorial del municipio de Toluca: 48 delegaciones, sus subdelegaciones y unidades territoriales básicas, con planos oficiales y polígonos geográficos.

**🔗 Ver el mapa interactivo:** publícalo con GitHub Pages desde `/docs` (ver sección [Publicar con GitHub Pages](#publicar-con-github-pages)) y pega aquí el enlace, por ejemplo `https://tu-usuario.github.io/toluca-delegaciones-subdelegaciones/`.

> 🚧 **Aviso de actualización** — Este repositorio está en construcción activa. Próximamente se incorporarán: capa de **manzanas**, **gasto público y proyectos** por delegación, y el **directorio de representantes** vecinales. Ver el detalle en [Próximas actualizaciones](#-próximas-actualizaciones).

---

## Estructura del repositorio

```
toluca-delegaciones-subdelegaciones/
├── README.md
├── CHANGELOG.md
│
├── data/
│   ├── raw/                                    # Archivos fuente, sin modificar
│   │   ├── POLIGONOS_DELEGACIONES_UNIFICADO.geojson
│   │   └── Delegaciones_Subdelegaciones_Toluca.xlsx
│   └── processed/                              # Derivados, listos para usar en código
│       ├── delegaciones_subdelegaciones.csv
│       └── equivalencia_fid_delegacion.csv     # fid (geojson) ↔ No. Delegación (xlsx)
│
├── scripts/
│   ├── requirements.txt
│   └── build_equivalence_table.py              # genera el csv de equivalencia anterior
│
├── planos/                                     # Plano oficial de cada delegación (imagen)
│   ├── README.md                               # Convención de nombres + checklist de avance
│   └── 01_centro-historico.jpg
│
└── docs/                                       # Sitio publicado (GitHub Pages)
    └── index.html                              # Mapa interactivo (Leaflet)
```

**Por qué esta organización:**
- `data/raw` conserva los archivos exactamente como llegan de la fuente oficial — nunca se editan a mano, para poder rastrear cualquier corrección.
- `data/processed` guarda versiones derivadas (como el `.csv`) que sí pueden regenerarse desde `raw` cuando haga falta.
- `planos/` concentra las imágenes de los planos oficiales, una por delegación, con nombre predecible para poder enlazarlas por código desde el mapa.
- `docs/` es la carpeta que GitHub Pages puede publicar directamente sin configuración adicional.

---

## Diccionario de datos

Archivo: `data/raw/Delegaciones_Subdelegaciones_Toluca.xlsx` (280 filas)

| Columna | Descripción |
|---|---|
| `No. Delegación` | Número oficial de la delegación (1–48) |
| `Nombre Delegación` | Nombre oficial de la delegación |
| `Tipo` | `Delegación` o `Subdelegación` |
| `No. Subdelegación` | Número y nombre corto de la subdelegación (solo aplica a delegaciones con subdelegaciones) |
| `Nombre Subdelegación` | Nombre de la colonia/localidad dentro de la subdelegación |
| `Unidad Territorial Básica` | Nombre de la unidad territorial (barrio/colonia) |
| `Clave Única Municipal` | Clave alfanumérica de la unidad territorial, p. ej. `010A` |

Archivo: `data/raw/POLIGONOS_DELEGACIONES_UNIFICADO.geojson`

| Propiedad | Descripción |
|---|---|
| `fid` | Identificador interno del polígono |
| `Delegacion` | Número de delegación (ver nota ⚠️ abajo) |
| `NOMBRE_DEL` | Nombre de la delegación en mayúsculas |

---

## ⚠️ Nota sobre consistencia de IDs

Al comparar el `.geojson` contra el `.xlsx` se detectaron diferencias que conviene resolver **antes** de enlazar ambos archivos por número. Ya se generó el cruce automático — ver [Tabla de equivalencia `fid` ↔ delegación](#tabla-de-equivalencia-fid--delegación) abajo — y quedaron **3 casos que requieren revisión manual**:

1. **`fid 7`** del geojson ("San Marcos Yachihualtepec") no corresponde a ninguna delegación del catálogo — el número 7 oficial es "Universidad", que no tiene polígono propio.
2. **`fid 24` y `fid 25`** del geojson ("San Andrés Cuecoxtitlán" y "San Andrés Cuexcotitlán") son casi idénticos entre sí, pero el catálogo solo tiene **una** delegación con ese nombre (la 25, "San Andrés Cuexcontitlán"); la 24 real ("Capultitlán") no tiene polígono. No es posible saber, solo con el nombre, cuál de los dos polígonos es el correcto sin revisar el plano oficial de cada uno.
3. **Delegaciones sin polígono en el geojson:** Capultitlán (24) y Sauces (48) — faltan por completo.

El resto (45 de 48) ya quedó resuelto: 35 coincidencias exactas y 10 aproximadas (typos/acentos) con confianza ≥ 0.75, todas correctas tras revisión.

### Tabla de equivalencia `fid` ↔ delegación

Generada por [`scripts/build_equivalence_table.py`](scripts/build_equivalence_table.py), que cruza ambos archivos por nombre normalizado (sin acentos, mayúsculas) en dos pasadas: primero coincidencias exactas, luego aproximadas solo contra lo que sobró, para que un nombre parecido no "robe" el match de otro que sí coincide exacto.

```bash
cd scripts
pip install -r requirements.txt
python build_equivalence_table.py
```

Esto regenera [`data/processed/equivalencia_fid_delegacion.csv`](data/processed/equivalencia_fid_delegacion.csv) con columnas `fid`, `nombre_geojson`, `no_delegacion_sugerido`, `nombre_excel`, `tipo_match` y `confianza`. Úsala como tabla puente al cargar capas nuevas (manzanas, gasto, representantes) para no etiquetar la delegación equivocada.

**Recomendación:** mientras no se resuelvan los 3 casos pendientes con el plano oficial de cada delegación, no usar `fid` como llave definitiva — usar `no_delegacion_sugerido` de esta tabla, y dejar en `null` lo que siga en revisión.

---

## Planos oficiales

Cada delegación tiene un plano oficial (formato del Ayuntamiento de Toluca) con sus unidades territoriales, criterios de delimitación y simbología. Se guardan en `planos/` con el nombre `NN_nombre-delegacion.jpg` (dos dígitos + nombre en minúsculas sin acentos).

Por ahora solo está disponible:
- ✅ `01_centro-historico.jpg`

El resto se irá agregando — ver el checklist completo en [`planos/README.md`](planos/README.md).

---

## Publicar con GitHub Pages

1. Sube este repositorio a GitHub.
2. Ve a **Settings → Pages**.
3. En **Source**, elige la rama `main` y la carpeta `/docs`.
4. Guarda — GitHub publicará `docs/index.html` como sitio web en uno o dos minutos.

---

## 🚧 Próximas actualizaciones

| Mejora planeada | Estado |
|---|---|
| Corregir y completar el `.geojson` (48 polígonos, IDs consistentes) | Pendiente |
| Capa de **manzanas** dentro de cada unidad territorial | Pendiente |
| Datos de **gasto público y proyectos** por delegación | Pendiente |
| **Directorio de representantes** (delegados/subdelegados) por demarcación | Pendiente |
| Plano oficial de las 47 delegaciones restantes | En progreso |

Las actualizaciones de esta lista se registran con más detalle en [`CHANGELOG.md`](CHANGELOG.md).

---

## Créditos y fuentes de datos

La información geográfica, los nombres oficiales de las delegaciones/subdelegaciones y los planos utilizados en este repositorio fueron obtenidos del portal oficial del Municipio de Toluca.

### Referencia en formato APA 7
Ayuntamiento de Toluca. (2026). *Delegaciones de Toluca*. Portal Oficial del Ayuntamiento de Toluca. https://toluca.gob.mx

- Cita en texto (parentética): (Ayuntamiento de Toluca, 2026)
- Cita en texto (narrativa): Según el Ayuntamiento de Toluca (2026)...

## Licencia

Pendiente de elegir. Si los datos son de carácter público/abierto, opciones comunes son [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es) para los datos y planos, y [MIT](https://opensource.org/license/mit/) para el código del visor.

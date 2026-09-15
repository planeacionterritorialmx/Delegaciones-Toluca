# Changelog

Registro de cambios del proyecto. Formato: fecha, qué cambió.

## [Sin publicar] — Roadmap

Mejoras planeadas, en orden tentativo:

- [x] **Tabla de equivalencia `fid` ↔ delegación** — cruce automático por nombre normalizado (`scripts/build_equivalence_table.py`). Quedan 3 casos puntuales por resolver a mano (ver README).
- [ ] **Corrección del GeoJSON** — completar los polígonos faltantes (Capultitlán, Sauces) y resolver la ambigüedad entre los polígonos `fid 24`/`fid 25`.
- [ ] **Capa de manzanas** — agregar el polígono de cada manzana dentro de su unidad territorial, ligado a la `Clave Única Municipal`.
- [ ] **Gasto público y proyectos** — incorporar, por delegación, los proyectos de obra/inversión y su presupuesto asociado, con fuente y fecha de corte.
- [ ] **Directorio de representantes** — nombre y contacto del delegado/subdelegado vigente por demarcación.
- [ ] **Planos restantes** — subir el plano oficial de las 47 delegaciones que faltan (ver checklist en `planos/README.md`).

## 2026-06-19 — Versión inicial

- Primera versión del mapa interactivo (Leaflet) con los 47 polígonos de delegaciones disponibles.
- Carga de datos oficiales: `Delegaciones_Subdelegaciones_Toluca.xlsx` (280 registros) y `POLIGONOS_DELEGACIONES_UNIFICADO.geojson`.
- Primer plano oficial incorporado: Centro Histórico (delegación 01).
- Aviso de actualización agregado al visor y documentado en este changelog.

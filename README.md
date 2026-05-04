# Report Ensambler

Repositorio reorganizado para generar reportes PDF reproducibles a partir de plantillas TOML.

## Estructura

```text
src/report_ensambler/   Paquete Python principal
configs/                Plantillas TOML de charts, notes, reports y tables
assets/                 Logo y estilos auxiliares
tests/                  Tests de generación de plots y PDFs
examples/               Script de generación de reportes de ejemplo
docs/                   Notas técnicas del refactor
```

## Uso rápido

```bash
python -m pip install -e .[test]
python examples/generate_example_reports.py --output-dir examples/output
pytest
```

Los PDFs de ejemplo se generan en `examples/output/pdf`. Se crea un PDF por cada plantilla/configuración de reporte encontrada en `configs/reports`.

## Cambios de enfoque

- Se reemplazaron imports rígidos a `libs.*` por un paquete instalable (`src/report_ensambler`).
- Las plantillas TOML se conservan y se cargan con `tomllib` estándar de Python 3.11+.
- Las dimensiones de filas/columnas ahora se normalizan al tamaño útil de la página para evitar overflow.
- La generación de ejemplos es determinista: usa datos sintéticos con semilla fija.
- Los tests validan que cada plantilla produzca un PDF legible de una página.

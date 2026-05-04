from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import tomli

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PACKAGE_ROOT / "configs"
ASSETS_DIR = PACKAGE_ROOT / "assets"
REPORT_CONFIG_DIR = CONFIG_DIR / "reports"
CHART_CONFIG_DIR = CONFIG_DIR / "charts"
TABLE_CONFIG_DIR = CONFIG_DIR / "tables"
NOTE_CONFIG_DIR = CONFIG_DIR / "notes"


@lru_cache(maxsize=128)
def load_toml(path_or_dir: str | Path, name: str | None = None) -> dict:
    """Carga un archivo TOML.

    Puede usarse como ``load_toml(path)`` o ``load_toml(directory, name)``. En el
    segundo caso ``name`` se recibe sin extensión.
    """
    path = Path(path_or_dir)
    if name is not None:
        path = path / f"{name}.toml"
    if path.suffix != ".toml":
        path = path.with_suffix(".toml")
    with path.open("rb") as fh:
        return tomli.load(fh)


def list_report_templates() -> list[str]:
    """Devuelve las plantillas de reporte disponibles, sin extensión."""
    return sorted(path.stem for path in REPORT_CONFIG_DIR.glob("*.toml"))

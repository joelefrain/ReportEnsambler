from __future__ import annotations

from reportlab.lib import colors


def parse_color(value):
    """Convierte strings TOML en colores de ReportLab."""
    if value is None or value == "None":
        return None
    if hasattr(value, "red"):
        return value
    if isinstance(value, str):
        value = value.strip()
        if value.startswith("#"):
            return colors.HexColor(value)
        named = getattr(colors, value, None)
        if named is not None:
            return named
    return value

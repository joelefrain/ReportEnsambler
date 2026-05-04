"""Report Ensambler: generación reproducible de reportes PDF basados en TOML."""

from .config import list_report_templates, load_toml
from .report import ReportBuilder, ReportMetadata
from .plotting import create_example_plot

__all__ = [
    "ReportBuilder",
    "ReportMetadata",
    "create_example_plot",
    "list_report_templates",
    "load_toml",
]

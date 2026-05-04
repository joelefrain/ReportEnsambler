from __future__ import annotations

from pathlib import Path

from .config import list_report_templates
from .plotting import save_example_plot
from .report import ReportBuilder, ReportMetadata


def generate_all_examples(output_dir: str | Path) -> list[Path]:
    """Genera un PDF de ejemplo por cada plantilla TOML disponible."""
    output = Path(output_dir)
    charts_dir = output / "plots"
    pdf_dir = output / "pdf"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for idx, template in enumerate(list_report_templates(), start=1):
        chart_path = save_example_plot(
            charts_dir / f"{template}.png",
            seed=100 + idx,
            title=f"Synthetic monitoring plot - {template}",
        )
        metadata = ReportMetadata(
            project_code=f"SYN-{idx:03d}",
            project_name=f"Synthetic validation for {template}",
            doc_title="Synthetic example report",
            chart_title=f"Template test: {template}",
            num_item=f"{idx:02d}",
        )
        pdf_path = pdf_dir / f"{template}.pdf"
        ReportBuilder(template).build_pdf(
            pdf_path, chart_path=chart_path, metadata=metadata
        )
        paths.append(pdf_path)
    return paths


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera reportes PDF de ejemplo para todas las plantillas."
    )
    parser.add_argument(
        "--output-dir", default="examples/output", help="Directorio de salida"
    )
    args = parser.parse_args()
    paths = generate_all_examples(args.output_dir)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table, TableStyle
from svglib.svglib import svg2rlg

from .colors import parse_color
from .config import ASSETS_DIR, REPORT_CONFIG_DIR, load_toml

_ALIGNMENT = {
    "LEFT": TA_LEFT,
    "CENTER": TA_CENTER,
    "RIGHT": TA_RIGHT,
    "JUSTIFY": TA_JUSTIFY,
}


@dataclass(slots=True)
class ReportMetadata:
    project_code: str = "SYN-001"
    company_name: str = "Anddes Asociados"
    project_name: str = "Synthetic data validation project"
    date: str = "2026-05-03"
    revision: str = "A"
    elaborated_by: str = "QA Bot"
    approved_by: str = "Technical Reviewer"
    doc_title: str = "Synthetic example report"
    chart_title: str = "Synthetic monitoring plot"
    num_item: str = "01"
    upper_cell: str = ""
    lower_cell: str = ""


class ReportBuilder:
    """Genera un PDF con una plantilla TOML de ``configs/reports``.

    La plantilla define grilla, spans, estilos y posiciones semánticas. El código
    normaliza anchos y altos al tamaño real de página para evitar desbordes.
    """

    def __init__(
        self,
        template: str,
        *,
        theme_color: str = "#1F4E79",
        theme_color_font: str = "white",
    ) -> None:
        self.template = template.removesuffix(".toml")
        self.config = load_toml(REPORT_CONFIG_DIR, self.template)
        self.theme_color = parse_color(theme_color)
        self.theme_color_font = parse_color(theme_color_font)
        self.rows = len(self.config["table"]["color"])
        self.cols = len(self.config["table"]["color"][0])

    def build_pdf(
        self,
        output_path: str | Path,
        *,
        chart_path: str | Path | None = None,
        metadata: ReportMetadata | None = None,
    ) -> Path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        metadata = metadata or ReportMetadata()

        page_size = self._page_size()
        margins = float(self.config.get("page", {}).get("margins", 25))
        doc = SimpleDocTemplate(
            str(output),
            pagesize=page_size,
            leftMargin=margins,
            rightMargin=margins,
            topMargin=margins,
            bottomMargin=margins,
        )
        content_width = page_size[0] - 2 * margins - 8
        content_height = page_size[1] - 2 * margins - 18
        col_widths = self._scaled(self.config["column_widths"]["values"], content_width)
        row_heights = self._scaled(self.config["row_heights"]["values"], content_height)

        data = self._table_data(metadata, chart_path, col_widths, row_heights)
        table = Table(data, colWidths=col_widths, rowHeights=row_heights, repeatRows=0)
        table.setStyle(TableStyle(self._table_styles()))
        doc.build([table])
        return output

    def _page_size(self) -> tuple[float, float]:
        page = self.config.get("page", {})
        size_name = page.get("size", "A4")
        if size_name != "A4":
            raise ValueError(f"Unsupported page size: {size_name}")
        orientation = page.get("orientation", "portrait")
        return landscape(A4) if orientation == "landscape" else portrait(A4)

    @staticmethod
    def _scaled(values: list[float], target: float) -> list[float]:
        total = float(sum(values))
        if total <= 0:
            raise ValueError("Dimension values must sum to a positive number")
        return [float(value) * target / total for value in values]

    def _table_data(
        self,
        metadata: ReportMetadata,
        chart_path: str | Path | None,
        col_widths: list[float],
        row_heights: list[float],
    ) -> list[list[Any]]:
        data: list[list[Any]] = [
            ["" for _ in range(self.cols)] for _ in range(self.rows)
        ]
        values = asdict(metadata)
        values["chart_cell"] = self._chart_flowable(chart_path, col_widths, row_heights)
        values["logo_cell"] = self._logo_flowable(col_widths, row_heights)

        for key, position in self.config.get("cell_positions", {}).items():
            row, col = position
            raw = values.get(key, "")
            data[row][col] = self._wrap(raw, row, col)

        for key, position in self.config.get("texts_positions", {}).items():
            row, col = position
            text = self.config.get("texts", {}).get(key, "")
            data[row][col] = self._wrap(text, row, col)
        return data

    def _wrap(self, value: Any, row: int, col: int) -> Any:
        if not isinstance(value, str):
            return value
        style = ParagraphStyle(
            name=f"cell_{row}_{col}",
            alignment=_ALIGNMENT.get(self.config["table"]["align"][row][col], TA_LEFT),
            fontName=self.config["table"]["font_name"][row][col],
            fontSize=float(self.config["table"]["font_size"][row][col]),
            leading=max(float(self.config["table"]["font_size"][row][col]) * 1.12, 7),
            textColor=self._color_value("font_color", row, col),
        )
        return Paragraph(value.replace("\n", "<br/>"), style)

    def _chart_flowable(
        self,
        chart_path: str | Path | None,
        col_widths: list[float],
        row_heights: list[float],
    ) -> Any:
        if chart_path is None:
            return ""
        row, col = self.config["cell_positions"].get("chart_cell", [0, 0])
        width, height = self._span_dimensions(row, col, col_widths, row_heights)
        image = Image(str(chart_path))
        max_w = max(width - 8, 10)
        max_h = max(height - 8, 10)
        scale = min(max_w / image.imageWidth, max_h / image.imageHeight)
        image.drawWidth = image.imageWidth * scale
        image.drawHeight = image.imageHeight * scale
        return image

    def _logo_flowable(self, col_widths: list[float], row_heights: list[float]) -> Any:
        svg = ASSETS_DIR / "logo" / "logo_main_109x50.svg"
        if not svg.exists():
            return "ANDDES"
        row, col = self.config["cell_positions"].get("logo_cell", [0, 0])
        width, height = self._span_dimensions(row, col, col_widths, row_heights)
        drawing = svg2rlg(str(svg))
        if drawing is None:
            return "ANDDES"
        scale = min(
            max((width - 6) / drawing.width, 0.01),
            max((height - 6) / drawing.height, 0.01),
        )
        drawing.width *= scale
        drawing.height *= scale
        drawing.scale(scale, scale)
        return drawing

    def _span_dimensions(
        self, row: int, col: int, col_widths: list[float], row_heights: list[float]
    ) -> tuple[float, float]:
        for span in self.config.get("spans", {}).get("values", []):
            if span["start"] == [row, col]:
                end_row, end_col = span["end"]
                return sum(col_widths[col : end_col + 1]), sum(
                    row_heights[row : end_row + 1]
                )
        return col_widths[col], row_heights[row]

    def _table_styles(self) -> list[tuple]:
        styles: list[tuple] = []
        for span in self.config.get("spans", {}).get("values", []):
            sr, sc = span["start"]
            er, ec = span["end"]
            styles.append(("SPAN", (sc, sr), (ec, er)))

        table = self.config["table"]
        for row in range(self.rows):
            for col in range(self.cols):
                cell = (col, row)
                styles.extend(
                    [
                        (
                            "BACKGROUND",
                            cell,
                            cell,
                            self._color_value("color", row, col),
                        ),
                        (
                            "TEXTCOLOR",
                            cell,
                            cell,
                            self._color_value("font_color", row, col),
                        ),
                        ("FONTNAME", cell, cell, table["font_name"][row][col]),
                        ("FONTSIZE", cell, cell, float(table["font_size"][row][col])),
                        ("ALIGN", cell, cell, table["align"][row][col]),
                        ("VALIGN", cell, cell, table["valign"][row][col]),
                        (
                            "LEFTPADDING",
                            cell,
                            cell,
                            float(table["padding_left"][row][col]),
                        ),
                        (
                            "RIGHTPADDING",
                            cell,
                            cell,
                            float(table["padding_right"][row][col]),
                        ),
                        (
                            "TOPPADDING",
                            cell,
                            cell,
                            float(table["padding_top"][row][col]),
                        ),
                        (
                            "BOTTOMPADDING",
                            cell,
                            cell,
                            float(table["padding_bottom"][row][col]),
                        ),
                        (
                            "GRID",
                            cell,
                            cell,
                            float(table["size_border"][row][col]),
                            self._color_value("color_border", row, col),
                        ),
                    ]
                )
        border = self.config.get("border", {})
        styles.append(
            (
                "OUTLINE",
                (0, 0),
                (-1, -1),
                float(border.get("size", 1)),
                parse_color(border.get("style", "black")),
            )
        )
        return styles

    def _color_value(self, key: str, row: int, col: int):
        value = self.config["table"][key][row][col]
        if value == "theme_color":
            return self.theme_color
        if value == "theme_color_font":
            return self.theme_color_font
        return parse_color(value)

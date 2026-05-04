from pathlib import Path

from pypdf import PdfReader

from report_ensambler.config import list_report_templates
from report_ensambler.examples import generate_all_examples
from report_ensambler.plotting import save_example_plot


def test_plot_example_is_created(tmp_path: Path):
    path = save_example_plot(tmp_path / "plot.png", seed=7)
    assert path.exists()
    assert path.stat().st_size > 5_000


def test_pdf_is_generated_for_each_report_template(tmp_path: Path):
    pdfs = generate_all_examples(tmp_path)
    assert len(pdfs) == len(list_report_templates())
    assert len(pdfs) >= 8
    for pdf in pdfs:
        assert pdf.exists(), pdf
        assert pdf.stat().st_size > 10_000, pdf
        reader = PdfReader(str(pdf))
        assert len(reader.pages) == 1
        text = reader.pages[0].extract_text() or ""
        assert "Synthetic" in text

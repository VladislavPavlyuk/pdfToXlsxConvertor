import argparse
from pathlib import Path

from converter.services.conversion import (
    PandasXlsxWriter,
    PdfToXlsxConverter,
    TabulaTableExtractor,
    UniquePathNamer,
)


def convert_pdf_to_xlsx(pdf_path: Path, output_dir: Path) -> Path:
    converter = PdfToXlsxConverter(
        extractor=TabulaTableExtractor(),
        writer=PandasXlsxWriter(),
        namer=UniquePathNamer(),
    )
    return converter.convert(pdf_path, output_dir)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert PDF tables to XLSX.")
    parser.add_argument(
        "inputs",
        nargs="+",
        help="PDF files or directories containing PDF files.",
    )
    parser.add_argument(
        "--output-dir",
        default="output_xlsx",
        help="Directory to write XLSX files into.",
    )
    return parser.parse_args()


def iter_pdfs(inputs: list[str]) -> list[Path]:
    pdfs: list[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            pdfs.extend(sorted(path.glob("*.pdf")))
        elif path.is_file() and path.suffix.lower() == ".pdf":
            pdfs.append(path)
    return pdfs


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    pdfs = iter_pdfs(args.inputs)
    if not pdfs:
        raise SystemExit("No PDF files found in provided inputs.")

    for pdf in pdfs:
        try:
            output_path = convert_pdf_to_xlsx(pdf, output_dir)
            print(f"Saved: {output_path}")
        except Exception as exc:
            print(f"Failed: {pdf} ({exc})")


if __name__ == "__main__":
    main()

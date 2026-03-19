from __future__ import annotations

import locale
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Protocol

import pandas as pd
import tabula


class TableExtractor(Protocol):
    def extract_tables(self, pdf_path: Path) -> list[pd.DataFrame]:
        raise NotImplementedError


class TabulaTableExtractor:
    def __init__(self, encoding: str | None = None) -> None:
        self._encoding = encoding or (locale.getpreferredencoding(False) or "utf-8")

    def extract_tables(self, pdf_path: Path) -> list[pd.DataFrame]:
        return tabula.read_pdf(
            str(pdf_path),
            pages="all",
            multiple_tables=True,
            encoding=self._encoding,
            java_options=[f"-Dfile.encoding={self._encoding}"],
            force_subprocess=True,
        )


class XlsxWriter(Protocol):
    def write_tables(self, tables: Iterable[pd.DataFrame], output_path: Path) -> None:
        raise NotImplementedError


class PandasXlsxWriter:
    def write_tables(self, tables: Iterable[pd.DataFrame], output_path: Path) -> None:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for idx, table in enumerate(tables, start=1):
                table.to_excel(writer, sheet_name=f"table_{idx}", index=False)


class OutputNamer(Protocol):
    def unique_path(self, dir_path: Path, filename: str) -> Path:
        raise NotImplementedError


class UniquePathNamer:
    def unique_path(self, dir_path: Path, filename: str) -> Path:
        candidate = dir_path / filename
        if not candidate.exists():
            return candidate
        stem = candidate.stem
        suffix = candidate.suffix
        counter = 1
        while True:
            candidate = dir_path / f"{stem}_{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1


@dataclass(frozen=True)
class PdfToXlsxConverter:
    extractor: TableExtractor
    writer: XlsxWriter
    namer: OutputNamer

    def convert(self, pdf_path: Path, output_dir: Path) -> Path:
        tables = self.extractor.extract_tables(pdf_path)
        if not tables:
            raise ValueError(f"No tables found in {pdf_path}")

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.namer.unique_path(output_dir, f"{pdf_path.stem}.xlsx")
        self.writer.write_tables(tables, output_path)
        return output_path

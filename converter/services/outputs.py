from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class OutputFileService:
    outputs_dir: Path
    base_dir: Path

    def resolve_destination(self, dest: str) -> Path:
        dest_path = Path(dest)
        if not dest_path.is_absolute():
            dest_path = self.base_dir / dest_path
        return dest_path

    def copy_to(self, names: Iterable[str], dest: str) -> list[dict[str, str]]:
        dest_path = self.resolve_destination(dest)
        dest_path.mkdir(parents=True, exist_ok=True)
        results: list[dict[str, str]] = []
        for name in names:
            source = self.outputs_dir / name
            if not source.is_file():
                results.append({"name": name, "error": "File not found."})
                continue
            try:
                shutil.copy2(source, dest_path / name)
                results.append({"name": name, "status": "copied"})
            except Exception as exc:
                results.append({"name": name, "error": str(exc)})
        return results

    def move_to(self, names: Iterable[str], dest: str) -> list[dict[str, str]]:
        dest_path = self.resolve_destination(dest)
        dest_path.mkdir(parents=True, exist_ok=True)
        results: list[dict[str, str]] = []
        for name in names:
            source = self.outputs_dir / name
            if not source.is_file():
                results.append({"name": name, "error": "File not found."})
                continue
            try:
                shutil.move(str(source), str(dest_path / name))
                results.append({"name": name, "status": "moved"})
            except Exception as exc:
                results.append({"name": name, "error": str(exc)})
        return results

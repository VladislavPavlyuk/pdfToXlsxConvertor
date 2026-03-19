from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from django.core.files.storage import FileSystemStorage


@dataclass(frozen=True)
class FileListItem:
    name: str
    size: int
    url: str | None = None


@dataclass
class FileStorageService:
    root_dir: Path
    storage: FileSystemStorage | None = None

    def __post_init__(self) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        if self.storage is None:
            self.storage = FileSystemStorage(location=str(self.root_dir))

    def save_files(self, files: Iterable) -> list[str]:
        saved: list[str] = []
        for file_obj in files:
            stored_name = self.storage.save(file_obj.name, file_obj)
            saved.append(stored_name)
        return saved

    def list_files(self, url_prefix: str | None = None) -> list[FileListItem]:
        items: list[FileListItem] = []
        for path in sorted(self.root_dir.iterdir()):
            if not path.is_file():
                continue
            url = f"{url_prefix}{path.name}" if url_prefix else None
            items.append(FileListItem(name=path.name, size=path.stat().st_size, url=url))
        return items

    def delete_files(self, names: Iterable[str]) -> tuple[list[str], list[str]]:
        deleted: list[str] = []
        skipped: list[str] = []
        for name in names:
            target = self.root_dir / name
            try:
                if target.is_file():
                    target.unlink()
                    deleted.append(name)
                else:
                    skipped.append(name)
            except OSError:
                skipped.append(name)
        return deleted, skipped

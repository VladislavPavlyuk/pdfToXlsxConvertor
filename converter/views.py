from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .services.conversion import (
    PandasXlsxWriter,
    PdfToXlsxConverter,
    TabulaTableExtractor,
    UniquePathNamer,
)
from .services.outputs import OutputFileService
from .services.storage import FileStorageService


@dataclass(frozen=True)
class ServiceContainer:
    converter: PdfToXlsxConverter
    uploads: FileStorageService
    outputs: FileStorageService
    output_files: OutputFileService


_services: ServiceContainer | None = None


def _get_services() -> ServiceContainer:
    global _services
    if _services is None:
        uploads_dir = Path(settings.MEDIA_ROOT) / "uploads"
        outputs_dir = Path(settings.MEDIA_ROOT) / "outputs"
        _services = ServiceContainer(
            converter=PdfToXlsxConverter(
                extractor=TabulaTableExtractor(),
                writer=PandasXlsxWriter(),
                namer=UniquePathNamer(),
            ),
            uploads=FileStorageService(root_dir=uploads_dir),
            outputs=FileStorageService(root_dir=outputs_dir),
            output_files=OutputFileService(
                outputs_dir=outputs_dir,
                base_dir=Path(settings.BASE_DIR),
            ),
        )
    return _services


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "converter/index.html")


def convert_files(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    files = request.FILES.getlist("pdf_files")
    if not files:
        return JsonResponse({"error": "No files uploaded."}, status=400)

    services = _get_services()
    results: list[dict[str, str]] = []
    for pdf_file in files:
        stored_name = services.uploads.save_files([pdf_file])[0]
        stored_path = services.uploads.root_dir / stored_name
        try:
            output_path = services.converter.convert(
                stored_path, services.outputs.root_dir
            )
            results.append(
                {
                    "name": stored_path.name,
                    "output": output_path.name,
                    "url": f"{settings.MEDIA_URL}outputs/{output_path.name}",
                }
            )
        except Exception as exc:
            results.append({"name": stored_path.name, "error": str(exc)})

    return JsonResponse({"results": results})


def upload_files(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    files = request.FILES.getlist("pdf_files")
    if not files:
        return JsonResponse({"error": "No files uploaded."}, status=400)

    services = _get_services()
    saved = services.uploads.save_files(files)
    return JsonResponse({"saved": saved})


def convert_selected_uploads(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    names = request.POST.getlist("names")
    if not names:
        return JsonResponse({"error": "No files selected."}, status=400)

    services = _get_services()
    results: list[dict[str, str]] = []
    for name in names:
        stored_path = services.uploads.root_dir / name
        if not stored_path.is_file():
            results.append({"name": name, "error": "File not found."})
            continue
        try:
            output_path = services.converter.convert(
                stored_path, services.outputs.root_dir
            )
            results.append(
                {
                    "name": stored_path.name,
                    "output": output_path.name,
                    "url": f"{settings.MEDIA_URL}outputs/{output_path.name}",
                }
            )
        except Exception as exc:
            results.append({"name": stored_path.name, "error": str(exc)})

    return JsonResponse({"results": results})


def list_uploads(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)

    services = _get_services()
    files = services.uploads.list_files()
    return JsonResponse({"files": [file.__dict__ for file in files]})


def delete_uploads(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    names = request.POST.getlist("names")
    if not names:
        return JsonResponse({"error": "No files selected."}, status=400)

    services = _get_services()
    deleted, skipped = services.uploads.delete_files(names)
    return JsonResponse({"deleted": deleted, "skipped": skipped})


def list_outputs(request: HttpRequest) -> JsonResponse:
    if request.method != "GET":
        return JsonResponse({"error": "GET required."}, status=405)

    services = _get_services()
    files = services.outputs.list_files(url_prefix=f"{settings.MEDIA_URL}outputs/")
    return JsonResponse({"files": [file.__dict__ for file in files]})


def delete_outputs(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    names = request.POST.getlist("names")
    if not names:
        return JsonResponse({"error": "No files selected."}, status=400)

    services = _get_services()
    deleted, skipped = services.outputs.delete_files(names)
    return JsonResponse({"deleted": deleted, "skipped": skipped})


def copy_outputs(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    names = request.POST.getlist("names")
    dest = request.POST.get("dest", "").strip()
    if not names:
        return JsonResponse({"error": "No files selected."}, status=400)
    if not dest:
        return JsonResponse({"error": "Destination path required."}, status=400)

    services = _get_services()
    results = services.output_files.copy_to(names, dest)
    destination = str(services.output_files.resolve_destination(dest))
    return JsonResponse({"results": results, "destination": destination})


def move_outputs(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    names = request.POST.getlist("names")
    dest = request.POST.get("dest", "").strip()
    if not names:
        return JsonResponse({"error": "No files selected."}, status=400)
    if not dest:
        return JsonResponse({"error": "Destination path required."}, status=400)

    services = _get_services()
    results = services.output_files.move_to(names, dest)
    destination = str(services.output_files.resolve_destination(dest))
    return JsonResponse({"results": results, "destination": destination})

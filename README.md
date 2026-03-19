# PDF to XLSX Converter

This project provides a Django web UI and a CLI to convert PDF tables into XLSX files using `tabula-py`.

## Architecture

The code is structured around a thin-controller + services architecture to keep responsibilities isolated and testable.

### Layers

- **UI (template + JS)**  
  The HTML/JS in `converter/templates/converter/index.html` renders the UI and calls API endpoints.

- **HTTP Controllers (views)**  
  `converter/views.py` validates requests and delegates work to services. Controllers do not perform filesystem or conversion logic directly.

- **Service Layer (dependency-injected)**  
  `converter/services/` contains independent services with clear responsibilities. This layer is designed for unit testing and mockable dependencies.

### Services

- **Conversion Service**  
  `converter/services/conversion.py` contains the conversion pipeline:
  - `TableExtractor` (interface)
  - `TabulaTableExtractor` (Tabula implementation)
  - `XlsxWriter` (interface)
  - `PandasXlsxWriter` (OpenPyXL-based implementation)
  - `OutputNamer` (interface)
  - `UniquePathNamer` (ensures unique output file names)
  - `PdfToXlsxConverter` (orchestrates extraction + write)

- **Storage Service**  
  `converter/services/storage.py` wraps filesystem operations:
  - save uploads
  - list files
  - delete files

- **Output File Service**  
  `converter/services/outputs.py` handles copy and move operations for files in `media/outputs`, including destination resolution.

### Dependency Injection

`converter/views.py` builds a `ServiceContainer` once per process and injects services into views through a `_get_services()` accessor. This makes it easy to replace services with mocks during tests.

## Dependencies

Runtime dependencies are in `requirements.txt`:

- `django`  
  Web framework for HTTP routing, templates, and static/media handling.
- `tabula-py`  
  Wrapper around tabula-java for extracting tables from PDFs.
- `pandas`  
  DataFrame operations and Excel export.
- `openpyxl`  
  XLSX file writer engine used by pandas.

System dependency:

- **Java**  
  `tabula-py` requires a working Java runtime (JRE/JDK).

## Data Security

This application handles user-uploaded PDF files and generated XLSX outputs on the local server filesystem. Key security considerations:

### Storage Locations

- Uploads are stored in `media/uploads`
- Converted XLSX files are stored in `media/outputs`

### Access Model

- Files are served only via Django’s development static file handler (when `DEBUG=True`).
- No external cloud storage or third-party file processing is used.
- All processing happens on the same machine where the server runs.

### Path Handling

- Copy/move endpoints accept a destination path. If a relative path is provided, it resolves under the project root (`BASE_DIR`).
- The UI provides a native folder picker in Edge/Chrome for copy/move actions, which runs **client-side** and does not expose OS paths to the server.

### Recommended Production Hardening

If deploying beyond a local environment, apply the following:

- Restrict `ALLOWED_HOSTS` and disable `DEBUG`.
- Add authentication to all upload/convert/copy/move/delete endpoints.
- Validate file types and size limits.
- Store uploads in a dedicated, non-public directory.
- Disable or restrict server-side copy/move to prevent filesystem exposure.
- Add antivirus or malware scanning for uploaded PDFs.
- Use a proper reverse proxy (e.g., Nginx) and serve media files securely.

## Docker

```powershell
docker compose up -d --build
```

App at `http://localhost:8000/`. Data (uploads, outputs, DB) is in a named volume `pdf2xlsx_data`.

## Deploy to QNAP NAS

Target: `192.168.0.213`. On the NAS: enable **SSH** (Control Panel → Terminal & SNMP) and **Container Station** (Docker).

From project root:

- **PowerShell:** `.\deploy.ps1` (set `$env:NAS_USER = "admin"` if needed)
- **Bash/WSL:** `chmod +x deploy.sh && ./deploy.sh` (set `NAS_USER`, `NAS_HOST`, `REMOTE_DIR` if needed)

Then open `http://192.168.0.213:8000/`.

## Running (local)

```powershell
pip install -r requirements.txt
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## CLI

```powershell
python convert_pdf_to_xlsx.py input.pdf --output-dir output_xlsx
```

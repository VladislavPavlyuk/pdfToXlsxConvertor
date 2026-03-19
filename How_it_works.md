Analyze project and explane how it works? Check if application send data from uploaded files somewere or just use external algorythms or dependencies? Is it safe ot use this application with private data?

Checking for network calls and reading the remaining critical files:

Checking the frontend for external requests:

Here’s the analysis.

How the project works
Purpose: Convert PDFs (tables) to XLSX via a Django web UI or a CLI script.

Flow:

Web: User uploads PDF(s) → Django saves to media/uploads → for each file, PdfToXlsxConverter runs → tables are extracted with tabula-py (local Java subprocess) → written to XLSX with pandas + openpyxl → files saved under media/outputs. Responses are JSON; the UI uses fetch/XHR only to the same Django app (relative URLs from {% url ... %}).

CLI: convert_pdf_to_xlsx.py uses the same pipeline: TabulaTableExtractor → PandasXlsxWriter → UniquePathNamer, no web layer.

Dependencies in use:

tabula-py – wrapper around tabula-java (JAR). It runs a local subprocess (force_subprocess=True); the PDF path is passed to that process and it reads the file from disk. No network involved.
pandas – in-memory DataFrames and Excel export.
openpyxl – writes the XLSX file on disk.
Django – HTTP, file handling, FileSystemStorage for uploads/outputs.
No other third-party services or APIs are used. There are no requests, urllib, httpx, or similar outbound HTTP calls in the project; the only “network” is the browser talking to your own Django server.

Does it send uploaded data anywhere?
No. File content is not sent to any external server or service.

Uploads go to media/uploads on the server.
Conversion is done by tabula-java (local process) and pandas/openpyxl (local).
Outputs go to media/outputs and are served by Django (or you can use copy/move endpoints to put them elsewhere on the same machine).
So: only local filesystem and local subprocess; no external APIs or cloud with your PDF/XLSX data.

Is it safe to use with private data?
From a “data leaving the machine” perspective, yes – the app and its dependencies do not transmit your files. Suited for private data as long as you treat the server as trusted (same as any local/self‑hosted tool).

Operational security caveats (as in the README):

No auth – anyone who can reach the app can upload, convert, list, delete, copy, move. Don’t expose it to the internet without adding authentication and tightening ALLOWED_HOSTS.
DEBUG=True – turn off in any non-local environment.
Copy/move – accept a server-side path; a malicious user could try path traversal. Validate/restrict destination paths and permissions if you expose these endpoints.
File type/size – only “PDF in the UI” is implied; no strict server-side check. Adding validation (and optionally virus scanning) is recommended for production.
Summary: The application does not send data from uploaded files anywhere; it only uses local algorithms and dependencies (tabula-java, pandas, openpyxl). It is safe to use with private data in the sense that the data stays on your machine, provided you secure the server (auth, DEBUG off, path checks) if you use it beyond localhost.
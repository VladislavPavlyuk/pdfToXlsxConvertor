# PDF to XLSX converter: Python + Java (for tabula)
FROM python:3.12-slim-bookworm

# Java required by tabula-py (tabula-java)
RUN apt-get update && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/app/data
ENV DEBUG=0
ENV ALLOWED_HOSTS=*

RUN mkdir -p /app/data/media

EXPOSE 8000

# Run migrations and gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn pdf_to_xlsx.wsgi:application --bind 0.0.0.0:8000 --workers 2"]

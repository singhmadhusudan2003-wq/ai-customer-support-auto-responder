# Root-level Dockerfile (convenience alias for the backend API service).
# This mirrors backend/Dockerfile so `docker build .` from the project root
# works out of the box. For the full multi-service setup (backend + frontend)
# use `docker-compose up` instead, which builds both services correctly.

FROM python:3.12-slim

WORKDIR /app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY dataset/ ../dataset/
COPY models/ ../models/

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s \
  CMD curl -f http://localhost:8000/api/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

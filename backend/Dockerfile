# GrowLocal API — Cloud Run image (prompt Step 14)
# Build:  gcloud run deploy growlocal-api --source backend --region asia-south1
# (Cloud Run maps $PORT automatically; PORT defaults to 8080 locally.)

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Layer 1 — dependencies only (fast rebuilds)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Layer 2 — code + seed data (app/data, app/prompts travel inside app/)
# .env is never in the image; Cloud Run uses runtime env vars.
COPY app ./app

# Non-root user (Cloud Run friendly)
RUN useradd --create-home --uid 10001 growlocal
USER growlocal

EXPOSE 8080

# PORT is injected by Cloud Run; default to 8080 elsewhere
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

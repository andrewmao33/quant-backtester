# syntax=docker/dockerfile:1

# Root-level Dockerfile: builds and runs the backend API
# Useful for platforms expecting a Dockerfile at repo root (e.g., Render Web Service without rootDir)

FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app/backend

# System deps for pandas and SQLite
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       liblapack-dev \
       gfortran \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy backend app code and data
COPY backend/src /app/backend/src
COPY backend/data /app/backend/data

# Ensure data dir exists (and can be mounted)
RUN mkdir -p /app/backend/data

EXPOSE 8000

CMD ["uvicorn", "src.api.server:app", "--host", "0.0.0.0", "--port", "8000"]

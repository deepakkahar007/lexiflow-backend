# Build stage
FROM astral/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

# Export locked dependencies to requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv export --frozen --no-dev -o requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Copy uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy requirements first
COPY --from=builder /app/requirements.txt .

# Install build dependencies, install python packages, and clean up in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && uv pip install --system --no-cache -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY src ./src

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose FastAPI port
EXPOSE 8000

# Run the application
CMD ["python", "-m", "fastapi", "run", "src/main.py", "--port", "8000", "--host", "0.0.0.0"]




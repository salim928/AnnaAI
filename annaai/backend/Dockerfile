FROM python:3.12-slim

# uv — fast Python package manager (replaces pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# System deps for lxml, asyncpg, Pillow, cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        libjpeg-dev \
        zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps via uv (much faster than pip)
COPY pyproject.toml .
RUN uv pip install --system -e ".[dev]"

# Install torch CPU separately — avoids the 2GB CUDA build
RUN uv pip install --system torch \
        --index-url https://download.pytorch.org/whl/cpu

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

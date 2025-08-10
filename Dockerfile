# ============================
# 1️⃣ Build Stage
# ============================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies (including prisma)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir prisma

# Copy source code
COPY . .

# Generate Prisma client (writes into installed prisma package)
RUN prisma generate

# Fetch Prisma query engine binary for production
RUN prisma py fetch


# ============================
# 2️⃣ Runtime Stage
# ============================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed packages (with generated Prisma client & query engine) from builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /root/.cache /root/.cache

# Copy app source code
COPY --from=builder /app /app

# Clean up unnecessary files
RUN apt-get purge -y --auto-remove && rm -rf /var/lib/apt/lists/* /root/.cache/pip

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
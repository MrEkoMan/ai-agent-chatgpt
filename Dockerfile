FROM node:18-alpine AS ui-build

# Install deps and build the web UI (Vite)
WORKDIR /app/webui
COPY webui/package.json webui/package-lock.json* ./
RUN npm install --legacy-peer-deps || true
COPY webui/ .
RUN npm run build || true
RUN if [ -d dist ]; then mv dist /dist || true; fi

FROM python:3.13-slim AS base

# Do not write pyc files and make output unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Create a virtualenv to isolate dependencies (recommended by official images)
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies first by copying only requirements.txt
# This lets Docker cache the pip install layer when the app source changes.
COPY requirements.txt ./
COPY requirements.lock ./
RUN pip install --upgrade pip setuptools wheel \
    && if [ -s requirements.lock ]; then pip install --no-cache-dir -r requirements.lock; \
       elif [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi \
    # Ensure uvicorn is available even if not pinned in requirements (safe fallback)
    && pip install --no-cache-dir "uvicorn[standard]" || true

# Copy application code
COPY . /app

# Copy compiled web UI from the builder stage (if produced)
COPY --from=ui-build /dist /app/webui_dist

# Create a non-root user and fix permissions for the venv and app folder
RUN useradd --create-home --uid 1000 appuser || true \
    && chown -R appuser:appuser /app /opt/venv

# Switch to non-root user (good practice for production)
USER appuser

# Expose API port
EXPOSE 8000

# Default command: run the FastAPI app via the venv python -m uvicorn
# Use --host 0.0.0.0 so the container accepts external connections
CMD ["/opt/venv/bin/python", "-m", "uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

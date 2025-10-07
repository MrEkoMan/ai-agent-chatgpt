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
       elif [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application code
COPY . /app

# Create a non-root user and fix permissions for the venv and app folder
RUN useradd --create-home --uid 1000 appuser || true \
    && chown -R appuser:appuser /app /opt/venv

# Switch to non-root user (good practice for production)
USER appuser

# Default command: run the example agent (uses lazy imports/fallback)
CMD ["python", "agent.py"]

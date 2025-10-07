FROM python:3.13-slim

# Create app directory
WORKDIR /app

# Install build deps then runtime deps
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && if [ -s requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy application
COPY . /app

# Do not run as root in production images; use a non-root user
RUN useradd --create-home appuser || true
USER appuser

ENV PYTHONUNBUFFERED=1

# Default command: run the example agent (uses lazy imports/fallback)
CMD ["python", "agent.py"]

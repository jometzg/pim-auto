FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (none needed initially, but prepared for future)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check (uses new health check endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -m pim_auto.main --mode health || exit 1

# Default command - run the PIM Auto application
CMD ["python", "-m", "pim_auto.main"]

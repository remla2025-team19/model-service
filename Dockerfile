# Stage 1: Build dependencies
FROM python:3.12.9-slim AS builder

WORKDIR /build

# Copy requirements file
COPY requirements.txt .

# Install git for dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Final lightweight runtime image
FROM python:3.12.9-slim

WORKDIR /app

# Copy only what's needed from the builder stage
COPY --from=builder /install /usr/local
COPY service.py /app/

# Set environment variables for REST API configuration and model version
# These can be overridden at runtime
ENV MODEL_SERVICE_HOST=0.0.0.0
ENV MODEL_SERVICE_PORT=8080
ENV MODEL_VERSION=v1.0.11
ENV MODEL_CACHE_DIR=/app/models_cache

# Create directory for model cache
RUN mkdir -p ${MODEL_CACHE_DIR}

# Document the port that will be exposed by the container
EXPOSE ${MODEL_SERVICE_PORT}

# Set Python to not write .pyc files and to not buffer stdout/stderr for better logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Setup volume for model cache persistence
VOLUME ["${MODEL_CACHE_DIR}"]

# Install curl for healthcheck
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Health check to ensure the service is running properly
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://${MODEL_SERVICE_HOST}:${MODEL_SERVICE_PORT}/health || exit 1

ENTRYPOINT ["python"]
CMD ["service.py"]

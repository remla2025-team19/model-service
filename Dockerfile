# Stage 1: Build and download dependencies
FROM python:3.12.9-slim AS builder

WORKDIR /build

# Copy requirements file
COPY requirements.txt .

# Install git and curl for dependencies and model download
RUN apt-get update && \
    apt-get install -y --no-install-recommends git curl && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt && \
    curl -L https://github.com/remla2025-team19/model-training/releases/download/v1.0.11/sentiment_model_v1.0.11.pkl -o /build/sentiment_model.pkl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Stage 2: Final lightweight runtime image
FROM python:3.12.9-slim

WORKDIR /root

# Copy only what's needed from the builder stage
COPY --from=builder /install /usr/local
COPY --from=builder /build/sentiment_model.pkl /root/sentiment_model.pkl
COPY service.py /root/

# Set host and port environment variables
ENV MODEL_SERVICE_HOST=0.0.0.0
ENV MODEL_SERVICE_PORT=8080

# Set Python to not write .pyc files and to not buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python"]
CMD ["service.py"]
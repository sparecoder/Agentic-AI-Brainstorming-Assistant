# Build stage for cleaning up dependencies
FROM python:3.9-slim AS builder

WORKDIR /app

# Install system dependencies for ChromaDB and other native extensions
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads chroma_db

# Expose port (HF Spaces defaults to 7860)
ENV PORT=7860
EXPOSE 7860

# Command to run the application
CMD python3 -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}

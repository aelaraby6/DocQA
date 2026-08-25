FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/app/cache/huggingface

WORKDIR /app

# Install system dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Hugging Face SentenceTransformer model during build time
# to ensure it's baked into the image, avoiding runtime download delays.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application files
COPY src/ ./src/
COPY ui/ ./ui/
COPY data/ ./data/

# Create runtime directories
RUN mkdir -p uploads

# Expose ports
EXPOSE 8000
EXPOSE 8501

# Copy the entrypoint script
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Use bash entrypoint to start either backend or frontend service
ENTRYPOINT ["/app/docker-entrypoint.sh"]

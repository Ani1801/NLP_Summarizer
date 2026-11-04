FROM python:3.11-slim

WORKDIR /app

# System dependencies for PyMuPDF and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch (prevents 2.5GB CUDA packages from bloating image)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install production Python dependencies
COPY requirements.prod.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model into image cache so runtime indexing is instant
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY . .

# Create uploads directory (ephemeral — PDF preview won't persist across restarts on free tier)
RUN mkdir -p uploads

EXPOSE 8000

# Use PORT env var if set (Koyeb/Render compatibility), default to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

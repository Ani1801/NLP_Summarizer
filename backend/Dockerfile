FROM python:3.11-slim

WORKDIR /app

# System dependencies for PyMuPDF and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory (ephemeral — PDF preview won't persist across restarts on free tier)
RUN mkdir -p uploads

EXPOSE 8000

# Use PORT env var if set (Koyeb/Render compatibility), default to 8000
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

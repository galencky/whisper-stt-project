FROM python:3.11-slim

# ---------- system packages ----------
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc tini && \
    rm -rf /var/lib/apt/lists/*

# ---------- working dir ----------
WORKDIR /app

# ---------- python deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- project ----------
COPY . .

# ---------- ensure data dirs exist & writable ----------
RUN mkdir -p /app/data/inbox /app/data/processed /app/data/transcripts \
           /app/data/parsed /app/data/markdown /app/data/uploaded \
           /app/data/models /app/data/logs && \
    chmod -R 775 /app/data                              # <-- R/W fix

# ---------- non-root user ----------
RUN useradd -ms /bin/bash syno && \
    chown -R syno:syno /app
USER syno

ENTRYPOINT ["tini", "--"]
CMD ["python", "main.py"]

# ─────────────────────────────────────────────────────────────
# Dockerfile   (build with:  docker build -t whisper-stt . )
# ─────────────────────────────────────────────────────────────
FROM python:3.11-slim

# ---------- system packages ----------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc tini ffmpeg  \
    && rm -rf /var/lib/apt/lists/*

# ---------- working dir ----------
WORKDIR /app

# ---------- python deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- project ----------
COPY app/   app/
COPY prompts/ prompts/
COPY start.sh .

# ---------- non-root user (match Synology share UID/GID) ----------
ARG PUID=1000
ARG PGID=100
RUN groupadd -g ${PGID} syno && \
    useradd  -u ${PUID} -g syno -ms /bin/bash syno
# take ownership of project files
RUN chown -R syno:syno /app

# ---------- create mutable folders ----------
RUN mkdir -p /data /app/output && \
    chmod -R 775 /data /app/output
VOLUME ["/data"]   # <- bind your share here

# ---------- final tweaks ----------
USER syno
RUN chmod +x /app/start.sh
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/start.sh"]

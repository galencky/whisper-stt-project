FROM python:3.11-slim

# ffmpeg for Whisper + build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg git build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source
COPY app/ app/
COPY prompts/ prompts/

ENV BASE_DIR=/data
VOLUME ["/data"]         # bind-mount on Synology

ENTRYPOINT ["python", "-m", "app.main"]
CMD ["all"]

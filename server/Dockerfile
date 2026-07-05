# Build context is the REPO ROOT (see docker-compose.yml) so the shared
# `pipeline` package can be copied in alongside the server.
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional cloned-voice TTS engine (XTTS-v2). Off by default — it pulls in
# torch and a multi-GB model download, only worth it if TTS_ENGINE=xtts.
# Enable with: docker compose build --build-arg INSTALL_XTTS=true
ARG INSTALL_XTTS=false
RUN if [ "$INSTALL_XTTS" = "true" ]; then \
    apt-get update && apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir "transformers>=4.57,<5" "coqui-tts[codec]==0.27.5"; \
    fi

COPY pipeline/ ./pipeline/
COPY server/app.py .

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

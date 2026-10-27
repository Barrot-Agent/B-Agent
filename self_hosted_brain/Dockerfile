FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone --depth 1 https://github.com/ggerganov/llama.cpp.git . \
    && cmake -B build -DGGML_NATIVE=OFF \
    && cmake --build build -j$(nproc) --target llama-server \
    && cp build/bin/llama-server /app/llama-server \
    && rm -rf build .git

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh \
    && useradd -m -u 1000 appuser && chown -R appuser:appuser /app

USER appuser
ENV HOME=/app
ENV MODEL_REPO="FINAL-Bench/Ourbox-35B-JGOS-GGUF"
ENV MODEL_FILE="ourbox35b-IQ1_M.gguf"
ENV PORT=7860

EXPOSE 7860
CMD ["/app/start.sh"]

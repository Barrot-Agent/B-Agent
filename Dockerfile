FROM mcr.microsoft.com/devcontainers/python:3.13

# Install system dependencies for animation and computation
RUN apt-get update && apt-get install -y \
    rustc \
    cargo \
    ffmpeg \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install AI and processing libraries
RUN pip install --no-cache-dir \
    huggingface_hub \
    hf-xet \
    pyyaml \
    numpy \
    opencv-python

# Set working directory to the workspace
WORKDIR /workspaces/B-Agent

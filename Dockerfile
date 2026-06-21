FROM python:3.11-slim

# Install system dependencies and git
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install uv for ultra-fast, lightweight package execution
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:${PATH}"

# Setup workspace
WORKDIR /workspace
RUN git clone https://github.com/SeanDrew-LeadTechArchitect/B-Agent.git /workspace/B-Agent

# Expose the Model Context Protocol standard standard-input/standard-output port
ENTRYPOINT ["uvx", "mcp-server-git", "--repository", "/workspace/B-Agent"]


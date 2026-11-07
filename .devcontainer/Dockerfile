FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential ca-certificates curl git jq libffi-dev libssl-dev make \
    && apt-get clean

# GitHub CLI is installed through the devcontainer feature in devcontainer.json.
# No API keys, tokens, or other credentials are baked into this image.

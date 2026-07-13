---
title: Barrot Self-Hosted Brain
emoji: 🧠
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Barrot-Ω Self-Hosted Brain

OpenAI-compatible inference endpoint running Ourbox-35B-JGOS (sparse MoE,
IQ1_M quant, ~3B active params) via llama.cpp on free CPU hardware.

No rate limits, no daily quota — dedicated compute instead of a shared
free tier. Trade-off: first request after a cold start re-downloads the
~8GB model file (Spaces sleep after 48h idle).

Endpoint: POST /v1/chat/completions
Auth: Bearer token via BRAIN_SHARED_SECRET

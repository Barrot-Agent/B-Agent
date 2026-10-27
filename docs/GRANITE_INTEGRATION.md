# IBM Granite 4.0-3b-vision Integration

## Overview

This document describes the integration of the **ibm-granite/granite-4.0-3b-vision**
multimodal vision-language model into the Barrot-Agent / B-Agent infrastructure.

| Field | Value |
|---|---|
| Model ID | `ibm-granite/granite-4.0-3b-vision` |
| Organization | IBM Granite |
| Parameters | 4 B |
| Tensor Type | BF16 |
| License | Apache 2.0 |
| Downloads (last month) | 5,724 |
| Architecture | granite4\_vision (Multimodal VLM) |
| Language | English |

---

## Capabilities

| Capability | Supported |
|---|---|
| Image-Text-to-Text | ✅ |
| Feature Extraction | ✅ |
| Conversational / Chat | ✅ |
| Custom Code Extensions | ✅ |
| Safetensors Format | ✅ |
| Chat Template | ✅ |

---

## Repository Files Added

| File | Purpose |
|---|---|
| `granite_model_config.py` | Model specifications, metadata, and load/inference config constants |
| `vision_pipeline.py` | Low-level `GraniteVisionPipeline` class (load, run, chat, extract\_features) |
| `inference_provider.py` | High-level module-singleton API (`infer`, `chat`, `extract_features`, metadata helpers) |
| `examples/vision_examples.py` | Runnable usage examples |
| `docs/GRANITE_INTEGRATION.md` | This document |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Single-image inference

```python
from inference_provider import infer

response = infer(
    prompt="Describe what you see in this image.",
    images="photo.jpg",
)
print(response)
```

### 3. Multi-turn chat

```python
from inference_provider import chat

conversation = [
    {
        "role": "user",
        "content": [
            {"type": "image"},
            {"type": "text", "text": "What is shown here?"},
        ],
    }
]
reply = chat(conversation=conversation, images="photo.jpg")
print(reply)
```

### 4. Feature extraction

```python
from inference_provider import extract_features

features = extract_features("Embed this image.", images="photo.jpg")
print(features.shape)   # (1, seq_len, hidden_dim)  dtype=bfloat16
```

### 5. Run example scripts

```bash
# Print metadata (no GPU / model download required)
python examples/vision_examples.py info

# Run image description example
python examples/vision_examples.py describe
```

---

## BF16 Precision

The model is loaded in **bfloat16** (`torch.bfloat16`) by default, matching the
published tensor type from the Hugging Face model card.  This halves GPU memory
usage compared with FP32 while retaining the dynamic range needed for large
language model weights.

---

## ArXiv References

The following research papers are associated with the IBM Granite model family:

| Reference | Link |
|---|---|
| arxiv:2603.27064 | <https://arxiv.org/abs/2603.27064> |
| arxiv:2404.19205 | <https://arxiv.org/abs/2404.19205> |
| arxiv:2412.07626 | <https://arxiv.org/abs/2412.07626> |
| arxiv:2512.10888 | <https://arxiv.org/abs/2512.10888> |
| arxiv:2208.00385 | <https://arxiv.org/abs/2208.00385> |
| arxiv:2502.09927 | <https://arxiv.org/abs/2502.09927> |
| arxiv:2406.04334 | <https://arxiv.org/abs/2406.04334> |

---

## Architecture Notes

- **Model type:** `granite4_vision` — IBM's multimodal vision encoder fused with a
  Granite language decoder.
- **Inference provider:** The `inference_provider.py` module keeps a process-level
  singleton so the model is loaded only once per Python process, avoiding redundant
  GPU memory allocations.
- **Device map:** `"auto"` — automatically spreads model layers across available
  GPU(s) / CPU via `accelerate`.
- **Chat template:** Applied via `processor.apply_chat_template()`, fully compatible
  with the Granite conversational format published on Hugging Face.

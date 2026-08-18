"""
IBM Granite 4.0-3b-vision Model Configuration
Source: https://huggingface.co/ibm-granite/granite-4.0-3b-vision
License: Apache 2.0
"""

MODEL_ID = "ibm-granite/granite-4.0-3b-vision"

MODEL_METADATA = {
    "model_id": MODEL_ID,
    "organization": "IBM Granite",
    "parameters": "4B",
    "tensor_type": "BF16",
    "license": "Apache 2.0",
    "downloads_last_month": 5724,
    "likes": 82,
    "followers": 4200,
    "language": ["en"],
    "model_type": "granite4_vision",
    "architecture": "Multimodal Vision-Language Model",
}

MODEL_TAGS = [
    "image-text-to-text",
    "transformers",
    "safetensors",
    "english",
    "granite4_vision",
    "feature-extraction",
    "conversational",
    "custom_code",
]

ARXIV_REFERENCES = [
    "arxiv:2603.27064",
    "arxiv:2404.19205",
    "arxiv:2412.07626",
    "arxiv:2512.10888",
    "arxiv:2208.00385",
    "arxiv:2502.09927",
    "arxiv:2406.04334",
]

CAPABILITIES = {
    "image_text_to_text": True,
    "feature_extraction": True,
    "conversational": True,
    "custom_code": True,
    "safetensors": True,
    "chat_template": True,
}

LOAD_CONFIG = {
    "torch_dtype": "bfloat16",
    "device_map": "auto",
    "trust_remote_code": True,
}

INFERENCE_CONFIG = {
    "max_new_tokens": 1024,
    "do_sample": False,
    "temperature": None,
    "top_p": None,
}

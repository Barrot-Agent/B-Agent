"""
IBM Granite 4.0-3b-vision — Usage Examples
============================================
Demonstrates single-image Q&A, multi-turn chat, and feature extraction.
"""

# ---------------------------------------------------------------------------
# Example 1 – Simple image description
# ---------------------------------------------------------------------------


def example_describe_image():
    from inference_provider import infer

    response = infer(
        prompt="Describe what you see in this image in detail.",
        images="sample.jpg",
    )
    print("=== Image Description ===")
    print(response)


# ---------------------------------------------------------------------------
# Example 2 – Visual question answering
# ---------------------------------------------------------------------------


def example_visual_qa():
    from inference_provider import infer

    response = infer(
        prompt="What objects are present in this image? List them.",
        images="sample.jpg",
        max_new_tokens=256,
    )
    print("=== Visual QA ===")
    print(response)


# ---------------------------------------------------------------------------
# Example 3 – Multi-turn chat with an image
# ---------------------------------------------------------------------------


def example_multi_turn_chat():
    from inference_provider import chat

    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": "What is shown in this image?"},
            ],
        }
    ]

    reply = chat(conversation=conversation, images="sample.jpg")
    print("=== Turn 1 ===")
    print(reply)

    # Follow-up turn (no image needed for subsequent messages)
    conversation.append({"role": "assistant", "content": reply})
    conversation.append({"role": "user", "content": "Can you describe the colours you see?"})

    reply2 = chat(conversation=conversation)
    print("=== Turn 2 ===")
    print(reply2)


# ---------------------------------------------------------------------------
# Example 4 – Feature extraction
# ---------------------------------------------------------------------------


def example_feature_extraction():
    from inference_provider import extract_features

    features = extract_features(
        prompt="Extract visual features from this image.",
        images="sample.jpg",
    )
    print("=== Feature Extraction ===")
    print(f"Embedding shape : {features.shape}")
    print(f"Tensor dtype    : {features.dtype}")


# ---------------------------------------------------------------------------
# Example 5 – Image from URL
# ---------------------------------------------------------------------------


def example_image_from_url():
    from inference_provider import infer

    url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/240px-PNG_transparency_demonstration_1.png"
    response = infer(
        prompt="What is depicted in this image?",
        images=url,
    )
    print("=== Image from URL ===")
    print(response)


# ---------------------------------------------------------------------------
# Example 6 – Model metadata
# ---------------------------------------------------------------------------


def example_model_info():
    from inference_provider import get_model_info, list_capabilities

    info = get_model_info()
    print("=== Model Metadata ===")
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n=== Supported Capabilities ===")
    for cap in list_capabilities():
        print(f"  ✓ {cap}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    examples = {
        "describe": example_describe_image,
        "qa": example_visual_qa,
        "chat": example_multi_turn_chat,
        "features": example_feature_extraction,
        "url": example_image_from_url,
        "info": example_model_info,
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        examples[sys.argv[1]]()
    else:
        print("Usage: python vision_examples.py [describe|qa|chat|features|url|info]")
        print("\nRunning metadata example (no model load required)...")
        example_model_info()

"""
Example Usage: Multimodal Processing Demo

Run from repository root with:
    PYTHONPATH=. python examples/multimodal_demo.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.multimodal_processor import initialize_multimodal

def main():
    print("=" * 60)
    print("Multimodal Processing Demo")
    print("=" * 60)
    
    # Initialize
    components = initialize_multimodal()
    processor = components['processor']
    vision = components['vision']
    audio = components['audio']
    
    # 1. Process text
    print("\n1. Processing text...")
    text_result = processor.process_text(
        "The quick brown fox jumps over the lazy dog. AI is transforming the world!",
        metadata={'source': 'example'}
    )
    print(f"   Words: {text_result['features']['word_count']}")
    print(f"   Characters: {text_result['features']['character_count']}")
    
    # 2. Process image
    print("\n2. Processing image...")
    image_result = processor.process_image(
        '/path/to/image.jpg',
        metadata={'source': 'example'}
    )
    print(f"   Format: {image_result['features']['format']}")
    print(f"   OpenCV ready: {image_result['features']['opencv_ready']}")
    print(f"   Note: {image_result['analysis']['note']}")
    
    # 3. Process audio
    print("\n3. Processing audio...")
    audio_result = processor.process_audio(
        '/path/to/audio.wav',
        metadata={'source': 'example'}
    )
    print(f"   Format: {audio_result['features']['format']}")
    print(f"   Whisper ready: {audio_result['features']['whisper_ready']}")
    print(f"   Note: {audio_result['analysis']['note']}")
    
    # 4. Fuse modalities
    print("\n4. Fusing multiple modalities...")
    fusion = processor.fuse_modalities([text_result, image_result, audio_result])
    print(f"   Modalities fused: {', '.join(fusion['modalities'])}")
    print(f"   Fusion method: {fusion['fusion_method']}")
    
    # 5. Vision processing
    print("\n5. Vision processing capabilities...")
    detection = vision.detect_objects('/path/to/image.jpg')
    print(f"   Detection note: {detection['integration_note']}")
    
    features = vision.extract_features('/path/to/image.jpg')
    print(f"   Feature extraction note: {features['integration_note']}")
    
    # 6. Audio processing
    print("\n6. Audio processing capabilities...")
    transcription = audio.transcribe('/path/to/audio.wav')
    print(f"   Transcription note: {transcription['integration_note']}")
    
    analysis = audio.analyze_audio('/path/to/audio.wav')
    print(f"   Analysis note: {analysis['integration_note']}")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()

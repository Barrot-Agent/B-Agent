# Barrot AGI Examples

This directory contains example scripts demonstrating the usage of various AGI modules.

## Available Examples

### 1. Autonomous Learning Demo (`autonomous_learning_demo.py`)
Demonstrates self-improvement pipeline and meta-learning capabilities:
- Performance evaluation
- Improvement plan generation
- Cross-domain knowledge transfer
- Meta-learning insights

Run: `python examples/autonomous_learning_demo.py`

### 2. Multimodal Processing Demo (`multimodal_demo.py`)
Shows multimodal data processing across text, images, and audio:
- Text processing
- Image analysis (OpenCV integration point)
- Audio transcription (Whisper integration point)
- Multimodal fusion

Run: `python examples/multimodal_demo.py`

### 3. Knowledge Graph Demo (`knowledge_graph_demo.py`)
Illustrates knowledge graph construction and reasoning:
- Building knowledge graphs
- Querying relationships
- Path finding
- Cross-domain reasoning

Run: `python examples/knowledge_graph_demo.py`

## Running Examples

From the repository root:

```bash
# Run individual examples
python examples/autonomous_learning_demo.py
python examples/multimodal_demo.py
python examples/knowledge_graph_demo.py
```

## Creating Your Own Examples

Each module can be imported and used independently:

```python
from modules.<module_name> import initialize_<module_name>

components = initialize_<module_name>()
# Use components...
```

See the existing examples for patterns and best practices.

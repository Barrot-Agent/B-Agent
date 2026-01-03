# 🚀 Pipeline Quick Start Guide

## What is it?

A modular, extensible processing pipeline for handling events in the B-Agent repository. Each event passes through specialized agents that transform, enrich, and validate the data.

## Quick Demo

### 1. Run the Claude Impact Pipeline
```bash
cd matrix
python3 claude_impact_pipeline.py
```

**Output:**
```
✅ Event processed successfully
✅ Quality Score: 100%
✅ Insights extracted
✅ Integrated with systems
```

### 2. Run the Tests
```bash
python3 test_pipeline.py
```

**Output:**
```
✅ 13/13 tests passing
```

### 3. Try the Custom Agent Example
```bash
python3 example_custom_agents.py
```

**Output:**
```
✅ Custom agents added successfully
✅ Sentiment: positive (70% confidence)
✅ Priority: HIGH (80% confidence)
```

## How It Works

```
Event → Ingestion → Enrichment → Analysis → Validation → Integration → Output
          ↓            ↓            ↓           ↓             ↓
       Validates   Adds Context  Extracts   Ensures      Connects
       Data        & Metadata    Insights   Quality      Systems
```

## Add Your Own Agent (3 Steps)

### Step 1: Create Agent Class
```python
from pipeline_orchestrator import PipelineAgent

class MyAgent(PipelineAgent):
    def __init__(self):
        super().__init__("MyAgent", "My Role")
    
    def process(self, data):
        data['my_output'] = 'my_value'
        return data
```

### Step 2: Add to Pipeline
```python
from pipeline_orchestrator import PipelineStage, create_pipeline

stage = PipelineStage("MyStage", [MyAgent()])
pipeline = create_pipeline("my_pipeline", [stage])
```

### Step 3: Execute
```python
result = pipeline.execute({'input': 'data'})
print(result['my_output'])  # 'my_value'
```

## Key Features

- ✅ **Modular**: Each agent is independent
- ✅ **Extensible**: Add agents in 3 simple steps
- ✅ **Tested**: 13 comprehensive tests
- ✅ **Documented**: Complete guides available
- ✅ **Production Ready**: 100% quality score

## Files to Explore

1. `matrix/claude_impact_pipeline.py` - Example pipeline
2. `matrix/example_custom_agents.py` - Extensibility demo
3. `matrix/test_pipeline.py` - Test suite
4. `PIPELINE_ARCHITECTURE.md` - Complete architecture
5. `PIPELINE_CONFIGURATION.md` - Configuration guide

## Need Help?

See the detailed documentation:
- **Architecture**: `PIPELINE_ARCHITECTURE.md`
- **Configuration**: `PIPELINE_CONFIGURATION.md`
- **Summary**: `PIPELINE_IMPLEMENTATION_SUMMARY.md`

## Status

✅ **Production Ready** - All systems operational!

---

**Version**: 1.0  
**Date**: 2026-01-03

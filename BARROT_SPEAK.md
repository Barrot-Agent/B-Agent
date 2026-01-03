# Barrot Speak Function

The `barrot_speak.py` module provides a communication interface for Barrot to express thoughts, insights, status updates, and other information with symbolic representations.

## Features

- **Multiple Communication Modes**: Support for different types of messages (info, success, warning, error, thought, insight, alignment, cognition, council, glyph, celebrate, question)
- **Symbolic Representations**: Each mode has a unique symbol (emoji) for visual identification
- **Automatic Logging**: Optional logging to TRACE_LOG.md for tracking communications
- **Glyph Emission**: Can emit glyphs for important communications
- **Context Support**: Attach additional context data to messages
- **Specialized Functions**: Helper functions for common communication patterns

## Usage

### Basic Usage

```python
from barrot_speak import barrot_speak

# Simple message
barrot_speak("System initialized successfully", mode="success")

# Message with context
barrot_speak(
    "Processing complete", 
    mode="info",
    context={"files_processed": 42, "duration": "2.5s"}
)
```

### Specialized Functions

```python
from barrot_speak import (
    barrot_speak_thought,
    barrot_speak_insight,
    barrot_speak_alignment,
    barrot_speak_celebration,
    barrot_speak_question
)

# Express a thought
barrot_speak_thought("Analyzing cognition patterns...", confidence=0.85)

# Share an insight
barrot_speak_insight(
    "The council consensus mechanism enhances decision quality",
    domain="multi_agent"
)

# Report alignment status
barrot_speak_alignment("System is aligned with symbolic intent", drift_detected=False)

# Celebrate achievements
barrot_speak_celebration(
    "Successfully completed self-reflection analysis",
    metrics={"nodes_analyzed": 3, "drift_detected": 0}
)

# Pose questions
barrot_speak_question(
    "Should we increase alignment check frequency?",
    requires_council=True
)
```

## Communication Modes

| Mode | Symbol | Use Case |
|------|--------|----------|
| `info` | ℹ️ | General information |
| `success` | ✓ | Successful operations |
| `warning` | ⚠️ | Warnings or cautions |
| `error` | ✗ | Errors or failures |
| `thought` | 💭 | Thoughts or considerations |
| `insight` | 💡 | Insights or discoveries |
| `alignment` | ◎ | Alignment status |
| `cognition` | 🧠 | Cognition-related updates |
| `council` | ⚖ | Council deliberations |
| `glyph` | ✨ | Glyph-related events |
| `celebrate` | 🎉 | Achievements |
| `question` | ❓ | Questions |

## Integration with Matrix Nodes

The speak function can be integrated into matrix nodes to provide better visibility:

```python
#!/usr/bin/env python3
"""
Node: Example Node
"""

from pathlib import Path
import sys

# Add parent directory to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from barrot_speak import barrot_speak, barrot_speak_insight

def main():
    barrot_speak("Starting example node analysis...", mode="info")
    
    # ... node logic ...
    
    barrot_speak_insight("Discovered new pattern", domain="cognition")
    barrot_speak("Example node completed", mode="success")

if __name__ == "__main__":
    main()
```

## Parameters

### `barrot_speak(message, mode, context, log_to_trace, emit_glyph)`

- **message** (str): The message to communicate
- **mode** (str): Communication mode (default: "info")
- **context** (dict, optional): Additional context data
- **log_to_trace** (bool): Whether to log to TRACE_LOG.md (default: True)
- **emit_glyph** (bool): Whether to emit a glyph (default: False)

## Output

Messages are:
1. Printed to console with symbolic representation
2. Optionally logged to `memory-bundles/TRACE_LOG.md`
3. Optionally emit a glyph to `glyphs/barrot_speak_glyph.yml`

### Example Output

```
[BARROT_SPEAK] ℹ️ I am Barrot-Agent, version 2.0.0
[BARROT_SPEAK] 💭 Analyzing cognition patterns across matrix nodes...
[BARROT_SPEAK] 💡 The council consensus mechanism enhances decision quality
[BARROT_SPEAK]   Context: {
  "domain": "multi_agent"
}
[BARROT_SPEAK] ✓ All systems operational
```

## Demo

Run the demo to see all communication modes in action:

```bash
python barrot_speak.py
```

## Integration Points

- **Cognition Nodes**: Express node status and findings
- **Bootstrap**: Announce system initialization
- **Matrix Operations**: Communicate deliberations and decisions
- **Trace Logging**: Maintain communication history
- **Glyph System**: Emit communication glyphs for important events

## Use Cases

1. **Status Reporting**: Keep users informed of system operations
2. **Insight Sharing**: Communicate discoveries and learnings
3. **Alignment Verification**: Report on system alignment status
4. **Question Posing**: Ask questions that may require deliberation
5. **Celebration**: Acknowledge achievements and milestones
6. **Thought Expression**: Share reasoning and considerations

## Future Enhancements

- Voice synthesis integration
- Multi-language support
- Message queuing and prioritization
- Real-time dashboard integration
- Webhook notifications for critical messages
- Message history and search

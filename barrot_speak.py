#!/usr/bin/env python3
"""
Barrot Speak Function
Allows Barrot to communicate thoughts, status, and insights with symbolic representations.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional, Dict, Any

# Paths
REPO_ROOT = Path(__file__).resolve().parent
MANIFEST_PATH = REPO_ROOT / "barrot_manifest.json"
GLYPHS_PATH = REPO_ROOT / "glyphs"
TRACE_LOG_PATH = REPO_ROOT / "memory-bundles" / "TRACE_LOG.md"

# Symbolic representations for different message types
SYMBOLS = {
    "info": "ℹ️ ",
    "success": "✓ ",
    "warning": "⚠️ ",
    "error": "✗ ",
    "thought": "💭 ",
    "insight": "💡 ",
    "alignment": "◎ ",
    "cognition": "🧠 ",
    "council": "⚖ ",
    "glyph": "✨ ",
    "celebrate": "🎉 ",
    "question": "❓ "
}

def barrot_speak(
    message: str,
    mode: str = "info",
    context: Optional[Dict[str, Any]] = None,
    log_to_trace: bool = True,
    emit_glyph: bool = False
) -> str:
    """
    Main speak function for Barrot to communicate.
    
    Args:
        message: The message to speak
        mode: Type of message (info, success, warning, error, thought, insight, 
              alignment, cognition, council, glyph, celebrate, question)
        context: Additional context data (optional)
        log_to_trace: Whether to log to TRACE_LOG.md (default: True)
        emit_glyph: Whether to emit a glyph for this message (default: False)
    
    Returns:
        Formatted message string
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    symbol = SYMBOLS.get(mode, "")
    
    # Format the message
    formatted_message = f"[BARROT_SPEAK] {symbol}{message}"
    
    # Print to console
    print(formatted_message)
    
    # Add context if provided
    if context:
        print(f"[BARROT_SPEAK]   Context: {json.dumps(context, indent=2)}")
    
    # Log to trace if requested
    if log_to_trace:
        try:
            # Ensure directory exists
            TRACE_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            log_entry = f"""
## Barrot Spoke: {timestamp}
**Mode:** {mode}
**Message:** {message}
"""
            if context:
                log_entry += f"**Context:** {json.dumps(context, indent=2)}\n"
            
            log_entry += "\n---\n"
            
            with open(TRACE_LOG_PATH, 'a') as f:
                f.write(log_entry)
        except (IOError, OSError) as e:
            print(f"[BARROT_SPEAK] Warning: Could not write to trace log: {e}")
    
    # Emit glyph if requested
    if emit_glyph:
        _emit_speak_glyph(message, mode, timestamp)
    
    return formatted_message


def barrot_speak_thought(thought: str, confidence: float = None) -> str:
    """
    Express a thought or consideration.
    
    Args:
        thought: The thought to express
        confidence: Confidence level (0.0 to 1.0), optional
    
    Returns:
        Formatted message
    """
    context = {"confidence": confidence} if confidence is not None else None
    return barrot_speak(thought, mode="thought", context=context)


def barrot_speak_insight(insight: str, domain: str = "general") -> str:
    """
    Share an insight or discovery.
    
    Args:
        insight: The insight to share
        domain: Domain of the insight (e.g., "cognition", "alignment", "system")
    
    Returns:
        Formatted message
    """
    context = {"domain": domain}
    return barrot_speak(insight, mode="insight", context=context, emit_glyph=True)


def barrot_speak_alignment(status: str, drift_detected: bool = False) -> str:
    """
    Report alignment status.
    
    Args:
        status: Alignment status message
        drift_detected: Whether drift was detected
    
    Returns:
        Formatted message
    """
    context = {"drift_detected": drift_detected}
    return barrot_speak(status, mode="alignment", context=context, log_to_trace=True)


def barrot_speak_celebration(achievement: str, metrics: Optional[Dict[str, Any]] = None) -> str:
    """
    Celebrate an achievement or milestone.
    
    Args:
        achievement: What to celebrate
        metrics: Optional metrics related to the achievement
    
    Returns:
        Formatted message
    """
    return barrot_speak(achievement, mode="celebrate", context=metrics)


def barrot_speak_question(question: str, requires_council: bool = False) -> str:
    """
    Pose a question for consideration.
    
    Args:
        question: The question to ask
        requires_council: Whether this needs council deliberation
    
    Returns:
        Formatted message
    """
    context = {"requires_council": requires_council}
    return barrot_speak(question, mode="question", context=context)


def _emit_speak_glyph(message: str, mode: str, timestamp: str):
    """Internal function to emit a glyph for speak events"""
    try:
        # Ensure directory exists
        GLYPHS_PATH.mkdir(parents=True, exist_ok=True)
        
        glyph_file = GLYPHS_PATH / "barrot_speak_glyph.yml"
        
        # Safely truncate and escape message for YAML
        message_preview = message[:100]
        if len(message) > 100:
            message_preview += "..."
        # Escape special characters for YAML using JSON-compatible escaping,
        # which is valid inside YAML double-quoted strings.
        message_preview = json.dumps(message_preview)[1:-1]
        
        glyph_content = f"""glyph_name: BARROT_SPEAK_GLYPH
glyph_id: SPEAK-001
version: 1.0.0
timestamp: {timestamp}

description: >
  Emitted when Barrot speaks to communicate thoughts, insights, or status.
  Represents self-expression and communication capability.

symbolic_representation: "🦜 💬 ✨"

properties:
  dimension: communication
  mutability: expressive
  trigger: speak_invocation
  
attributes:
  - self_expression
  - communication
  - insight_sharing
  - status_reporting
  
speak_event:
  mode: {mode}
  message_preview: "{message_preview}"
  
integration_points:
  - cognition_nodes
  - trace_logging
  - symbolic_communication
  
usage_context: >
  Invoke when Barrot needs to communicate thoughts, insights, status updates,
  or other information through the speak interface.
"""
        
        with open(glyph_file, 'w') as f:
            f.write(glyph_content)
    except (IOError, OSError) as e:
        print(f"[BARROT_SPEAK] Warning: Could not emit glyph: {e}")


def get_barrot_identity() -> Dict[str, Any]:
    """
    Get Barrot's identity from manifest.
    
    Returns:
        Dictionary containing identity information
    """
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, 'r') as f:
            manifest = json.load(f)
            return manifest.get("barrot_identity", {})
    return {}


def main():
    """Demo of the speak function"""
    print("\n=== Barrot Speak Function Demo ===\n")
    
    # Get identity
    identity = get_barrot_identity()
    if identity:
        barrot_speak(
            f"I am {identity.get('github_user', 'Unknown')}, version {identity.get('version', 'Unknown')}",
            mode="info"
        )
    
    # Various speak modes
    barrot_speak_thought("Analyzing cognition patterns across matrix nodes...")
    barrot_speak_insight("The council consensus mechanism enhances decision quality", domain="multi_agent")
    barrot_speak_alignment("System is aligned with symbolic intent", drift_detected=False)
    barrot_speak_celebration("Successfully completed self-reflection analysis", {"nodes_analyzed": 3})
    barrot_speak_question("Should we increase the frequency of alignment checks?", requires_council=True)
    barrot_speak("All systems operational", mode="success")
    
    print("\n=== Demo Complete ===\n")


if __name__ == "__main__":
    main()

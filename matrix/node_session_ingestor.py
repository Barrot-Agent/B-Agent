#!/usr/bin/env python3
"""
Node: Session Ingestor
Parses Copilot session transcripts, emits SESSION_TRACE_GLYPH,
and logs missed cognition events.
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
BUNDLES_PATH = REPO_ROOT / "memory-bundles"
GLYPHS_PATH = REPO_ROOT / "glyphs"
TRACE_LOG_PATH = BUNDLES_PATH / "TRACE_LOG.md"

def find_session_transcripts():
    """Find Copilot session transcript files"""
    # Look for session logs in memory-bundles
    transcripts = list(BUNDLES_PATH.glob("*session*.md"))
    transcripts.extend(BUNDLES_PATH.glob("*transcript*.md"))
    transcripts.extend(BUNDLES_PATH.glob("*copilot*.md"))
    return transcripts

def parse_transcript(transcript_path):
    """Parse a session transcript and extract key events"""
    if not transcript_path.exists():
        return {}
    
    with open(transcript_path, 'r') as f:
        content = f.read()
    
    data = {
        'timestamp': transcript_path.stat().st_mtime,
        'filename': transcript_path.name,
        'events': [],
        'cognition_events': [],
        'missed_events': []
    }
    
    # Parse for cognition-related events
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Look for cognition keywords
        if any(keyword in line.lower() for keyword in ['cognition', 'matrix', 'glyph', 'reflect', 'align']):
            data['cognition_events'].append({
                'line_number': i + 1,
                'content': line.strip(),
                'context': 'cognition_related'
            })
        
        # Look for decision points
        if any(keyword in line.lower() for keyword in ['decide', 'choose', 'select', 'determine']):
            data['events'].append({
                'line_number': i + 1,
                'content': line.strip(),
                'type': 'decision'
            })
    
    # Identify missed cognition events (events that should have triggered cognition but didn't)
    for event in data['cognition_events']:
        if 'should' in event['content'].lower() or 'need' in event['content'].lower():
            data['missed_events'].append(event)
    
    return data

def emit_glyph(transcript_data):
    """Emit SESSION_TRACE_GLYPH for ingested session"""
    glyph_file = GLYPHS_PATH / "session_trace_glyph.yml"
    
    glyph_content = f"""glyph_name: SESSION_TRACE_GLYPH
glyph_id: SESS-001
version: 1.0.0
timestamp: {datetime.utcnow().isoformat()}Z

description: >
  Emitted when a Copilot session transcript is ingested and analyzed.
  Captures session events, cognition triggers, and missed events for traceability.

symbolic_representation: "📝 ⟿ ✦"

properties:
  dimension: session_tracing
  mutability: archival
  trigger: transcript_ingestion
  
attributes:
  - session_capture
  - event_extraction
  - cognition_tracking
  - missed_event_detection
  
session_summary:
  total_events: {len(transcript_data.get('events', []))}
  cognition_events: {len(transcript_data.get('cognition_events', []))}
  missed_events: {len(transcript_data.get('missed_events', []))}
  
integration_points:
  - copilot_sessions
  - trace_logging
  - event_analysis
  
usage_context: >
  Invoke when ingesting and analyzing Copilot session transcripts to maintain
  complete traceability of cognition events and system interactions.
"""
    
    with open(glyph_file, 'w') as f:
        f.write(glyph_content)
    
    print(f"[SESSION_INGESTOR] Emitted SESSION_TRACE_GLYPH -> {glyph_file}")

def log_session_analysis(transcript_data):
    """Log session analysis to TRACE_LOG.md"""
    log_entry = f"""
## Session Ingestion: {datetime.utcnow().isoformat()}Z

**Transcript:** {transcript_data.get('filename', 'unknown')}

### Event Summary
- Total events: {len(transcript_data.get('events', []))}
- Cognition events: {len(transcript_data.get('cognition_events', []))}
- Missed events: {len(transcript_data.get('missed_events', []))}

### Missed Cognition Events
"""
    
    if transcript_data.get('missed_events'):
        for event in transcript_data['missed_events']:
            log_entry += f"- Line {event['line_number']}: {event['content']}\n"
    else:
        log_entry += "- None detected\n"
    
    log_entry += "\n---\n"
    
    # Append to trace log
    with open(TRACE_LOG_PATH, 'a') as f:
        f.write(log_entry)
    
    print(f"[SESSION_INGESTOR] Logged session analysis to TRACE_LOG.md")

def main():
    print("[SESSION_INGESTOR] Starting session transcript ingestion...")
    
    # Find transcripts
    transcripts = find_session_transcripts()
    
    if not transcripts:
        print("[SESSION_INGESTOR] No session transcripts found")
        # Still emit glyph for the ingestion attempt
        emit_glyph({'events': [], 'cognition_events': [], 'missed_events': []})
        return
    
    print(f"[SESSION_INGESTOR] Found {len(transcripts)} transcript(s)")
    
    # Process most recent transcript
    latest_transcript = max(transcripts, key=lambda p: p.stat().st_mtime)
    print(f"[SESSION_INGESTOR] Processing: {latest_transcript.name}")
    
    # Parse transcript
    transcript_data = parse_transcript(latest_transcript)
    
    # Report findings
    print(f"[SESSION_INGESTOR] Events found: {len(transcript_data['events'])}")
    print(f"[SESSION_INGESTOR] Cognition events: {len(transcript_data['cognition_events'])}")
    print(f"[SESSION_INGESTOR] Missed events: {len(transcript_data['missed_events'])}")
    
    # Emit glyph and log
    emit_glyph(transcript_data)
    log_session_analysis(transcript_data)

if __name__ == "__main__":
    main()

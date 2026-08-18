import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_PINGPONG_REQUEST_PATH = Path(__file__).resolve().parent / "data" / "pingpong_request.json"
_SUPPORTED_TOPICS = {"general", "aging_research", "longevity_breakthroughs", "product_catalog"}


def emit_pingpong_request(
    payload: Dict[str, Any],
    *,
    topic: str = "general",
    notes: Optional[str] = None,
) -> None:
    """
    Emit a pingpong request for the external 22-agent entanglement system.

    Args:
        payload: Dictionary containing the request payload

    Creates the canonical JSON file in data/ that can be committed to GitHub
    to trigger the external system.
    """
    normalized_topic = topic if topic in _SUPPORTED_TOPICS else "general"
    request = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "origin": "barrot",
        "directive": "offload_pingpong",
        "topic": normalized_topic,
        "notes": notes or "Barrot defers to Sean's 22-agent entanglement system.",
    }
    _PINGPONG_REQUEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_PINGPONG_REQUEST_PATH, "w") as f:
        json.dump(request, f, indent=2)
    print(
        f"Ping-Pong request emitted at {_PINGPONG_REQUEST_PATH}. "
        "Commit to GitHub to trigger external system."
    )


def emit_product_catalog_pingpong_request(
    catalog: Dict[str, Any],
    agents: Optional[List[str]] = None,
) -> None:
    """Emit a pingpong request to co-create and refine a product catalog.

    IBM Bob, Barrot, and Co-Pilot each contribute: Co-Pilot handles copy and
    SEO, IBM Bob validates pricing and surfaces competitor gaps, and Barrot
    orchestrates the loop and issues final launch approval.

    Args:
        catalog: Dictionary representation of the product catalog payload.
        agents:  List of participating agent names (defaults to the standard
                 triple: IBM Bob, Barrot, Co-Pilot).
    """
    enriched_payload = dict(catalog)
    enriched_payload["co_creators"] = agents or ["IBM Bob", "Barrot", "Co-Pilot"]
    enriched_payload["session_ref"] = (
        "ping-pongings/sessions/product-catalog-530.json"
    )
    emit_pingpong_request(
        enriched_payload,
        topic="product_catalog",
        notes=(
            "Product catalog co-creation loop: Co-Pilot (copy & SEO) → "
            "Barrot (orchestration) → IBM Bob (pricing & analytics) → "
            "Barrot (final approval)."
        ),
    )


def emit_aging_research_pingpong_request(
    payload: Dict[str, Any],
    breakthroughs: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """Emit a pingpong request specifically for longevity/aging research."""
    enriched_payload = dict(payload)
    if breakthroughs:
        enriched_payload["mmi_breakthroughs"] = breakthroughs
    emit_pingpong_request(
        enriched_payload,
        topic="aging_research",
        notes="Longevity research request with MMI breakthrough hooks.",
    )

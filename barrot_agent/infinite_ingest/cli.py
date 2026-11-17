"""Command line interface for the infinite-ingestion pipeline.

Examples::

    python -m barrot_agent.infinite_ingest.cli status
    python -m barrot_agent.infinite_ingest.cli seed --capability long_context_memory
    python -m barrot_agent.infinite_ingest.cli ingest --queue --capability long_context_memory
    python -m barrot_agent.infinite_ingest.cli connect
    python -m barrot_agent.infinite_ingest.cli refine --capability long_context_memory
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cross_analyzer import CrossAnalyzer
from .continuous import ContinuousRunner
from .ingestor import Ingestor
from .models import IngestItem
from .refiner import Refiner
from .sources import DEFAULT_SEARXNG_URL, SourceFetcher, searxng_search
from .storage import DEFAULT_DATA_ROOT, Store
from .transmuter import Transmuter


def _build(args) -> tuple[Store, Ingestor]:
    store = Store(Path(args.data_root))
    ingestor = Ingestor(store, SourceFetcher(min_interval=args.min_interval), max_ingests=args.max)
    return store, ingestor


def cmd_status(args) -> int:
    store = Store(Path(args.data_root))
    ledger = store.ledger()
    graph = store.load_connections()
    memory = store.load_memory()
    capabilities = sorted(path.stem for path in store.capability_dir.glob("*.json"))
    payload = {
        "data_root": str(store.root),
        "raw_bytes": store.raw_bytes(),
        "raw_cap_bytes": store.raw_cap_bytes,
        "ledger_urls": len(ledger),
        "queue": store.queue_size(),
        "memory_records": len(memory),
        "connections": graph.get("stats", {}),
        "capabilities": capabilities,
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_seed(args) -> int:
    store = Store(Path(args.data_root))
    capability = store.load_capability(args.capability)
    if not capability:
        print(f"unknown capability: {args.capability}")
        return 2
    items = [
        IngestItem(
            url=source["url"],
            kind=source.get("kind", "web"),
            title=source.get("title", ""),
            capability=args.capability,
            path=source.get("path", ""),
        )
        for source in capability.get("sources", [])
        if source.get("url")
    ]
    added = store.push_queue(items)
    print(f"queued {added} of {len(items)} sources for {args.capability}")
    return 0


def cmd_ingest(args) -> int:
    store, ingestor = _build(args)
    if args.url:
        report = ingestor.ingest_items(
            [
                IngestItem(
                    url=args.url,
                    kind=args.kind,
                    title=args.title,
                    capability=args.capability,
                    path=args.path,
                )
            ]
        )
    else:
        report = ingestor.ingest_queue(capability=args.capability)
    print(report.summary())
    for record in report.accepted:
        print(f"  {record.tag:4} {record.kind:10} {record.url} ({len(record.text)} chars)")
    for skipped in report.skipped:
        print(f"  skip {skipped['url']}: {skipped['reason']}")
    for failure in report.failed:
        print(f"  fail {failure['url']}: {failure['reason']}")
    if args.transmute:
        transmuter = Transmuter()
        written = 0
        for record in report.accepted:
            records = transmuter.transmute(record, capability=args.capability)
            written += len(store.append_memory(records))
        print(f"transmuted into {written} new memory records")
    return 0


def cmd_discover(args) -> int:
    store = Store(Path(args.data_root))
    found = searxng_search(
        args.query,
        base_url=args.searxng,
        limit=args.limit,
        kind=args.kind,
    )
    items = [
        IngestItem(
            url=item.url,
            kind=item.kind,
            title=item.title,
            capability=args.capability,
        )
        for item in found
    ]
    added = store.push_queue(items)
    print(f"discovered {len(found)} results, queued {added} new sources")
    for item in items[:10]:
        print(f"  {item.kind:10} {item.url}")
    return 0


def cmd_connect(args) -> int:
    store = Store(Path(args.data_root))
    graph = CrossAnalyzer(store).build()
    print(json.dumps(graph.get("stats", {}), indent=2))
    for suggestion in graph.get("suggestions", [])[:5]:
        print(f"  hypothesis: {suggestion['hypothesis']}")
    return 0


def cmd_refine(args) -> int:
    store, ingestor = _build(args)
    refiner = Refiner(store, ingestor, Transmuter(), CrossAnalyzer(store))
    result = refiner.run_once(args.capability, run_id=args.run_id)
    print(f"before: {result.before.summary()}")
    print(f"after:  {result.after.summary()}")
    print(result.summary())
    for source in result.sources:
        print(f"  source {source['tag']:4} {source['url']} @ {source['fetched_at']}")
    return 0


def cmd_continuous(args) -> int:
    store, ingestor = _build(args)
    runner = ContinuousRunner(
        store,
        ingestor,
        transmute=not args.no_transmute,
        refine=not args.no_refine,
    )
    report = runner.run(
        cycles=args.cycles,
        max_minutes=args.minutes,
        capability=args.capability,
        idle_cycles=args.idle_cycles,
    )
    print(report.summary())
    for cycle in report.cycles:
        print(json.dumps(cycle.as_dict(), ensure_ascii=False))
    from ..phoenix import Phoenix

    state = Phoenix(store=store).record_continuous(
        {
            "command": "python -m barrot_agent.infinite_ingest.cli continuous",
            "capability": args.capability,
            "cycles": args.cycles,
            "max_minutes": args.minutes,
            "max_ingests_per_run": args.max,
            "last_run": report.as_dict(),
        }
    )
    print(json.dumps(state, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Infinite ingestion + transmutation")
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    parser.add_argument("--max", type=int, default=10, help="max ingests per run")
    parser.add_argument("--min-interval", type=float, default=1.5, help="seconds per host")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show pipeline state").set_defaults(func=cmd_status)

    seed = sub.add_parser("seed", help="queue a capability's declared sources")
    seed.add_argument("--capability", required=True)
    seed.set_defaults(func=cmd_seed)

    ingest = sub.add_parser("ingest", help="ingest one URL or drain the queue")
    ingest.add_argument("--url")
    ingest.add_argument("--kind", default="auto")
    ingest.add_argument("--title", default="")
    ingest.add_argument("--path", default="", help="local file instead of the network")
    ingest.add_argument("--capability", default="")
    ingest.add_argument("--transmute", action="store_true")
    ingest.set_defaults(func=cmd_ingest)

    discover = sub.add_parser("discover", help="queue sources found by SearXNG")
    discover.add_argument("--query", required=True)
    discover.add_argument("--kind", default="", help="filter by inferred kind")
    discover.add_argument("--limit", type=int, default=10)
    discover.add_argument("--searxng", default=DEFAULT_SEARXNG_URL)
    discover.add_argument("--capability", default="")
    discover.set_defaults(func=cmd_discover)

    connect = sub.add_parser("connect", help="rebuild data/connections.json")
    connect.set_defaults(func=cmd_connect)

    refine = sub.add_parser("refine", help="run one refinement for one capability")
    refine.add_argument("--capability", required=True)
    refine.add_argument("--run-id", default=None)
    refine.set_defaults(func=cmd_refine)

    continuous = sub.add_parser(
        "continuous", help="bounded ingest -> transmute -> connect -> refine cycles"
    )
    continuous.add_argument("--cycles", type=int, default=2)
    continuous.add_argument("--minutes", type=float, default=10.0)
    continuous.add_argument("--idle-cycles", type=int, default=2)
    continuous.add_argument("--capability", default="")
    continuous.add_argument("--no-transmute", action="store_true")
    continuous.add_argument("--no-refine", action="store_true")
    continuous.set_defaults(func=cmd_continuous)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

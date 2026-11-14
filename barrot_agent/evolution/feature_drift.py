"""Point-in-time univariate feature-distribution drift monitoring for XRP.

The monitor is diagnostic only. It never authorizes a forecast or trade.
Reference-window records must have been available by the reference cutoff;
late backfills are excluded rather than backdated.
"""
from __future__ import annotations

import hashlib
import json
import math
from bisect import bisect_right
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping

from .point_in_time_features import FeatureSnapshotError, validate_feature_record

MONITOR_VERSION = "xrp-feature-drift-v1"
DRIFT_REPORT_RETENTION_DAYS = 90
_DEFAULT_WARNING_PSI = 0.10
_DEFAULT_DRIFT_PSI = 0.25


class FeatureDriftError(ValueError):
    """A feature-drift input or monitoring configuration is invalid."""


def _utc(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise FeatureDriftError(f"{field} must be a timezone-aware ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise FeatureDriftError(f"{field} is not valid ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise FeatureDriftError(f"{field} must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _available_at(record: Mapping[str, Any]) -> datetime:
    fields = (
        "known_at_utc",
        "source_data_as_of_utc",
        "ingested_at_utc",
        "revision_available_at_utc",
    )
    return max(_utc(record.get(field), field) for field in fields)


def _psi(reference: list[float], current: list[float], bin_count: int) -> tuple[float, int]:
    ordered = sorted(reference)
    low, high = ordered[0], ordered[-1]
    unique_count = len(set(ordered))
    if unique_count >= bin_count:
        edges = []
        for index in range(1, bin_count):
            quantile_index = min(len(ordered) - 2, max(0, math.ceil(index * len(ordered) / bin_count) - 1))
            edges.append(ordered[quantile_index])
        edges = sorted(set(edges))
    else:
        if high <= low:
            spread = max(abs(low) * 0.02, 1e-9)
            low -= spread / 2
            high += spread / 2
        edges = [low + (high - low) * index / bin_count for index in range(1, bin_count)]
        edges = sorted(set(edges))

    actual_bins = len(edges) + 1
    ref_counts = [0] * actual_bins
    cur_counts = [0] * actual_bins
    for value in reference:
        ref_counts[bisect_right(edges, value)] += 1
    for value in current:
        cur_counts[bisect_right(edges, value)] += 1

    epsilon = 1e-6
    ref_total = len(reference) + epsilon * actual_bins
    cur_total = len(current) + epsilon * actual_bins
    score = 0.0
    for ref_count, cur_count in zip(ref_counts, cur_counts):
        ref_share = (ref_count + epsilon) / ref_total
        cur_share = (cur_count + epsilon) / cur_total
        score += (cur_share - ref_share) * math.log(cur_share / ref_share)
    return score, actual_bins


def _categorical_psi(reference: Counter[str], current: Counter[str]) -> float | None:
    categories = sorted(set(reference) | set(current))
    if not categories:
        return None
    epsilon = 1e-6
    ref_total = sum(reference.values()) + epsilon * len(categories)
    cur_total = sum(current.values()) + epsilon * len(categories)
    score = 0.0
    for category in categories:
        ref_share = (reference.get(category, 0) + epsilon) / ref_total
        cur_share = (current.get(category, 0) + epsilon) / cur_total
        score += (cur_share - ref_share) * math.log(cur_share / ref_share)
    return score


def _groups(record: Mapping[str, Any]) -> list[str]:
    groups = record.get("source_independence_groups")
    if isinstance(groups, list) and groups:
        return sorted({str(group) for group in groups if str(group).strip()})
    sources = record.get("sources", [])
    if isinstance(sources, list):
        return sorted({
            str(source.get("independence_group"))
            for source in sources
            if isinstance(source, Mapping) and source.get("independence_group")
        })
    return []


def _dimensions(record: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(
        record.get(field)
        for field in (
            "asset",
            "unit",
            "venue",
            "instrument",
            "currency_pair",
            "market_type",
            "aggregation_window",
            "feature_version",
        )
    )


def monitor_feature_drift(
    records: Iterable[Mapping[str, Any]],
    *,
    cutoff_utc: str,
    reference_days: int = 30,
    current_days: int = 7,
    min_samples_per_window: int = 30,
    bin_count: int = 10,
    warning_psi: float = _DEFAULT_WARNING_PSI,
    drift_psi: float = _DEFAULT_DRIFT_PSI,
) -> dict[str, Any]:
    """Compare non-overlapping, availability-safe reference/current feature windows.

    PSI thresholds are provisional operational heuristics. This is univariate
    feature-distribution monitoring, not label/concept-drift detection.
    """
    cutoff = _utc(cutoff_utc, "cutoff_utc")
    for name, value in (
        ("reference_days", reference_days),
        ("current_days", current_days),
        ("min_samples_per_window", min_samples_per_window),
    ):
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise FeatureDriftError(f"{name} must be a positive integer")
    if isinstance(bin_count, bool) or not isinstance(bin_count, int) or bin_count < 2:
        raise FeatureDriftError("bin_count must be an integer of at least two")
    if (
        isinstance(warning_psi, bool)
        or isinstance(drift_psi, bool)
        or not isinstance(warning_psi, (int, float))
        or not isinstance(drift_psi, (int, float))
        or not math.isfinite(float(warning_psi))
        or not math.isfinite(float(drift_psi))
        or warning_psi < 0
        or drift_psi <= warning_psi
    ):
        raise FeatureDriftError("PSI thresholds must be finite with 0 <= warning_psi < drift_psi")

    current_start = cutoff - timedelta(days=current_days)
    reference_end = current_start
    reference_start = reference_end - timedelta(days=reference_days)
    buckets: dict[str, dict[str, list[dict[str, Any]]]] = {}
    input_count = 0
    excluded_ineligible = 0
    late_reference = 0
    future_events = 0

    for raw in records:
        input_count += 1
        if not isinstance(raw, Mapping):
            raise FeatureDriftError("each feature record must be a mapping")
        try:
            checked = validate_feature_record(
                raw,
                _iso(cutoff),
                captured_at_utc=_iso(cutoff),
            )
        except FeatureSnapshotError as exc:
            raise FeatureDriftError(f"invalid point-in-time feature record: {exc}") from exc
        if not checked["eligible"]:
            excluded_ineligible += 1
            continue

        record = checked["record"]
        event_time = _utc(record["event_time_utc"], "event_time_utc")
        available_at = _available_at(record)
        if event_time > cutoff:
            future_events += 1
            continue
        feature_id = record["feature_id"]
        feature = buckets.setdefault(feature_id, {"reference": [], "current": []})
        if reference_start <= event_time < reference_end:
            if available_at <= reference_end:
                feature["reference"].append(record)
            else:
                late_reference += 1
        elif current_start <= event_time <= cutoff and available_at <= cutoff:
            feature["current"].append(record)

    feature_results = []
    for feature_id in sorted(buckets):
        reference_records = buckets[feature_id]["reference"]
        current_records = buckets[feature_id]["current"]
        result: dict[str, Any] = {
            "feature_id": feature_id,
            "reference_sample_count": len(reference_records),
            "current_sample_count": len(current_records),
            "psi": None,
            "source_mix_psi": None,
            "mean_shift_reference_standard_deviations": None,
            "status": "INSUFFICIENT_DATA",
        }
        if (
            len(reference_records) < min_samples_per_window
            or len(current_records) < min_samples_per_window
        ):
            feature_results.append(result)
            continue

        all_records = reference_records + current_records
        if len({_dimensions(record) for record in all_records}) != 1:
            result["status"] = "DIMENSION_MISMATCH"
            feature_results.append(result)
            continue
        values = [record["value"] for record in all_records]
        if any(
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
            for value in values
        ):
            result["status"] = "UNSUPPORTED_NON_NUMERIC"
            feature_results.append(result)
            continue

        reference_values = [float(record["value"]) for record in reference_records]
        current_values = [float(record["value"]) for record in current_records]
        psi, actual_bins = _psi(reference_values, current_values, bin_count)
        reference_mean = math.fsum(reference_values) / len(reference_values)
        current_mean = math.fsum(current_values) / len(current_values)
        reference_variance = math.fsum(
            (value - reference_mean) ** 2 for value in reference_values
        ) / len(reference_values)
        reference_std = math.sqrt(reference_variance)
        mean_shift = (
            (current_mean - reference_mean) / reference_std
            if reference_std > 1e-12
            else None
        )
        reference_groups = Counter(
            group for record in reference_records for group in _groups(record)
        )
        current_groups = Counter(
            group for record in current_records for group in _groups(record)
        )
        source_mix_psi = _categorical_psi(reference_groups, current_groups)
        maximum_psi = max(psi, source_mix_psi or 0.0)
        if maximum_psi >= drift_psi:
            status = "DRIFT"
        elif maximum_psi >= warning_psi:
            status = "WARNING"
        else:
            status = "STABLE"
        result.update(
            {
                "psi": psi,
                "psi_bin_count": actual_bins,
                "source_mix_psi": source_mix_psi,
                "mean_shift_reference_standard_deviations": mean_shift,
                "reference_mean": reference_mean,
                "current_mean": current_mean,
                "reference_source_group_counts": dict(sorted(reference_groups.items())),
                "current_source_group_counts": dict(sorted(current_groups.items())),
                "status": status,
            }
        )
        feature_results.append(result)

    statuses = [item["status"] for item in feature_results]
    if "DRIFT" in statuses:
        overall = "DRIFT"
    elif "WARNING" in statuses:
        overall = "WARNING"
    elif statuses and all(status == "STABLE" for status in statuses):
        overall = "STABLE"
    else:
        overall = "INSUFFICIENT_DATA"

    report: dict[str, Any] = {
        "schema_version": 1,
        "artifact_type": "xrp_point_in_time_feature_drift_report",
        "monitor_version": MONITOR_VERSION,
        "captured_at_utc": _iso(cutoff),
        "data_cutoff_utc": _iso(cutoff),
        "reference_window": {
            "start_utc": _iso(reference_start),
            "end_exclusive_utc": _iso(reference_end),
        },
        "current_window": {
            "start_utc": _iso(current_start),
            "end_inclusive_utc": _iso(cutoff),
        },
        "minimum_samples_per_window": min_samples_per_window,
        "thresholds": {
            "warning_psi": float(warning_psi),
            "drift_psi": float(drift_psi),
            "bin_count": bin_count,
        },
        "input_record_count": input_count,
        "excluded_ineligible_record_count": excluded_ineligible,
        "late_reference_record_exclusion_count": late_reference,
        "future_event_exclusion_count": future_events,
        "feature_count": len(feature_results),
        "evaluated_feature_count": sum(item["status"] in {"STABLE", "WARNING", "DRIFT"} for item in feature_results),
        "feature_results": feature_results,
        "status": overall,
        "model_eligible": False,
        "forecast_issuance_allowed": False,
        "limitations": [
            "Population Stability Index is a univariate feature-distribution diagnostic, not a test of label drift, concept drift, causal change or feature interactions.",
            "PSI thresholds are provisional operational heuristics and require validation against historical XRP regime changes.",
            "Reference-window records are admitted only when known, source-as-of, ingested and revision-available timestamps are all no later than the reference-window end; later backfills are excluded.",
            "A STABLE result does not establish model accuracy, probability calibration, out-of-sample lift, shadow performance or permission to issue forecasts.",
        ],
    }
    report["report_sha256"] = _canonical_hash(report)
    return report

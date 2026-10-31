"""Append-only, fixed-horizon XRP forecast and outcome evaluation.

Forecasts and outcomes are stored separately. The module never fetches market
data, changes an issued forecast, or claims descriptive metrics are skill.
Appends and consistent reads are serialized with an OS-level lock.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
import math
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping

CLASSES = ("up", "flat", "down")
TIE_BREAK_ORDER = ("flat", "up", "down")
PROBABILITY_TOLERANCE = 1e-6
LOG_EPSILON = 1e-15


def _parse_utc(value: str, field: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty ISO-8601 timestamp")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _format_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _positive_number(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a finite positive number") from exc
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{field} must be a finite positive number")
    return number


def _probabilities(value: Any, field: str) -> dict[str, float]:
    if not isinstance(value, Mapping) or set(value) != set(CLASSES):
        raise ValueError(f"{field} must contain exactly {', '.join(CLASSES)}")
    result: dict[str, float] = {}
    for label in CLASSES:
        try:
            probability = float(value[label])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{field}.{label} must be a probability") from exc
        if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError(f"{field}.{label} must be between zero and one")
        result[label] = probability
    if abs(sum(result.values()) - 1.0) > PROBABILITY_TOLERANCE:
        raise ValueError(f"{field} probabilities must sum to one")
    return result


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{field} entries must be non-empty strings")
    return [item.strip() for item in value]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL record in {path} at line {line_number}") from exc
        if not isinstance(record, dict):
            raise ValueError(f"JSONL record in {path} at line {line_number} must be an object")
        records.append(record)
    return records


@contextmanager
def _ledger_lock(directory: Path) -> Iterator[None]:
    """Serialize ledger readers and writers across processes on a local filesystem."""
    directory.mkdir(parents=True, exist_ok=True)
    lock_path = directory / ".forecast-ledger.lock"
    descriptor = os.open(
        str(lock_path),
        os.O_CREAT | os.O_RDWR | getattr(os, "O_BINARY", 0),
        0o600,
    )
    try:
        try:
            import fcntl
        except ImportError:
            try:
                import msvcrt
            except ImportError as exc:
                raise RuntimeError("No supported operating-system file-lock API is available") from exc
            if os.fstat(descriptor).st_size == 0:
                os.write(descriptor, b"\0")
            os.lseek(descriptor, 0, os.SEEK_SET)
            msvcrt.locking(descriptor, msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                os.lseek(descriptor, 0, os.SEEK_SET)
                msvcrt.locking(descriptor, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def _append_jsonl(path: Path, record: dict[str, Any], duplicate_message: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (
        json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode("utf-8")
    forecast_id = record.get("forecast_id")
    if not isinstance(forecast_id, str) or not forecast_id:
        raise ValueError("forecast_id is required for append-only ledger records")
    with _ledger_lock(path.parent):
        if any(item.get("forecast_id") == forecast_id for item in _read_jsonl(path)):
            raise ValueError(duplicate_message)
        descriptor = os.open(
            str(path),
            os.O_CREAT | os.O_APPEND | os.O_WRONLY | getattr(os, "O_BINARY", 0),
            0o600,
        )
        try:
            offset = 0
            while offset < len(payload):
                written = os.write(descriptor, payload[offset:])
                if written <= 0:
                    raise OSError("Short append while writing the forecast ledger")
                offset += written
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

class ForecastLedger:
    """Persist immutable forecasts and separate, timestamped outcomes."""

    def __init__(
        self,
        root: str | Path | None = None,
        max_observation_lag_seconds: int = 900,
        max_issue_price_lag_seconds: int = 120,
        source_registry: Iterable[str] | None = None,
    ) -> None:
        if (
            isinstance(max_observation_lag_seconds, bool)
            or not isinstance(max_observation_lag_seconds, int)
            or max_observation_lag_seconds <= 0
        ):
            raise ValueError("max_observation_lag_seconds must be a positive integer")
        self.root = Path(root) if root is not None else Path("data/xrp_forecasts")
        self.forecasts_path = self.root / "forecasts.jsonl"
        self.outcomes_path = self.root / "outcomes.jsonl"
        self.max_observation_lag_seconds = int(max_observation_lag_seconds)
        if (
            isinstance(max_issue_price_lag_seconds, bool)
            or not isinstance(max_issue_price_lag_seconds, int)
            or max_issue_price_lag_seconds <= 0
        ):
            raise ValueError("max_issue_price_lag_seconds must be a positive integer")
        self.max_issue_price_lag_seconds = int(max_issue_price_lag_seconds)
        if source_registry is None:
            self.source_registry: frozenset[str] | None = None
        else:
            if isinstance(source_registry, (str, bytes)):
                raise ValueError("source_registry must be an iterable of source IDs")
            try:
                registry_values = list(source_registry)
            except TypeError as exc:
                raise ValueError("source_registry must be an iterable of source IDs") from exc
            if any(not isinstance(item, str) or not item.strip() for item in registry_values):
                raise ValueError("source_registry entries must be non-empty strings")
            self.source_registry = frozenset(item.strip() for item in registry_values)

    def forecasts(self) -> list[dict[str, Any]]:
        with _ledger_lock(self.root):
            return _read_jsonl(self.forecasts_path)

    def outcomes(self) -> list[dict[str, Any]]:
        with _ledger_lock(self.root):
            return _read_jsonl(self.outcomes_path)

    def append_forecast(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("forecast payload must be an object")
        forecast_id = payload.get("forecast_id")
        if not isinstance(forecast_id, str) or not forecast_id.strip():
            raise ValueError("forecast_id is required")
        forecast_id = forecast_id.strip()
        if any(item.get("forecast_id") == forecast_id for item in self.forecasts()):
            raise ValueError(f"forecast_id already exists: {forecast_id}")

        asset_pair = payload.get("asset_pair", "XRP/USD")
        if asset_pair != "XRP/USD":
            raise ValueError("this ledger currently accepts only XRP/USD forecasts")
        issued = _parse_utc(payload.get("issued_at_utc"), "issued_at_utc")
        cutoff = _parse_utc(payload.get("data_cutoff_utc"), "data_cutoff_utc")
        if cutoff > issued:
            raise ValueError("data_cutoff_utc cannot be later than issued_at_utc")

        horizon = payload.get("horizon_seconds")
        if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon <= 0:
            raise ValueError("horizon_seconds must be a positive integer")
        target_end = issued + timedelta(seconds=horizon)
        supplied_target_end = payload.get("target_end_at_utc")
        if supplied_target_end is not None:
            if _parse_utc(supplied_target_end, "target_end_at_utc") != target_end:
                raise ValueError("target_end_at_utc must equal issued_at_utc plus horizon_seconds")

        target = payload.get("target")
        if not isinstance(target, Mapping) or target.get("name") != "xrp_usd_return_class_v1":
            raise ValueError("target.name must be xrp_usd_return_class_v1")
        try:
            up_threshold = float(target.get("up_threshold_pct"))
            down_threshold = float(target.get("down_threshold_pct"))
        except (TypeError, ValueError) as exc:
            raise ValueError("target thresholds must be numeric") from exc
        if not math.isfinite(up_threshold) or not math.isfinite(down_threshold):
            raise ValueError("target thresholds must be finite")
        if up_threshold <= 0 or down_threshold >= 0 or down_threshold >= up_threshold:
            raise ValueError("up threshold must be positive and down threshold negative")

        probabilities = _probabilities(payload.get("probabilities"), "probabilities")
        confidence = max(probabilities.values())
        supplied_confidence = payload.get("confidence")
        if supplied_confidence is not None:
            try:
                supplied_confidence = float(supplied_confidence)
            except (TypeError, ValueError) as exc:
                raise ValueError("confidence must equal the maximum class probability") from exc
            if not math.isfinite(supplied_confidence) or abs(supplied_confidence - confidence) > PROBABILITY_TOLERANCE:
                raise ValueError("confidence must equal the maximum class probability")

        model = payload.get("model")
        if not isinstance(model, Mapping):
            raise ValueError("model metadata is required")
        model_name = model.get("name")
        model_version = model.get("version")
        if not all(isinstance(item, str) and item.strip() for item in (model_name, model_version)):
            raise ValueError("model name and version are required")

        feature = payload.get("feature_snapshot")
        if not isinstance(feature, Mapping):
            raise ValueError("feature_snapshot metadata is required")
        feature_id = feature.get("snapshot_id")
        feature_hash = feature.get("sha256")
        if not isinstance(feature_id, str) or not feature_id.strip():
            raise ValueError("feature_snapshot.snapshot_id is required")
        if not isinstance(feature_hash, str) or len(feature_hash) != 64:
            raise ValueError("feature_snapshot.sha256 must be a 64-character SHA-256 hex digest")
        try:
            int(feature_hash, 16)
        except ValueError as exc:
            raise ValueError("feature_snapshot.sha256 must be hexadecimal") from exc
        feature_captured = _parse_utc(
            feature.get("captured_at_utc"), "feature_snapshot.captured_at_utc"
        )
        if feature_captured > cutoff:
            raise ValueError("feature snapshot cannot be captured after the data cutoff")

        baseline = payload.get("baseline")
        if not isinstance(baseline, Mapping):
            raise ValueError("a point-in-time baseline is required")
        baseline_id = baseline.get("id")
        if not isinstance(baseline_id, str) or not baseline_id.strip():
            raise ValueError("baseline.id is required")
        baseline_trained_through = _parse_utc(
            baseline.get("trained_through_utc"), "baseline.trained_through_utc"
        )
        baseline_computed_at = _parse_utc(
            baseline.get("computed_at_utc"), "baseline.computed_at_utc"
        )
        if baseline_trained_through > cutoff:
            raise ValueError("baseline cannot use information after the data cutoff")
        if baseline_trained_through > baseline_computed_at:
            raise ValueError(
                "baseline cannot be trained through a time later than it was computed"
            )
        if baseline_computed_at > issued or baseline_computed_at > cutoff:
            raise ValueError("baseline must be computed no later than the forecast data cutoff")
        baseline_probabilities = _probabilities(
            baseline.get("probabilities"), "baseline.probabilities"
        )

        assumptions = _string_list(payload.get("assumptions"), "assumptions")
        alternatives = _string_list(payload.get("alternatives"), "alternatives")
        source_ids = _string_list(payload.get("source_ids"), "source_ids")
        if len(set(source_ids)) != len(source_ids):
            raise ValueError("source_ids must be unique")
        source_registry_status = "NOT_CHECKED"
        if self.source_registry is not None:
            missing_source_ids = sorted(set(source_ids) - self.source_registry)
            if missing_source_ids:
                raise ValueError(f"source_ids are not registered: {missing_source_ids}")
            source_registry_status = "REGISTERED"
        price_source_id = payload.get("price_at_issue_source_id")
        if not isinstance(price_source_id, str) or not price_source_id.strip():
            raise ValueError("price_at_issue_source_id is required")
        price_source_id = price_source_id.strip()
        if price_source_id not in source_ids:
            raise ValueError("price_at_issue_source_id must be included in source_ids")
        price_observed_at = _parse_utc(
            payload.get("price_at_issue_observed_at_utc"), "price_at_issue_observed_at_utc"
        )
        if price_observed_at > cutoff or price_observed_at > issued:
            raise ValueError("issue price observation cannot be later than the data cutoff")
        if issued - price_observed_at > timedelta(seconds=self.max_issue_price_lag_seconds):
            raise ValueError("issue price observation exceeds the configured freshness window")
        price_at_issue = _positive_number(payload.get("price_at_issue_usd"), "price_at_issue_usd")

        record = {
            "schema_version": "1.1",
            "record_type": "xrp_forecast",
            "forecast_id": forecast_id,
            "asset_pair": asset_pair,
            "issued_at_utc": _format_utc(issued),
            "data_cutoff_utc": _format_utc(cutoff),
            "horizon_seconds": horizon,
            "target_start_at_utc": _format_utc(issued),
            "target_end_at_utc": _format_utc(target_end),
            "target_resolution_policy": "LATEST_OBSERVATION_AT_OR_BEFORE_HORIZON",
            "max_pre_horizon_observation_lag_seconds": self.max_observation_lag_seconds,
            "target": {
                "name": "xrp_usd_return_class_v1",
                "up_threshold_pct": up_threshold,
                "down_threshold_pct": down_threshold,
            },
            "probabilities": probabilities,
            "confidence": confidence,
            "assumptions": assumptions,
            "alternatives": alternatives,
            "model": {"name": model_name.strip(), "version": model_version.strip()},
            "feature_snapshot": {
                "snapshot_id": feature_id.strip(),
                "sha256": feature_hash.lower(),
                "captured_at_utc": _format_utc(feature_captured),
            },
            "baseline": {
                "id": baseline_id.strip(),
                "trained_through_utc": _format_utc(baseline_trained_through),
                "computed_at_utc": _format_utc(baseline_computed_at),
                "probabilities": baseline_probabilities,
            },
            "source_ids": source_ids,
            "source_registry_status": source_registry_status,
            "price_at_issue_usd": price_at_issue,
            "price_at_issue_source_id": price_source_id,
            "price_at_issue_observed_at_utc": _format_utc(price_observed_at),
            "price_at_issue_max_observation_lag_seconds": self.max_issue_price_lag_seconds,
            "status": "OPEN",
        }
        _append_jsonl(
            self.forecasts_path,
            record,
            f"forecast_id already exists: {forecast_id}",
        )
        return record

    def append_outcome(
        self,
        forecast_id: str,
        price_at_horizon_usd: float,
        price_observed_at_utc: str,
        outcome_recorded_at_utc: str,
        price_source_id: str,
    ) -> dict[str, Any]:
        forecasts = self.forecasts()
        matches = [item for item in forecasts if item.get("forecast_id") == forecast_id]
        if len(matches) != 1:
            raise ValueError("exactly one matching forecast is required")
        if any(item.get("forecast_id") == forecast_id for item in self.outcomes()):
            raise ValueError(f"an outcome already exists for forecast_id: {forecast_id}")

        forecast = matches[0]
        observed_at = _parse_utc(price_observed_at_utc, "price_observed_at_utc")
        recorded_at = _parse_utc(outcome_recorded_at_utc, "outcome_recorded_at_utc")
        target_end = _parse_utc(forecast["target_end_at_utc"], "target_end_at_utc")
        issued_at = _parse_utc(forecast["issued_at_utc"], "issued_at_utc")
        if observed_at < issued_at:
            raise ValueError("outcome price timestamp cannot precede forecast issuance")
        if observed_at > target_end:
            raise ValueError("outcome price timestamp cannot be after the fixed horizon")
        observation_lag = (target_end - observed_at).total_seconds()
        if observation_lag > self.max_observation_lag_seconds:
            raise ValueError("outcome price timestamp exceeds the maximum pre-horizon observation lag")
        if recorded_at < target_end:
            raise ValueError("outcome_recorded_at_utc cannot precede the fixed horizon")
        if recorded_at < observed_at:
            raise ValueError("outcome_recorded_at_utc cannot precede the price observation")
        effective_horizon_seconds = (observed_at - issued_at).total_seconds()
        if not isinstance(price_source_id, str) or not price_source_id.strip():
            raise ValueError("price_source_id is required")
        price_source_id = price_source_id.strip()
        price_source_registry_status = "NOT_CHECKED"
        if self.source_registry is not None:
            if price_source_id not in self.source_registry:
                raise ValueError(f"price_source_id is not registered: {price_source_id}")
            price_source_registry_status = "REGISTERED"

        price_at_horizon = _positive_number(price_at_horizon_usd, "price_at_horizon_usd")
        price_at_issue = float(forecast["price_at_issue_usd"])
        realized_return = (price_at_horizon / price_at_issue - 1.0) * 100.0
        target = forecast["target"]
        if realized_return > float(target["up_threshold_pct"]):
            realized_class = "up"
        elif realized_return < float(target["down_threshold_pct"]):
            realized_class = "down"
        else:
            realized_class = "flat"

        record = {
            "schema_version": "1.1",
            "record_type": "xrp_forecast_outcome",
            "forecast_id": forecast_id,
            "target_end_at_utc": _format_utc(target_end),
            "target_resolution_policy": "LATEST_OBSERVATION_AT_OR_BEFORE_HORIZON",
            "effective_horizon_seconds": effective_horizon_seconds,
            "observation_lag_seconds": observation_lag,
            "price_at_issue_usd": price_at_issue,
            "price_at_horizon_usd": price_at_horizon,
            "price_observed_at_utc": _format_utc(observed_at),
            "outcome_recorded_at_utc": _format_utc(recorded_at),
            "price_source_id": price_source_id,
            "price_source_registry_status": price_source_registry_status,
            "realized_return_pct": realized_return,
            "realized_class": realized_class,
        }
        _append_jsonl(
            self.outcomes_path,
            record,
            f"an outcome already exists for forecast_id: {forecast_id}",
        )
        return record

    def metrics(self) -> dict[str, Any]:
        with _ledger_lock(self.root):
            forecasts = _read_jsonl(self.forecasts_path)
            outcomes = _read_jsonl(self.outcomes_path)
        by_id = {item["forecast_id"]: item for item in forecasts}
        if len(by_id) != len(forecasts):
            raise ValueError("duplicate forecast IDs found in the immutable forecast ledger")
        outcome_by_id: dict[str, dict[str, Any]] = {}
        for outcome in outcomes:
            forecast_id = outcome.get("forecast_id")
            if forecast_id not in by_id:
                raise ValueError("outcome references an unknown forecast")
            if forecast_id in outcome_by_id:
                raise ValueError("duplicate outcomes found for a forecast")
            outcome_by_id[forecast_id] = outcome

        resolved = [(by_id[key], value) for key, value in outcome_by_id.items()]
        pending_count = len(forecasts) - len(resolved)
        if not resolved:
            return {
                "forecast_count": len(forecasts),
                "resolved_count": 0,
                "pending_count": pending_count,
                "accuracy": None,
                "mean_brier_score": None,
                "mean_log_loss": None,
                "mean_baseline_brier_score": None,
                "mean_baseline_log_loss": None,
                "brier_skill_score": None,
                "mean_entropy_nats": None,
                "top_label_calibration_bins": [],
                "top_label_tie_break_order": list(TIE_BREAK_ORDER),
                "walk_forward_baseline_status": "NO_RESOLVED_OUTCOMES",
                "performance_claim_status": "NOT_AUTHORIZED",
            }

        correct = 0
        brier_scores: list[float] = []
        log_losses: list[float] = []
        baseline_brier_scores: list[float] = []
        baseline_log_losses: list[float] = []
        entropies: list[float] = []
        bins: dict[int, list[tuple[float, bool]]] = {}

        for forecast, outcome in resolved:
            probabilities = forecast["probabilities"]
            baseline_probabilities = forecast["baseline"]["probabilities"]
            realized_class = outcome["realized_class"]
            predicted_class = max(TIE_BREAK_ORDER, key=lambda label: probabilities[label])
            is_correct = predicted_class == realized_class
            correct += int(is_correct)
            brier_scores.append(
                sum((probabilities[label] - float(label == realized_class)) ** 2 for label in CLASSES)
            )
            baseline_brier_scores.append(
                sum(
                    (baseline_probabilities[label] - float(label == realized_class)) ** 2
                    for label in CLASSES
                )
            )
            log_losses.append(-math.log(max(LOG_EPSILON, probabilities[realized_class])))
            baseline_log_losses.append(
                -math.log(max(LOG_EPSILON, baseline_probabilities[realized_class]))
            )
            entropies.append(
                -sum(
                    probability * math.log(probability)
                    for probability in probabilities.values()
                    if probability > 0
                )
            )
            confidence = max(probabilities.values())
            bin_index = min(int(confidence * 10), 9)
            bins.setdefault(bin_index, []).append((confidence, is_correct))

        mean_brier = sum(brier_scores) / len(brier_scores)
        mean_baseline_brier = sum(baseline_brier_scores) / len(baseline_brier_scores)
        calibration = []
        for index in sorted(bins):
            values = bins[index]
            calibration.append(
                {
                    "bin": f"{index / 10:.1f}-{(index + 1) / 10:.1f}",
                    "count": len(values),
                    "mean_confidence": sum(value[0] for value in values) / len(values),
                    "accuracy": sum(int(value[1]) for value in values) / len(values),
                }
            )

        return {
            "forecast_count": len(forecasts),
            "resolved_count": len(resolved),
            "pending_count": pending_count,
            "accuracy": correct / len(resolved),
            "mean_brier_score": mean_brier,
            "mean_log_loss": sum(log_losses) / len(log_losses),
            "mean_baseline_brier_score": mean_baseline_brier,
            "mean_baseline_log_loss": sum(baseline_log_losses) / len(baseline_log_losses),
            "brier_skill_score": (
                1.0 - mean_brier / mean_baseline_brier
                if mean_baseline_brier > 0
                else None
            ),
            "mean_entropy_nats": sum(entropies) / len(entropies),
            "top_label_calibration_bins": calibration,
            "top_label_tie_break_order": list(TIE_BREAK_ORDER),
            "walk_forward_baseline_status": (
                "NOT_IMPLEMENTED_STORED_BASELINE_CUTOFF_CHECKED"
            ),
            "performance_claim_status": "DESCRIPTIVE_ONLY_NO_MODEL_SKILL_CLAIM",
        }

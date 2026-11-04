"""Fixed-horizon XRP forecast ledger; records only after verified OOS readiness, never predicts or trades."""
from __future__ import annotations

import hashlib
import json
import math
import re
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .feature_store import FeatureStoreError, HistoricalFeatureStore

HORIZONS = (3600, 14400, 86400, 604800, 2592000)
CLASSES = ("down", "flat", "up")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
READINESS_POLICY_ID = "xrp_forecast_readiness_v1"
_REQUIRED_BASELINES = ("naive_class_prior", "momentum_sign", "mean_reversion_sign", "volatility_normal")
_MIN_OOS_SAMPLES = 100
_MIN_SHADOW_SAMPLES = 100
_MIN_HORIZON_MULTIPLE = 10
_MIN_SOURCE_GROUPS = 2
_MAX_WEIGHTED_CALIBRATION_ERROR = 0.05
DEFAULT_DB = Path(__file__).resolve().parents[2] / "data" / "xrp_intelligence" / "forecast_ledger.sqlite3"


class ForecastLedgerError(ValueError):
    pass


class ForecastAlreadyResolvedError(ForecastLedgerError):
    pass


def _utc(value: Any, field: str) -> tuple[datetime, str]:
    if not isinstance(value, str) or not value.strip():
        raise ForecastLedgerError(f"{field} must be an ISO-8601 UTC timestamp")
    try:
        dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ForecastLedgerError(f"{field} is not valid ISO-8601") from exc
    if dt.tzinfo is None or dt.utcoffset() != timedelta(0):
        raise ForecastLedgerError(f"{field} must include UTC timezone")
    dt = dt.astimezone(timezone.utc)
    return dt, dt.isoformat(timespec="microseconds").replace("+00:00", "Z")


def _number(value: Any, field: str, minimum: float = 0.0) -> float:
    if isinstance(value, bool):
        raise ForecastLedgerError(f"{field} must be numeric, not boolean")
    try:
        n = float(value)
    except (TypeError, ValueError) as exc:
        raise ForecastLedgerError(f"{field} must be numeric") from exc
    if not math.isfinite(n) or n < minimum:
        raise ForecastLedgerError(f"{field} must be finite and >= {minimum}")
    return n


def _probs(value: Any, field: str) -> dict[str, float]:
    if not isinstance(value, Mapping) or set(value) != set(CLASSES):
        raise ForecastLedgerError(f"{field} must contain down, flat and up")
    result = {k: _number(value[k], f"{field}.{k}") for k in CLASSES}
    if any(v > 1 for v in result.values()) or abs(sum(result.values()) - 1) > 1e-6:
        raise ForecastLedgerError(f"{field} probabilities must be in [0,1] and sum to 1")
    return result


def _strings(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not value or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ForecastLedgerError(f"{field} must be a non-empty list of strings")
    return [x.strip() for x in value]


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode()).hexdigest()


def _class(realized_return: float, flat_band_bps: float) -> str:
    band = flat_band_bps / 10000
    return "down" if realized_return < -band else "up" if realized_return > band else "flat"


def _scores(probabilities: Mapping[str, float], actual: str) -> tuple[float, float, bool, str]:
    predicted = max(CLASSES, key=lambda key: probabilities[key])
    brier = sum((probabilities[k] - (k == actual)) ** 2 for k in CLASSES) / 3
    log_loss = -math.log(max(probabilities[actual], 1e-15))
    return brier, log_loss, predicted == actual, predicted


def _validate_readiness_report(report: Any) -> dict[str, Any]:
    """Validate an independent model evaluation and its point-in-time dataset manifest."""
    if not isinstance(report, Mapping):
        raise ForecastLedgerError("readiness report must be a JSON object")
    if report.get("schema_version") != "barrot.xrp.model-readiness.v1":
        raise ForecastLedgerError("readiness report schema is unsupported")
    if report.get("evaluation_type") != "chronological_walk_forward_model_evaluation":
        raise ForecastLedgerError("baseline-only or non-chronological evaluation cannot authorize a forecast")
    if report.get("status") != "PASS" or report.get("policy_id") != READINESS_POLICY_ID:
        raise ForecastLedgerError("readiness report has not passed the active forecast policy")

    for field in ("evaluation_id", "model_version", "baseline_model_version", "asset", "venue", "dataset_receipt_id"):
        if not isinstance(report.get(field), str) or not report[field].strip():
            raise ForecastLedgerError(f"readiness report {field} must be a non-empty string")
    if report["model_version"] == report["baseline_model_version"]:
        raise ForecastLedgerError("evaluated model must be distinct from its baseline model")
    if not isinstance(report.get("dataset_sha256"), str) or not _SHA256.fullmatch(report["dataset_sha256"]):
        raise ForecastLedgerError("readiness report dataset_sha256 must be a SHA-256 digest")

    horizon = report.get("horizon_seconds")
    if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon not in HORIZONS:
        raise ForecastLedgerError("readiness report horizon_seconds is unsupported")

    dataset = report.get("dataset_manifest")
    if not isinstance(dataset, Mapping):
        raise ForecastLedgerError("readiness report needs an immutable dataset_manifest")
    if dataset.get("model_eligible") is not True or dataset.get("quality_status") != "verified":
        raise ForecastLedgerError("readiness dataset manifest is not verified and model eligible")
    if dataset.get("asset") != report["asset"] or dataset.get("venue") != report["venue"]:
        raise ForecastLedgerError("readiness dataset manifest asset/venue does not match report")

    def string_list(value: Any, field: str) -> list[str]:
        if (
            not isinstance(value, list)
            or not value
            or any(not isinstance(item, str) or not item.strip() for item in value)
        ):
            raise ForecastLedgerError(f"readiness dataset {field} must be a non-empty string list")
        cleaned = [item.strip() for item in value]
        if len(cleaned) != len(set(cleaned)):
            raise ForecastLedgerError(f"readiness dataset {field} contains duplicates")
        return cleaned

    feature_ids = string_list(dataset.get("feature_ids"), "feature_ids")
    source_ids = string_list(dataset.get("source_ids"), "source_ids")
    feature_snapshot_ids = string_list(dataset.get("feature_snapshot_ids"), "feature_snapshot_ids")
    if any(not _SHA256.fullmatch(item) for item in feature_snapshot_ids):
        raise ForecastLedgerError("readiness dataset feature_snapshot_ids must be SHA-256 IDs")

    receipts = dataset.get("raw_source_receipts")
    if not isinstance(receipts, list) or not receipts:
        raise ForecastLedgerError("readiness dataset needs byte-addressed raw_source_receipts")
    receipt_sources: set[str] = set()
    receipt_groups: set[str] = set()
    receipt_ids: set[str] = set()
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, Mapping):
            raise ForecastLedgerError(f"raw_source_receipts[{index}] must be an object")
        source_id = receipt.get("source_id")
        receipt_id = receipt.get("receipt_id")
        digest = receipt.get("raw_content_sha256")
        group = receipt.get("independence_group")
        uri = receipt.get("source_uri")
        if not isinstance(source_id, str) or not source_id.strip():
            raise ForecastLedgerError(f"raw_source_receipts[{index}] needs source_id")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise ForecastLedgerError(f"raw_source_receipts[{index}] needs receipt_id")
        if receipt_id in receipt_ids:
            raise ForecastLedgerError("readiness dataset contains duplicate raw receipt IDs")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ForecastLedgerError(f"raw_source_receipts[{index}] needs a SHA-256 digest")
        if receipt.get("raw_capture_status") != "byte_complete":
            raise ForecastLedgerError(f"raw_source_receipts[{index}] must be byte_complete")
        if receipt.get("raw_receipt_sha256_verified") is not True:
            raise ForecastLedgerError(f"raw_source_receipts[{index}] has not verified its raw bytes")
        if not isinstance(group, str) or not group.strip():
            raise ForecastLedgerError(f"raw_source_receipts[{index}] needs independence_group")
        if not isinstance(uri, str) or not uri.strip():
            raise ForecastLedgerError(f"raw_source_receipts[{index}] needs source_uri")
        parsed_uri = urlsplit(uri.strip())
        if parsed_uri.scheme not in {"http", "https"} or not parsed_uri.netloc:
            raise ForecastLedgerError(f"raw_source_receipts[{index}] source_uri must be HTTP(S)")
        source_as_of = _utc(receipt.get("source_data_as_of_utc"), f"raw_source_receipts[{index}].source_data_as_of_utc")[0]
        captured_at = _utc(receipt.get("captured_at_utc"), f"raw_source_receipts[{index}].captured_at_utc")[0]
        if captured_at < source_as_of:
            raise ForecastLedgerError(f"raw_source_receipts[{index}] capture precedes source data as-of")
        receipt_sources.add(source_id.strip())
        receipt_groups.add(group.strip())
        receipt_ids.add(receipt_id.strip())
    if receipt_sources != set(source_ids):
        raise ForecastLedgerError("readiness dataset source_ids do not exactly match raw receipt sources")
    declared_groups = string_list(dataset.get("source_independence_groups"), "source_independence_groups")
    if set(declared_groups) != receipt_groups or len(receipt_groups) < _MIN_SOURCE_GROUPS:
        raise ForecastLedgerError(
            f"readiness dataset needs at least {_MIN_SOURCE_GROUPS} independently receipted source groups"
        )
    if report.get("source_independence_group_count") != len(receipt_groups):
        raise ForecastLedgerError("readiness report source_independence_group_count does not match dataset receipts")
    if dataset.get("data_cutoff_utc") is None:
        raise ForecastLedgerError("readiness dataset data_cutoff_utc is required")
    dataset_cutoff = _utc(dataset["data_cutoff_utc"], "dataset data_cutoff_utc")[0]
    if _hash(dict(dataset)) != report["dataset_sha256"]:
        raise ForecastLedgerError("readiness dataset manifest SHA-256 does not match dataset_sha256")

    def sample_count(field: str, minimum: int) -> int:
        value = report.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
            raise ForecastLedgerError(f"readiness report {field} must be at least {minimum}")
        return value

    sample_count("training_sample_count", _MIN_OOS_SAMPLES)
    sample_count("out_of_sample_sample_count", _MIN_OOS_SAMPLES)
    sample_count("shadow_evaluation_sample_count", _MIN_SHADOW_SAMPLES)

    def span(start_field: str, end_field: str, label: str) -> tuple[datetime, datetime]:
        start = _utc(report.get(start_field), f"readiness report {start_field}")[0]
        end = _utc(report.get(end_field), f"readiness report {end_field}")[0]
        if end <= start or (end - start).total_seconds() < horizon * _MIN_HORIZON_MULTIPLE:
            raise ForecastLedgerError(
                f"readiness report {label} span must cover at least {_MIN_HORIZON_MULTIPLE} forecast horizons"
            )
        return start, end

    _, oos_end = span("out_of_sample_start_utc", "out_of_sample_end_utc", "out-of-sample")
    shadow_start, shadow_end = span("shadow_evaluation_start_utc", "shadow_evaluation_end_utc", "shadow")
    if shadow_start < oos_end:
        raise ForecastLedgerError("shadow evaluation must follow the independent out-of-sample window")

    if report.get("leakage_check_status") != "PASS":
        raise ForecastLedgerError("readiness report leakage check did not pass")
    if report.get("calibration_status") != "PASS":
        raise ForecastLedgerError("readiness report calibration did not pass")
    if report.get("drift_status") != "STABLE":
        raise ForecastLedgerError("readiness report drift status is not stable")
    if report.get("shadow_evaluation_status") != "PASS":
        raise ForecastLedgerError("readiness report shadow evaluation did not pass")
    calibration_error = _number(
        report.get("weighted_calibration_error"), "readiness report weighted_calibration_error"
    )
    if calibration_error > _MAX_WEIGHTED_CALIBRATION_ERROR:
        raise ForecastLedgerError(
            f"readiness report weighted calibration error exceeds {_MAX_WEIGHTED_CALIBRATION_ERROR}"
        )

    model_metrics = report.get("model_metrics")
    baseline_metrics = report.get("baseline_metrics")
    if not isinstance(model_metrics, Mapping) or not isinstance(baseline_metrics, Mapping):
        raise ForecastLedgerError("readiness report must include model and baseline metrics")
    if not set(_REQUIRED_BASELINES).issubset(baseline_metrics):
        raise ForecastLedgerError("readiness report is missing one or more required baselines")
    model_brier = _number(model_metrics.get("mean_brier_score"), "model mean_brier_score")
    model_log_loss = _number(model_metrics.get("mean_log_loss"), "model mean_log_loss")
    for baseline in _REQUIRED_BASELINES:
        metrics = baseline_metrics[baseline]
        if not isinstance(metrics, Mapping):
            raise ForecastLedgerError(f"baseline metrics for {baseline} must be an object")
        _number(metrics.get("mean_brier_score"), f"{baseline} mean_brier_score")
        _number(metrics.get("mean_log_loss"), f"{baseline} mean_log_loss")
    naive = baseline_metrics["naive_class_prior"]
    if (
        model_brier >= _number(naive.get("mean_brier_score"), "naive mean_brier_score")
        or model_log_loss >= _number(naive.get("mean_log_loss"), "naive mean_log_loss")
    ):
        raise ForecastLedgerError("model must outperform the naive baseline on both Brier score and log loss")

    data_cutoff = _utc(report.get("evaluation_data_cutoff_utc"), "evaluation_data_cutoff_utc")[0]
    completed = _utc(report.get("evaluation_completed_at_utc"), "evaluation_completed_at_utc")[0]
    if data_cutoff < dataset_cutoff:
        raise ForecastLedgerError("evaluation data cutoff precedes dataset manifest cutoff")
    if completed < data_cutoff or completed < oos_end or completed < shadow_end:
        raise ForecastLedgerError("readiness evaluation completion precedes its evaluated data window")
    return dict(report)


class ForecastLedger:
    """SQLite append-only ledger with SQL row guards; not file-level tamper-proof."""

    def __init__(
        self,
        db_path: str | Path = DEFAULT_DB,
        *,
        clock: Callable[[], datetime] | None = None,
        feature_store: HistoricalFeatureStore | None = None,
    ) -> None:
        self.db_path = Path(db_path)
        # Injectable only as a deterministic test seam; production defaults to UTC wall time.
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.feature_store = feature_store
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        db = self._connect()
        try:
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ForecastLedgerError(f"unsupported forecast ledger schema version: {version}")
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS forecasts(
                    forecast_id TEXT PRIMARY KEY, payload TEXT NOT NULL,
                    target_time_utc TEXT NOT NULL, venue TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS readiness_reports(
                    report_sha256 TEXT PRIMARY KEY, receipt_id TEXT NOT NULL,
                    payload BLOB NOT NULL, registered_at_utc TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS outcomes(
                    forecast_id TEXT PRIMARY KEY REFERENCES forecasts(forecast_id),
                    status TEXT NOT NULL CHECK(status IN ('scored','unscorable')),
                    payload TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events(
                    event_id TEXT PRIMARY KEY, forecast_id TEXT NOT NULL REFERENCES forecasts(forecast_id),
                    event_type TEXT NOT NULL, payload TEXT NOT NULL
                );
                CREATE TRIGGER IF NOT EXISTS forecasts_no_update BEFORE UPDATE ON forecasts
                    BEGIN SELECT RAISE(ABORT,'forecast records are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS forecasts_no_delete BEFORE DELETE ON forecasts
                    BEGIN SELECT RAISE(ABORT,'forecast records are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS readiness_reports_no_update BEFORE UPDATE ON readiness_reports
                    BEGIN SELECT RAISE(ABORT,'readiness reports are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS readiness_reports_no_delete BEFORE DELETE ON readiness_reports
                    BEGIN SELECT RAISE(ABORT,'readiness reports are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS outcomes_no_update BEFORE UPDATE ON outcomes
                    BEGIN SELECT RAISE(ABORT,'outcome records are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS outcomes_no_delete BEFORE DELETE ON outcomes
                    BEGIN SELECT RAISE(ABORT,'outcome records are immutable'); END;
                CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
                    BEGIN SELECT RAISE(ABORT,'events are append-only'); END;
                CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
                    BEGIN SELECT RAISE(ABORT,'events are append-only'); END;
            """)
            db.execute("PRAGMA user_version=1")
            db.commit()
        finally:
            db.close()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.db_path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _now(self) -> datetime:
        """Return the validated UTC ledger receipt clock."""
        now = self._clock()
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise ForecastLedgerError("ledger clock must return a timezone-aware datetime")
        return now.astimezone(timezone.utc)

    def register_readiness_report(
        self,
        report_bytes: bytes,
        *,
        receipt_id: str,
        raw_receipt_bytes: Mapping[str, bytes],
    ) -> str:
        """Register one immutable, byte-addressed model-readiness report."""
        if not isinstance(report_bytes, bytes) or not report_bytes:
            raise ForecastLedgerError("readiness report bytes are required")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise ForecastLedgerError("readiness report receipt_id is required")
        try:
            report = json.loads(report_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForecastLedgerError("readiness report bytes must contain valid JSON") from exc
        validated_report = _validate_readiness_report(report)
        if not isinstance(raw_receipt_bytes, Mapping):
            raise ForecastLedgerError("raw_receipt_bytes must map raw receipt IDs to exact bytes")
        for index, receipt in enumerate(validated_report["dataset_manifest"]["raw_source_receipts"]):
            raw_bytes = raw_receipt_bytes.get(receipt["receipt_id"])
            if not isinstance(raw_bytes, bytes) or not raw_bytes:
                raise ForecastLedgerError(f"readiness raw receipt {receipt['receipt_id']!r} bytes are missing")
            if hashlib.sha256(raw_bytes).hexdigest() != receipt["raw_content_sha256"]:
                raise ForecastLedgerError(
                    f"readiness raw receipt {receipt['receipt_id']!r} bytes do not match its SHA-256"
                )
        report_sha256 = hashlib.sha256(report_bytes).hexdigest()
        registered_at = self._now().isoformat(timespec="microseconds").replace("+00:00", "Z")
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT receipt_id,payload,registered_at_utc FROM readiness_reports WHERE report_sha256=?",
                (report_sha256,),
            ).fetchone()
            if existing:
                if existing["receipt_id"] != receipt_id.strip() or bytes(existing["payload"]) != report_bytes:
                    raise ForecastLedgerError("readiness report hash collision")
                db.commit()
                return report_sha256
            db.execute(
                "INSERT INTO readiness_reports(report_sha256,receipt_id,payload,registered_at_utc) VALUES(?,?,?,?)",
                (report_sha256, receipt_id.strip(), report_bytes, registered_at),
            )
            db.commit()
            return report_sha256
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _verify_readiness_certificate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        certificate = payload.get("readiness_certificate")
        if not isinstance(certificate, Mapping):
            raise ForecastLedgerError("a verified out-of-sample readiness certificate is required")
        report_sha256 = certificate.get("report_sha256")
        receipt_id = certificate.get("receipt_id")
        if not isinstance(report_sha256, str) or not _SHA256.fullmatch(report_sha256):
            raise ForecastLedgerError("readiness certificate report_sha256 must be a SHA-256 digest")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise ForecastLedgerError("readiness certificate receipt_id is required")
        if certificate.get("policy_id") != READINESS_POLICY_ID or certificate.get("status") != "PASS":
            raise ForecastLedgerError("readiness certificate does not match the active forecast policy")

        db = self._connect()
        try:
            row = db.execute(
                "SELECT receipt_id,payload FROM readiness_reports WHERE report_sha256=?",
                (report_sha256,),
            ).fetchone()
        finally:
            db.close()
        if not row:
            raise ForecastLedgerError("readiness report is not registered in the immutable ledger")
        if row["receipt_id"] != receipt_id.strip():
            raise ForecastLedgerError("readiness certificate receipt_id does not match the registered report")
        report_bytes = bytes(row["payload"])
        if hashlib.sha256(report_bytes).hexdigest() != report_sha256:
            raise ForecastLedgerError("registered readiness report failed SHA-256 verification")
        try:
            report = json.loads(report_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ForecastLedgerError("registered readiness report is not valid JSON") from exc
        _validate_readiness_report(report)

        if report["model_version"] != payload["model_version"]:
            raise ForecastLedgerError("readiness report model_version does not match forecast")
        if report["asset"].strip().upper() != payload["asset"]:
            raise ForecastLedgerError("readiness report asset does not match forecast")
        if report["venue"].strip() != payload["venue"]:
            raise ForecastLedgerError("readiness report venue does not match forecast")
        if report["horizon_seconds"] != payload["horizon_seconds"]:
            raise ForecastLedgerError("readiness report horizon does not match forecast")
        evaluation_cutoff = _utc(report["evaluation_data_cutoff_utc"], "evaluation_data_cutoff_utc")[0]
        evaluation_completed = _utc(report["evaluation_completed_at_utc"], "evaluation_completed_at_utc")[0]
        forecast_cutoff = _utc(payload["data_cutoff_utc"], "data_cutoff_utc")[0]
        forecast_issued = _utc(payload["issued_at_utc"], "issued_at_utc")[0]
        if evaluation_cutoff > forecast_cutoff:
            raise ForecastLedgerError("readiness evaluation data cutoff exceeds forecast cutoff")
        if evaluation_completed > forecast_issued:
            raise ForecastLedgerError("readiness evaluation completed after forecast issue time")
        registered_at = _utc(row["registered_at_utc"], "readiness report registered_at_utc")[0]
        if registered_at > forecast_issued:
            raise ForecastLedgerError("readiness report was registered after forecast issue time")
        if set(report["dataset_manifest"]["source_ids"]) != set(payload["source_ids"]):
            raise ForecastLedgerError("readiness dataset source_ids do not match forecast source_ids")
        return report

    def _normalize(self, r: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(r, Mapping):
            raise ForecastLedgerError("forecast must be a mapping")
        required = (
            "asset", "venue", "target_definition", "reference_price_usd", "reference_price_timestamp_utc",
            "reference_price_source_id", "reference_price_max_age_seconds", "data_cutoff_utc", "issued_at_utc",
            "target_time_utc", "horizon_seconds", "model_version", "baseline_model_version",
            "probabilities", "baseline_probabilities", "flat_band_bps",
            "outcome_tolerance_seconds", "feature_max_timestamp_utc",
            "feature_snapshot_ids", "source_ids", "assumptions", "alternatives",
            "fee_bps", "slippage_bps", "readiness_certificate",
        )
        missing = [k for k in required if k not in r]
        if missing:
            raise ForecastLedgerError("missing fields: " + ", ".join(missing))
        horizon = r["horizon_seconds"]
        if isinstance(horizon, bool) or not isinstance(horizon, int) or horizon not in HORIZONS:
            raise ForecastLedgerError(f"horizon_seconds must be one of {HORIZONS}")
        cutoff, cutoff_s = _utc(r["data_cutoff_utc"], "data_cutoff_utc")
        reference_time, reference_time_s = _utc(r["reference_price_timestamp_utc"], "reference_price_timestamp_utc")
        issued, issued_s = _utc(r["issued_at_utc"], "issued_at_utc")
        target, target_s = _utc(r["target_time_utc"], "target_time_utc")
        feature_max, feature_s = _utc(r["feature_max_timestamp_utc"], "feature_max_timestamp_utc")
        if reference_time > cutoff:
            raise ForecastLedgerError("reference_price_timestamp_utc exceeds data cutoff (look-ahead leakage)")
        reference_max_age = r["reference_price_max_age_seconds"]
        if isinstance(reference_max_age, bool) or not isinstance(reference_max_age, int) or not 0 <= reference_max_age <= 3600:
            raise ForecastLedgerError("reference_price_max_age_seconds must be 0..3600")
        if (cutoff - reference_time).total_seconds() > reference_max_age:
            raise ForecastLedgerError("reference price is older than the declared maximum age")
        if issued < cutoff or issued >= target:
            raise ForecastLedgerError("issued_at_utc must be >= cutoff and < target time")
        if feature_max > cutoff:
            raise ForecastLedgerError("feature_max_timestamp_utc exceeds cutoff (look-ahead leakage)")
        if target != cutoff + timedelta(seconds=horizon):
            raise ForecastLedgerError("target_time_utc must equal cutoff plus horizon_seconds")
        tolerance = r["outcome_tolerance_seconds"]
        if isinstance(tolerance, bool) or not isinstance(tolerance, int) or not 0 <= tolerance <= 3600:
            raise ForecastLedgerError("outcome_tolerance_seconds must be 0..3600")
        text_fields = ("asset", "venue", "target_definition", "model_version", "baseline_model_version")
        if any(not isinstance(r[k], str) or not r[k].strip() for k in text_fields):
            raise ForecastLedgerError("asset, venue, target_definition and model versions must be non-empty strings")
        asset, venue = r["asset"].strip().upper(), r["venue"].strip()
        target_definition = r["target_definition"].strip()
        model, baseline = r["model_version"].strip(), r["baseline_model_version"].strip()
        reference_source = r["reference_price_source_id"]
        if not isinstance(reference_source, str) or not reference_source.strip():
            raise ForecastLedgerError("reference_price_source_id must be a non-empty string")
        reference_source = reference_source.strip()
        certificate = r["readiness_certificate"]
        if not isinstance(certificate, Mapping):
            raise ForecastLedgerError("readiness_certificate must be an object")
        report_sha256 = certificate.get("report_sha256")
        receipt_id = certificate.get("receipt_id")
        if not isinstance(report_sha256, str) or not _SHA256.fullmatch(report_sha256):
            raise ForecastLedgerError("readiness_certificate report_sha256 must be a SHA-256 digest")
        if not isinstance(receipt_id, str) or not receipt_id.strip():
            raise ForecastLedgerError("readiness_certificate receipt_id is required")
        if certificate.get("policy_id") != READINESS_POLICY_ID or certificate.get("status") != "PASS":
            raise ForecastLedgerError("readiness_certificate does not match the active policy")
        source_ids = _strings(r["source_ids"], "source_ids")
        if reference_source not in source_ids:
            raise ForecastLedgerError("reference_price_source_id must be included in source_ids")
        return {
            "schema_version": 1, "asset": asset, "venue": venue,
            "target_definition": target_definition,
            "reference_price_usd": _number(r["reference_price_usd"], "reference_price_usd", 1e-12),
            "reference_price_timestamp_utc": reference_time_s,
            "reference_price_source_id": reference_source,
            "reference_price_max_age_seconds": reference_max_age,
            "data_cutoff_utc": cutoff_s, "issued_at_utc": issued_s, "target_time_utc": target_s,
            "horizon_seconds": horizon, "model_version": model, "baseline_model_version": baseline,
            "probabilities": _probs(r["probabilities"], "probabilities"),
            "baseline_probabilities": _probs(r["baseline_probabilities"], "baseline_probabilities"),
            "flat_band_bps": _number(r["flat_band_bps"], "flat_band_bps"),
            "outcome_tolerance_seconds": tolerance, "feature_max_timestamp_utc": feature_s,
            "feature_snapshot_ids": _strings(r["feature_snapshot_ids"], "feature_snapshot_ids"),
            "source_ids": source_ids,
            "assumptions": _strings(r["assumptions"], "assumptions"),
            "alternatives": _strings(r["alternatives"], "alternatives"),
            "fee_bps": _number(r["fee_bps"], "fee_bps"),
            "slippage_bps": _number(r["slippage_bps"], "slippage_bps"),
            "readiness_certificate": {
                "report_sha256": report_sha256,
                "receipt_id": receipt_id.strip(),
                "policy_id": READINESS_POLICY_ID,
                "status": "PASS",
            },
            "point_target_price_usd": (
                _number(r["point_target_price_usd"], "point_target_price_usd", 1e-12)
                if r.get("point_target_price_usd") is not None else None
            ),
        }

    def _verify_feature_snapshots(
        self, payload: Mapping[str, Any], readiness_report: Mapping[str, Any]
    ) -> None:
        """Fail closed unless every referenced snapshot is exact, verified and available by cutoff."""
        store = self.feature_store
        if store is None:
            raise ForecastLedgerError(
                "a verified HistoricalFeatureStore is required before forecast recording"
            )

        snapshot_ids = payload["feature_snapshot_ids"]
        if len(snapshot_ids) != len(set(snapshot_ids)):
            raise ForecastLedgerError("feature_snapshot_ids must be unique")
        if any(not _SHA256.fullmatch(snapshot_id) for snapshot_id in snapshot_ids):
            raise ForecastLedgerError("feature_snapshot_ids must be SHA-256 snapshot IDs")

        cutoff = _utc(payload["data_cutoff_utc"], "data_cutoff_utc")[0]
        declared_feature_max = _utc(
            payload["feature_max_timestamp_utc"], "feature_max_timestamp_utc"
        )[0]
        expected_sources: set[str] = set()
        maximum_information_time: datetime | None = None
        observed_feature_ids: set[str] = set()
        asset = payload["asset"]

        for snapshot_id in snapshot_ids:
            try:
                snapshot = store.verified_snapshot(snapshot_id)
            except (FeatureStoreError, AttributeError, KeyError, TypeError, ValueError) as exc:
                raise ForecastLedgerError(
                    f"feature snapshot {snapshot_id} is unavailable or failed integrity verification"
                ) from exc

            if snapshot.get("snapshot_id") != snapshot_id:
                raise ForecastLedgerError("feature store returned a different snapshot ID")
            if not snapshot.get("verification", {}).get("valid"):
                raise ForecastLedgerError("feature snapshot integrity is not verified")
            if asset not in snapshot.get("asset_scope", []):
                raise ForecastLedgerError(
                    f"feature snapshot {snapshot_id} does not cover asset {asset}"
                )

            snapshot_cutoff = _utc(
                snapshot.get("data_cutoff_utc"), "feature snapshot data_cutoff_utc"
            )[0]
            captured_at = _utc(
                snapshot.get("captured_at_utc"), "feature snapshot captured_at_utc"
            )[0]
            stored_at = _utc(
                snapshot.get("stored_at_utc"), "feature snapshot stored_at_utc"
            )[0]
            if snapshot_cutoff > cutoff:
                raise ForecastLedgerError("feature snapshot data cutoff exceeds forecast cutoff")
            if captured_at > cutoff or stored_at > cutoff:
                raise ForecastLedgerError(
                    "feature snapshot was not captured and stored by the forecast cutoff"
                )

            manifest = snapshot.get("manifest")
            if not isinstance(manifest, Mapping) or not isinstance(manifest.get("records"), list):
                raise ForecastLedgerError("verified feature snapshot has a malformed manifest")
            asset_records = [
                item for item in manifest["records"]
                if isinstance(item, Mapping) and item.get("asset") == asset
            ]
            if not asset_records:
                raise ForecastLedgerError(
                    f"feature snapshot {snapshot_id} contains no model-facing records for {asset}"
                )

            for record in asset_records:
                feature_id = record.get("feature_id")
                if not isinstance(feature_id, str) or not feature_id.strip():
                    raise ForecastLedgerError("feature record contains an invalid feature_id")
                observed_feature_ids.add(feature_id.strip())
                sources = record.get("sources")
                if not isinstance(sources, list):
                    raise ForecastLedgerError("feature record source lineage is malformed")
                for source in sources:
                    source_id = source.get("source_id") if isinstance(source, Mapping) else None
                    if not isinstance(source_id, str) or not source_id.strip():
                        raise ForecastLedgerError("feature record contains an invalid source ID")
                    expected_sources.add(source_id)
                for field in (
                    "known_at_utc",
                    "source_data_as_of_utc",
                    "ingested_at_utc",
                    "revision_available_at_utc",
                ):
                    timestamp = _utc(record.get(field), f"feature record {field}")[0]
                    if timestamp > cutoff:
                        raise ForecastLedgerError(
                            f"feature record {field} exceeds forecast cutoff"
                        )
                    if maximum_information_time is None or timestamp > maximum_information_time:
                        maximum_information_time = timestamp

        if set(payload["source_ids"]) != expected_sources:
            missing = sorted(expected_sources - set(payload["source_ids"]))
            extra = sorted(set(payload["source_ids"]) - expected_sources)
            raise ForecastLedgerError(
                f"forecast source_ids do not exactly match referenced feature lineage; missing={missing}, extra={extra}"
            )
        if maximum_information_time is None or declared_feature_max != maximum_information_time:
            raise ForecastLedgerError(
                "feature_max_timestamp_utc must equal the maximum feature information-availability timestamp"
            )
        if not observed_feature_ids.issubset(set(readiness_report["dataset_manifest"]["feature_ids"])):
            raise ForecastLedgerError("feature snapshots contain feature IDs absent from the evaluated dataset")

    def record_forecast(self, record: Mapping[str, Any]) -> str:
        """Record a live/shadow forecast once; historical backtests use separate artifacts."""
        payload = self._normalize(record)
        readiness_report = self._verify_readiness_certificate(payload)
        self._verify_feature_snapshots(payload, readiness_report)
        payload_s = _json(payload)
        forecast_id = _hash(payload)
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT payload FROM forecasts WHERE forecast_id=?", (forecast_id,)).fetchone()
            if old:
                if old["payload"] != payload_s:
                    raise ForecastLedgerError("forecast ID collision")
                db.commit()
                return forecast_id

            recorded_at = self._now()
            recorded_at_s = recorded_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
            issued_at = _utc(payload["issued_at_utc"], "issued_at_utc")[0]
            target_at = _utc(payload["target_time_utc"], "target_time_utc")[0]

            # A caller-supplied historical issued_at must not make a past outcome look
            # like a forecast that existed before the outcome. The live ledger accepts
            # only forecasts recorded before their target and within five minutes of issue.
            if issued_at > recorded_at:
                raise ForecastLedgerError("issued_at_utc cannot be later than actual ledger recording time")
            if target_at <= recorded_at:
                raise ForecastLedgerError("target_time_utc must be after actual ledger recording time")
            if (recorded_at - issued_at).total_seconds() > 300:
                raise ForecastLedgerError("issued_at_utc is older than the five-minute live recording window")

            event = {
                "forecast_id": forecast_id,
                "forecast": payload,
                "recorded_at_utc": recorded_at_s,
                "recording_mode": "live_shadow",
            }
            event_id = _hash({"event_type": "forecast_issued", "payload": event})
            db.execute(
                "INSERT INTO forecasts(forecast_id,payload,target_time_utc,venue) VALUES(?,?,?,?)",
                (forecast_id, payload_s, payload["target_time_utc"], payload["venue"]),
            )
            db.execute(
                "INSERT INTO events(event_id,forecast_id,event_type,payload) VALUES(?,?,?,?)",
                (event_id, forecast_id, "forecast_issued", _json(event)),
            )
            db.commit()
            return forecast_id
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def resolve_forecast(
        self, forecast_id: str, *, resolved_at_utc: str, outcome_price_usd: float | None,
        outcome_price_timestamp_utc: str | None = None, outcome_venue: str | None = None,
        outcome_source_ids: list[str] | None = None,
        cross_venue_normalization: str | None = None, unscorable_reason: str | None = None,
    ) -> dict[str, Any]:
        """Record one outcome after the horizon; missing data is unscorable, never a miss."""
        resolved, resolved_s = _utc(resolved_at_utc, "resolved_at_utc")
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            recorded_at = self._now()
            recorded_at_s = recorded_at.isoformat(timespec="microseconds").replace("+00:00", "Z")
            row = db.execute("SELECT payload FROM forecasts WHERE forecast_id=?", (forecast_id,)).fetchone()
            if not row:
                raise ForecastLedgerError("unknown forecast_id")
            if db.execute("SELECT 1 FROM outcomes WHERE forecast_id=?", (forecast_id,)).fetchone():
                raise ForecastAlreadyResolvedError("forecast outcome is immutable")
            forecast = json.loads(row["payload"])
            target = _utc(forecast["target_time_utc"], "target_time_utc")[0]
            if resolved > recorded_at:
                raise ForecastLedgerError("resolved_at_utc cannot be later than actual ledger recording time")
            if resolved < target:
                raise ForecastLedgerError("resolved_at_utc precedes target time")

            if outcome_price_usd is None:
                tolerance_end = target + timedelta(seconds=forecast["outcome_tolerance_seconds"])
                if resolved < tolerance_end or recorded_at < tolerance_end:
                    raise ForecastLedgerError("unscorable outcome cannot be recorded before the outcome_tolerance_seconds window closes")
                if not isinstance(unscorable_reason, str) or not unscorable_reason.strip():
                    raise ForecastLedgerError("unscorable_reason required when outcome price is missing")
                outcome = {
                    "forecast_id": forecast_id, "status": "unscorable",
                    "resolved_at_utc": resolved_s, "outcome_price_usd": None,
                    "actual_class": None, "directional_correct": None,
                    "brier_score": None, "log_loss": None,
                    "baseline_brier_score": None, "baseline_log_loss": None,
                    "unscorable_reason": unscorable_reason.strip(),
                }
            else:
                price = _number(outcome_price_usd, "outcome_price_usd", 1e-12)
                observed, observed_s = _utc(outcome_price_timestamp_utc, "outcome_price_timestamp_utc")
                if observed > recorded_at:
                    raise ForecastLedgerError("outcome_price_timestamp_utc cannot be later than actual ledger recording time")
                if abs((observed - target).total_seconds()) > forecast["outcome_tolerance_seconds"]:
                    raise ForecastLedgerError("outcome timestamp outside predeclared tolerance")
                if resolved < observed:
                    raise ForecastLedgerError("resolved_at_utc precedes outcome timestamp")
                if not isinstance(outcome_venue, str) or not outcome_venue.strip():
                    raise ForecastLedgerError("outcome_venue required")
                normalization = cross_venue_normalization.strip() if isinstance(cross_venue_normalization, str) else ""
                if outcome_venue.strip() != forecast["venue"] and not normalization:
                    raise ForecastLedgerError("cross-venue outcome requires explicit normalization")
                sources = _strings(outcome_source_ids or [], "outcome_source_ids")
                realized = price / forecast["reference_price_usd"] - 1
                actual = _class(realized, forecast["flat_band_bps"])
                brier, loss, correct, predicted = _scores(forecast["probabilities"], actual)
                base_brier, base_loss, base_correct, base_predicted = _scores(forecast["baseline_probabilities"], actual)
                outcome = {
                    "forecast_id": forecast_id, "status": "scored", "resolved_at_utc": resolved_s,
                    "outcome_price_usd": price, "outcome_price_timestamp_utc": observed_s,
                    "outcome_venue": outcome_venue.strip(), "outcome_source_ids": sources,
                    "cross_venue_normalization": normalization or None, "realized_return": realized,
                    "actual_class": actual, "predicted_class": predicted, "baseline_predicted_class": base_predicted,
                    "directional_correct": correct, "baseline_directional_correct": base_correct,
                    "brier_score": brier, "log_loss": loss,
                    "baseline_brier_score": base_brier, "baseline_log_loss": base_loss,
                }
            outcome["recorded_at_utc"] = recorded_at_s
            event = {
                "forecast_id": forecast_id,
                "outcome": outcome,
                "recorded_at_utc": recorded_at_s,
            }
            event_id = _hash({"event_type": "forecast_resolved", "payload": event})
            db.execute(
                "INSERT INTO outcomes(forecast_id,status,payload) VALUES(?,?,?)",
                (forecast_id, outcome["status"], _json(outcome)),
            )
            db.execute(
                "INSERT INTO events(event_id,forecast_id,event_type,payload) VALUES(?,?,?,?)",
                (event_id, forecast_id, "forecast_resolved", _json(event)),
            )
            db.commit()
            return outcome
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def get_forecast(self, forecast_id: str) -> dict[str, Any] | None:
        db = self._connect()
        try:
            row = db.execute("SELECT payload FROM forecasts WHERE forecast_id=?", (forecast_id,)).fetchone()
            if not row:
                return None
            result = json.loads(row["payload"])
            result["forecast_id"] = forecast_id
            return result
        finally:
            db.close()

    def events(self, forecast_id: str | None = None) -> list[dict[str, Any]]:
        db = self._connect()
        try:
            if forecast_id:
                rows = db.execute("SELECT payload FROM events WHERE forecast_id=? ORDER BY rowid", (forecast_id,))
            else:
                rows = db.execute("SELECT payload FROM events ORDER BY rowid")
            return [json.loads(row["payload"]) for row in rows.fetchall()]
        finally:
            db.close()

    def summary(self) -> dict[str, Any]:
        db = self._connect()
        try:
            total = db.execute("SELECT COUNT(*) FROM forecasts").fetchone()[0]
            rows = db.execute("""
                SELECT f.payload AS forecast, o.payload AS outcome
                FROM forecasts f LEFT JOIN outcomes o ON f.forecast_id=o.forecast_id
                ORDER BY f.target_time_utc
            """).fetchall()
        finally:
            db.close()

        resolved = [json.loads(row["outcome"]) for row in rows if row["outcome"]]
        scored = [
            (json.loads(row["forecast"]), json.loads(row["outcome"]))
            for row in rows
            if row["outcome"] and json.loads(row["outcome"])["status"] == "scored"
        ]
        counts = {
            "forecasts": total,
            "resolved": len(resolved),
            "scored": len(scored),
            "unscorable": sum(x["status"] == "unscorable" for x in resolved),
            "unresolved": total - len(resolved),
        }
        empty_metrics = {
            "directional_accuracy": None,
            "top_class_accuracy": None,
            "baseline_directional_accuracy": None,
            "baseline_top_class_accuracy": None,
            "mean_brier_score": None,
            "mean_log_loss": None,
            "baseline_mean_brier_score": None,
            "baseline_mean_log_loss": None,
            "brier_improvement_vs_baseline": None,
            "calibration_bins": [],
            "weighted_calibration_error": None,
            "scoring_method": "three_class_brier_mean_squared_error_v1",
            "accuracy_definition": "top-class classification accuracy across down/flat/up; includes the flat class",
        }
        if not scored:
            return {
                **counts,
                **empty_metrics,
                "cohort_summaries": [],
                "aggregation_policy": (
                    "Top-level scoring metrics are populated only when all scored records share "
                    "the same asset, venue, horizon, model, baseline, target definition, flat band "
                    "and outcome tolerance; otherwise consult cohort_summaries."
                ),
            }

        def metrics(items: list[tuple[dict[str, Any], dict[str, Any]]]) -> dict[str, Any]:
            accuracy = sum(bool(outcome["directional_correct"]) for _, outcome in items) / len(items)
            baseline_accuracy = sum(bool(outcome["baseline_directional_correct"]) for _, outcome in items) / len(items)
            mean_brier = sum(outcome["brier_score"] for _, outcome in items) / len(items)
            mean_loss = sum(outcome["log_loss"] for _, outcome in items) / len(items)
            base_brier = sum(outcome["baseline_brier_score"] for _, outcome in items) / len(items)
            base_loss = sum(outcome["baseline_log_loss"] for _, outcome in items) / len(items)
            bins: dict[int, list[float]] = {}
            for forecast, outcome in items:
                confidence = max(forecast["probabilities"].values())
                index = min(int(confidence * 10), 9)
                bucket = bins.setdefault(index, [0, 0.0, 0.0])
                bucket[0] += 1
                bucket[1] += confidence
                bucket[2] += float(outcome["directional_correct"])
            calibration = []
            weighted_error = 0.0
            for index, (count, confidence_sum, correct_sum) in sorted(bins.items()):
                mean_conf = confidence_sum / count
                observed = correct_sum / count
                gap = abs(mean_conf - observed)
                weighted_error += count / len(items) * gap
                calibration.append({
                    "lower_bound": index / 10,
                    "upper_bound": (index + 1) / 10,
                    "count": int(count),
                    "mean_confidence": mean_conf,
                    "observed_accuracy": observed,
                    "absolute_gap": gap,
                })
            return {
                "scored": len(items),
                "directional_accuracy": accuracy,
                "top_class_accuracy": accuracy,
                "baseline_directional_accuracy": baseline_accuracy,
                "baseline_top_class_accuracy": baseline_accuracy,
                "mean_brier_score": mean_brier,
                "mean_log_loss": mean_loss,
                "baseline_mean_brier_score": base_brier,
                "baseline_mean_log_loss": base_loss,
                "brier_improvement_vs_baseline": base_brier - mean_brier,
                "calibration_bins": calibration,
                "weighted_calibration_error": weighted_error,
                "scoring_method": "three_class_brier_mean_squared_error_v1",
                "accuracy_definition": "top-class classification accuracy across down/flat/up; includes the flat class",
            }

        cohorts: dict[tuple[Any, ...], list[tuple[dict[str, Any], dict[str, Any]]]] = {}
        for forecast, outcome in scored:
            key = (
                forecast["asset"],
                forecast["venue"],
                forecast["horizon_seconds"],
                forecast["model_version"],
                forecast["baseline_model_version"],
                forecast["target_definition"],
                forecast["flat_band_bps"],
                forecast["outcome_tolerance_seconds"],
            )
            cohorts.setdefault(key, []).append((forecast, outcome))

        cohort_summaries = []
        for key, items in sorted(cohorts.items()):
            cohort_summaries.append({
                "asset": key[0],
                "venue": key[1],
                "horizon_seconds": key[2],
                "model_version": key[3],
                "baseline_model_version": key[4],
                "target_definition": key[5],
                "flat_band_bps": key[6],
                "outcome_tolerance_seconds": key[7],
                **metrics(items),
            })

        # Never pool unlike horizons, venues, models or target definitions.
        top_level_metrics = metrics(scored) if len(cohorts) == 1 else empty_metrics
        return {
            **counts,
            **top_level_metrics,
            "cohort_summaries": cohort_summaries,
            "aggregation_policy": (
                "Top-level scoring metrics are populated only when all scored records share "
                "the same asset, venue, horizon, model, baseline, target definition, flat band "
                "and outcome tolerance; otherwise consult cohort_summaries."
            ),
        }

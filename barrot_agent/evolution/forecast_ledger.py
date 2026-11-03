"""Fixed-horizon XRP forecast ledger; records only, never predicts or trades."""
from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

HORIZONS = (3600, 14400, 86400, 604800, 2592000)
CLASSES = ("down", "flat", "up")
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


class ForecastLedger:
    """SQLite event ledger with database-enforced immutable forecast/outcome rows."""

    def __init__(self, db_path: str | Path = DEFAULT_DB) -> None:
        self.db_path = Path(db_path)
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
            "fee_bps", "slippage_bps",
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
            "point_target_price_usd": (
                _number(r["point_target_price_usd"], "point_target_price_usd", 1e-12)
                if r.get("point_target_price_usd") is not None else None
            ),
        }

    def record_forecast(self, record: Mapping[str, Any]) -> str:
        """Record once; an identical retry returns the same forecast ID."""
        payload = self._normalize(record)
        payload_s = _json(payload)
        forecast_id = _hash(payload)
        event = {"forecast_id": forecast_id, "forecast": payload}
        event_id = _hash({"event_type": "forecast_issued", "payload": event})
        db = self._connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            old = db.execute("SELECT payload FROM forecasts WHERE forecast_id=?", (forecast_id,)).fetchone()
            if old:
                if old["payload"] != payload_s:
                    raise ForecastLedgerError("forecast ID collision")
                db.commit()
                return forecast_id
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
            row = db.execute("SELECT payload FROM forecasts WHERE forecast_id=?", (forecast_id,)).fetchone()
            if not row:
                raise ForecastLedgerError("unknown forecast_id")
            if db.execute("SELECT 1 FROM outcomes WHERE forecast_id=?", (forecast_id,)).fetchone():
                raise ForecastAlreadyResolvedError("forecast outcome is immutable")
            forecast = json.loads(row["payload"])
            target = _utc(forecast["target_time_utc"], "target_time_utc")[0]
            if resolved < target:
                raise ForecastLedgerError("resolved_at_utc precedes target time")

            if outcome_price_usd is None:
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
            event = {"forecast_id": forecast_id, "outcome": outcome}
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
        scored = [(json.loads(row["forecast"]), json.loads(row["outcome"])) for row in rows if row["outcome"] and json.loads(row["outcome"])["status"] == "scored"]
        if not scored:
            return {
                "forecasts": total, "resolved": len(resolved), "scored": 0,
                "unscorable": sum(x["status"] == "unscorable" for x in resolved),
                "unresolved": total - len(resolved), "directional_accuracy": None,
                "mean_brier_score": None, "mean_log_loss": None,
                "baseline_directional_accuracy": None, "baseline_mean_brier_score": None,
                "baseline_mean_log_loss": None, "calibration_bins": [],
            }
        accuracy = sum(x["directional_correct"] for _, x in scored) / len(scored)
        baseline_accuracy = sum(x["baseline_directional_correct"] for _, x in scored) / len(scored)
        mean_brier = sum(x["brier_score"] for _, x in scored) / len(scored)
        mean_loss = sum(x["log_loss"] for _, x in scored) / len(scored)
        base_brier = sum(x["baseline_brier_score"] for _, x in scored) / len(scored)
        base_loss = sum(x["baseline_log_loss"] for _, x in scored) / len(scored)
        bins: dict[int, list[float]] = {}
        for forecast, outcome in scored:
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
            weighted_error += count / len(scored) * gap
            calibration.append({
                "lower_bound": index / 10, "upper_bound": (index + 1) / 10,
                "count": int(count), "mean_confidence": mean_conf,
                "observed_accuracy": observed, "absolute_gap": gap,
            })
        return {
            "forecasts": total, "resolved": len(resolved), "scored": len(scored),
            "unscorable": sum(x["status"] == "unscorable" for x in resolved),
            "unresolved": total - len(resolved), "directional_accuracy": accuracy,
            "mean_brier_score": mean_brier, "mean_log_loss": mean_loss,
            "baseline_directional_accuracy": baseline_accuracy,
            "baseline_mean_brier_score": base_brier, "baseline_mean_log_loss": base_loss,
            "brier_improvement_vs_baseline": base_brier - mean_brier,
            "calibration_bins": calibration, "weighted_calibration_error": weighted_error,
            "scoring_method": "three_class_brier_mean_squared_error_v1",
        }

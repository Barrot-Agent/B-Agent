"""
MCP Kaggle Client
=================
Integrates Kaggle competitions into the B-Agent MCP ecosystem.
Provides a class-based interface that mirrors the style of
:mod:`mcp_huggingface` and :mod:`mcp_databricks`.

Responsibilities
----------------
* Authenticate against the Kaggle API.
* List active competitions the user can participate in.
* Download competition datasets into a configurable data directory.
* Train a lightweight baseline model and generate predictions.
* Submit the predictions CSV to the competition leaderboard.
* Track per-competition state so callers can report progress.

Authentication
--------------
Credentials are resolved from (in priority order):

1. Constructor arguments ``username`` / ``key``.
2. Environment variables ``KAGGLE_USERNAME`` / ``KAGGLE_KEY``.
3. ``~/.kaggle/kaggle.json`` or ``$KAGGLE_CONFIG_DIR/kaggle.json``.

Usage
-----
    from mcp_kaggle import KaggleMCP

    kg = KaggleMCP(username="alice", key="abc123")
    for event in kg.run_competitions(max_competitions=3):
        print(event.competition, event.status)
"""

from __future__ import annotations

import io
import json
import logging
import os
import time
import zipfile
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_DATA_DIR = Path(os.environ.get("KAGGLE_DATA_DIR", "/tmp/kaggle_data"))
_DEFAULT_MAX_COMPETITIONS = int(os.environ.get("KAGGLE_MAX_COMPETITIONS", "5"))
_DEFAULT_SUBMISSION_MESSAGE = os.environ.get(
    "KAGGLE_SUBMISSION_MESSAGE",
    "Baseline submission via B-Agent MCP",
)
# Number of unique target values above which the problem is treated as
# regression rather than classification.
_MAX_UNIQUE_FOR_CLASSIFICATION = 20


# ---------------------------------------------------------------------------
# Status types
# ---------------------------------------------------------------------------

class CompetitionStatus(str, Enum):
    PENDING     = "pending"
    DOWNLOADING = "downloading"
    TRAINING    = "training"
    PREDICTING  = "predicting"
    SUBMITTING  = "submitting"
    COMPLETE    = "complete"
    SKIPPED     = "skipped"
    ERROR       = "error"


@dataclass
class CompetitionState:
    """Tracks the lifecycle of a single competition run."""
    competition: str
    status: CompetitionStatus = CompetitionStatus.PENDING
    submission_path: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    @property
    def elapsed(self) -> Optional[float]:
        if self.started_at is None:
            return None
        end = self.completed_at or time.time()
        return end - self.started_at


@dataclass
class KaggleRunEvent:
    """Progress event yielded during :meth:`KaggleMCP.run_competitions`."""
    competition: str
    status: CompetitionStatus
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @property
    def is_error(self) -> bool:
        return self.status == CompetitionStatus.ERROR

    @property
    def is_complete(self) -> bool:
        return self.status in (CompetitionStatus.COMPLETE, CompetitionStatus.SKIPPED)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class KaggleMCP:
    """MCP client for Kaggle competition automation."""

    def __init__(
        self,
        username: Optional[str] = None,
        key: Optional[str] = None,
        data_dir: Optional[Path] = None,
        submission_message: str = _DEFAULT_SUBMISSION_MESSAGE,
    ) -> None:
        self._username = username or os.environ.get("KAGGLE_USERNAME", "")
        self._key = key or os.environ.get("KAGGLE_KEY", "")
        self._data_dir = Path(data_dir) if data_dir else _DEFAULT_DATA_DIR
        self._submission_message = submission_message
        self._states: Dict[str, CompetitionState] = {}
        self._api: Optional[Any] = None

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def _ensure_credentials_file(self) -> None:
        """Write credentials to ~/.kaggle/kaggle.json when env vars are set."""
        if self._username and self._key:
            kaggle_dir = Path.home() / ".kaggle"
            kaggle_dir.mkdir(exist_ok=True)
            cfg_file = kaggle_dir / "kaggle.json"
            cfg_file.write_text(
                json.dumps({"username": self._username, "key": self._key}),
                encoding="utf-8",
            )
            cfg_file.chmod(0o600)

    def _load_api(self) -> Optional[Any]:
        """Lazily build the Kaggle API client; returns None when unavailable."""
        try:
            from kaggle.api.kaggle_api_extended import KaggleApiExtended  # noqa: F401
            self._ensure_credentials_file()
            api = KaggleApiExtended()
            api.authenticate()
            return api
        except ImportError:
            logger.warning(
                "kaggle package not installed. Install with: pip install kaggle"
            )
            return None
        except Exception as exc:
            logger.warning("Kaggle authentication failed: %s", exc)
            return None

    def _get_api(self) -> Optional[Any]:
        if self._api is None:
            self._api = self._load_api()
        return self._api

    def is_configured(self) -> bool:
        """Return True when at least one credential source is available."""
        if self._username and self._key:
            return True
        kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
        return kaggle_json.exists()

    def token_ok(self) -> bool:
        """Return True when the Kaggle API authenticates successfully."""
        return self._get_api() is not None

    # ------------------------------------------------------------------
    # Competition helpers
    # ------------------------------------------------------------------

    def list_competitions(self, max_competitions: int = _DEFAULT_MAX_COMPETITIONS) -> List[str]:
        """Return up to *max_competitions* active competition slugs."""
        api = self._get_api()
        if api is None:
            logger.warning("Kaggle API unavailable; returning empty competition list.")
            return []
        try:
            comps = api.competitions_list(sort_by="latestDeadline")
            active = [
                c.ref if hasattr(c, "ref") else str(c)
                for c in comps
                if not getattr(c, "isKernelsSubmissionsOnly", False)
            ]
            logger.info(
                "Found %d active Kaggle competitions (capping at %d).",
                len(active), max_competitions,
            )
            return active[:max_competitions]
        except Exception as exc:
            logger.error("list_competitions failed: %s", exc)
            return []

    def download_dataset(self, competition: str) -> bool:
        """
        Download *competition* files into ``data_dir/competition/``.

        Returns False when the user has not accepted the rules or the
        download fails for any other reason.
        """
        api = self._get_api()
        if api is None:
            return False

        dest = self._data_dir / competition
        dest.mkdir(parents=True, exist_ok=True)

        state = self._get_state(competition)
        state.status = CompetitionStatus.DOWNLOADING

        try:
            api.competition_download_files(competition, path=str(dest), quiet=False)
            # Unzip any archives
            for zf_path in dest.glob("*.zip"):
                with zipfile.ZipFile(zf_path, "r") as zf:
                    zf.extractall(dest)
                zf_path.unlink()
            logger.info("Downloaded data for competition '%s' to %s", competition, dest)
            return True
        except Exception as exc:
            logger.warning("Download failed for '%s': %s", competition, exc)
            state.error_message = str(exc)
            return False

    def train_and_predict(self, competition: str) -> Optional[Path]:
        """
        Fit a baseline model on downloaded training data and write a
        ``submission.csv`` to ``data_dir/competition/``.

        Returns the submission path or None on failure.
        """
        try:
            import pandas as pd
            from sklearn.dummy import DummyClassifier, DummyRegressor
            from sklearn.preprocessing import LabelEncoder
        except ImportError as exc:
            logger.warning("sklearn / pandas unavailable: %s", exc)
            return None

        comp_dir = self._data_dir / competition
        state = self._get_state(competition)
        state.status = CompetitionStatus.TRAINING

        train_csv = self._find_csv(comp_dir)
        sample_sub = self._find_sample_submission(comp_dir)

        if train_csv is None or sample_sub is None:
            logger.warning(
                "Cannot locate train.csv or sample_submission.csv in %s", comp_dir
            )
            state.error_message = "Missing train.csv or sample_submission.csv"
            return None

        try:
            train_df = pd.read_csv(train_csv)
            sample_df = pd.read_csv(sample_sub)
        except Exception as exc:
            logger.warning("CSV read error: %s", exc)
            state.error_message = str(exc)
            return None

        if train_df.shape[1] < 2:
            logger.warning("Training file has fewer than 2 columns – skipping.")
            state.error_message = "Training file has fewer than 2 columns"
            return None

        target_col = train_df.columns[-1]
        feature_cols = [c for c in train_df.columns if c != target_col]
        X_train = train_df[feature_cols].select_dtypes(include="number").fillna(0)
        y_train = train_df[target_col]

        is_classification = (
            y_train.dtype == object
            or y_train.nunique(dropna=True) < _MAX_UNIQUE_FOR_CLASSIFICATION
        )

        state.status = CompetitionStatus.PREDICTING
        if is_classification:
            le = LabelEncoder()
            # Drop NaN before fitting to avoid 'nan' being treated as a class label
            y_clean = y_train.dropna()
            X_clean = X_train.loc[y_clean.index]
            y_enc = le.fit_transform(y_clean.astype(str))
            model = DummyClassifier(strategy="most_frequent")
            model.fit(X_clean, y_enc)
        else:
            model = DummyRegressor(strategy="mean")
            model.fit(X_train, y_train.fillna(y_train.median()))

        pred_cols = [c for c in sample_df.columns if c != sample_df.columns[0]]
        if not pred_cols:
            logger.warning("Cannot identify prediction column in sample submission.")
            state.error_message = "No prediction column found in sample submission"
            return None
        # Use the first non-ID column as the prediction target (standard Kaggle format).
        # For multi-target competitions, extend this to handle multiple pred columns.
        pred_col = pred_cols[0]

        n_rows = len(sample_df)
        # Build a zero-filled feature matrix — this is an intentionally naive baseline.
        # The DummyClassifier/DummyRegressor ignores features and always predicts the
        # majority class / mean, so feature values do not affect the output.
        X_pred = pd.DataFrame(0, index=range(n_rows), columns=X_train.columns)
        raw_preds = model.predict(X_pred)
        if is_classification:
            raw_preds = le.inverse_transform(raw_preds)

        sample_df[pred_col] = raw_preds
        out_path = comp_dir / "submission.csv"
        sample_df.to_csv(out_path, index=False)
        logger.info("Submission file written: %s", out_path)
        state.submission_path = str(out_path)
        return out_path

    def submit(self, competition: str, submission_path: Path) -> bool:
        """
        Upload *submission_path* to *competition*.

        Returns True on success, False on failure.
        """
        api = self._get_api()
        if api is None:
            return False

        state = self._get_state(competition)
        state.status = CompetitionStatus.SUBMITTING

        try:
            api.competition_submit(
                file_name=str(submission_path),
                message=self._submission_message,
                competition=competition,
            )
            logger.info("Submitted to '%s'", competition)
            return True
        except Exception as exc:
            logger.warning("Submission to '%s' failed: %s", competition, exc)
            state.error_message = str(exc)
            return False

    # ------------------------------------------------------------------
    # High-level: run multiple competitions, yielding progress events
    # ------------------------------------------------------------------

    def run_competitions(
        self,
        max_competitions: int = _DEFAULT_MAX_COMPETITIONS,
    ) -> Generator[KaggleRunEvent, None, None]:
        """
        Run the full download → train → submit pipeline for up to
        *max_competitions* active competitions.

        Yields :class:`KaggleRunEvent` instances for streaming UIs.
        """
        if not self.is_configured():
            yield KaggleRunEvent(
                competition="(none)",
                status=CompetitionStatus.ERROR,
                message="Kaggle credentials not configured",
                error="Set KAGGLE_USERNAME and KAGGLE_KEY env vars",
            )
            return

        competitions = self.list_competitions(max_competitions)
        if not competitions:
            yield KaggleRunEvent(
                competition="(none)",
                status=CompetitionStatus.SKIPPED,
                message="No active Kaggle competitions found",
            )
            return

        for comp in competitions:
            state = self._get_state(comp)
            state.started_at = time.time()

            # --- Download ---
            yield KaggleRunEvent(
                competition=comp,
                status=CompetitionStatus.DOWNLOADING,
                message=f"Downloading dataset for '{comp}'…",
            )
            if not self.download_dataset(comp):
                state.status = CompetitionStatus.SKIPPED
                state.completed_at = time.time()
                yield KaggleRunEvent(
                    competition=comp,
                    status=CompetitionStatus.SKIPPED,
                    message=f"Skipped '{comp}' — download failed (rules not accepted?)",
                    error=state.error_message,
                )
                continue

            # --- Train & predict ---
            yield KaggleRunEvent(
                competition=comp,
                status=CompetitionStatus.TRAINING,
                message=f"Training baseline model for '{comp}'…",
            )
            submission_path = self.train_and_predict(comp)
            if submission_path is None:
                state.status = CompetitionStatus.SKIPPED
                state.completed_at = time.time()
                yield KaggleRunEvent(
                    competition=comp,
                    status=CompetitionStatus.SKIPPED,
                    message=f"Skipped '{comp}' — could not generate predictions",
                    error=state.error_message,
                )
                continue

            # --- Submit ---
            yield KaggleRunEvent(
                competition=comp,
                status=CompetitionStatus.SUBMITTING,
                message=f"Submitting predictions for '{comp}'…",
            )
            ok = self.submit(comp, submission_path)
            state.status = CompetitionStatus.COMPLETE if ok else CompetitionStatus.ERROR
            state.completed_at = time.time()
            yield KaggleRunEvent(
                competition=comp,
                status=state.status,
                message=(
                    f"✅ Submitted to '{comp}'"
                    if ok
                    else f"❌ Submission failed for '{comp}'"
                ),
                details={"submission_path": str(submission_path)},
                error=None if ok else state.error_message,
            )

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def _get_state(self, competition: str) -> CompetitionState:
        if competition not in self._states:
            self._states[competition] = CompetitionState(competition=competition)
        return self._states[competition]

    def get_competition_state(self, competition: str) -> CompetitionState:
        """Return the current state for *competition*."""
        return self._get_state(competition)

    def all_states(self) -> Dict[str, CompetitionState]:
        """Return a snapshot of all tracked competition states."""
        return dict(self._states)

    # ------------------------------------------------------------------
    # Path utilities (internal)
    # ------------------------------------------------------------------

    @staticmethod
    def _find_csv(directory: Path) -> Optional[Path]:
        for candidate in ("train.csv", "training.csv", "train_features.csv"):
            p = directory / candidate
            if p.exists():
                return p
        csvs = sorted(directory.glob("*.csv"))
        return csvs[0] if csvs else None

    @staticmethod
    def _find_sample_submission(directory: Path) -> Optional[Path]:
        for candidate in ("sample_submission.csv", "sampleSubmission.csv"):
            p = directory / candidate
            if p.exists():
                return p
        return None

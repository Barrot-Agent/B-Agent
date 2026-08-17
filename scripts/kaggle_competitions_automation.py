"""
kaggle_competitions_automation.py
==================================
Automates participation in Kaggle competitions using the official Kaggle API.

For each active competition where the authenticated user has already accepted
the rules, the script will:
  1. Download the competition dataset.
  2. Train a simple baseline model.
  3. Generate predictions.
  4. Submit the predictions file.

NOTE: You must manually accept a competition's rules on kaggle.com before this
script can download data or submit.  Programmatic rule-acceptance is not
supported by the Kaggle API.

Authentication is resolved from environment variables:
    KAGGLE_USERNAME  – Kaggle account username
    KAGGLE_KEY       – Kaggle API key

Or from ~/.kaggle/kaggle.json / $KAGGLE_CONFIG_DIR/kaggle.json.
"""

import io
import logging
import os
import sys
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd
from kaggle.api.kaggle_api_extended import KaggleApiExtended
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = Path(os.environ.get("KAGGLE_DATA_DIR", "/tmp/kaggle_data"))
MAX_COMPETITIONS = int(os.environ.get("KAGGLE_MAX_COMPETITIONS", "5"))
SUBMISSION_MESSAGE = os.environ.get(
    "KAGGLE_SUBMISSION_MESSAGE", "Baseline submission via B-Agent automation"
)

# Maximum number of unique target values before a column is treated as
# a regression target rather than a classification target.
MAX_UNIQUE_VALUES_FOR_CLASSIFICATION = 20


# ---------------------------------------------------------------------------
# Kaggle API helpers
# ---------------------------------------------------------------------------


def _build_api() -> KaggleApiExtended:
    """
    Initialise the Kaggle API client.
    Credentials are read from environment variables or from kaggle.json.
    """
    username = os.environ.get("KAGGLE_USERNAME", "")
    key = os.environ.get("KAGGLE_KEY", "")
    if username and key:
        # Write credentials to the expected location so the SDK picks them up
        import json

        kaggle_dir = Path.home() / ".kaggle"
        kaggle_dir.mkdir(exist_ok=True)
        cfg_file = kaggle_dir / "kaggle.json"
        cfg_file.write_text(json.dumps({"username": username, "key": key}))
        cfg_file.chmod(0o600)

    api = KaggleApiExtended()
    api.authenticate()
    return api


def _list_active_competitions(api: KaggleApiExtended) -> list:
    """Return competitions that are still accepting submissions."""
    comps = api.competitions_list(sort_by="latestDeadline")
    active = [c for c in comps if not getattr(c, "isKernelsSubmissionsOnly", False)]
    log.info("Found %d active competitions (showing up to %d).", len(active), MAX_COMPETITIONS)
    return active[:MAX_COMPETITIONS]


def _download_data(api: KaggleApiExtended, competition: str, dest: Path) -> bool:
    """
    Download competition files.  Returns False if the user has not yet
    accepted the competition rules (access denied).
    """
    dest.mkdir(parents=True, exist_ok=True)
    try:
        api.competition_download_files(competition, path=str(dest), quiet=False)
        # Unzip any downloaded archives
        for zf in dest.glob("*.zip"):
            with zipfile.ZipFile(zf, "r") as z:
                z.extractall(dest)
            zf.unlink()
        return True
    except Exception as exc:
        log.warning("Could not download data for %s: %s", competition, exc)
        return False


def _find_csv(directory: Path) -> Optional[Path]:
    """Return the first CSV file that looks like a training set."""
    for candidate in ("train.csv", "training.csv", "train_features.csv"):
        p = directory / candidate
        if p.exists():
            return p
    csvs = sorted(directory.glob("*.csv"))
    return csvs[0] if csvs else None


def _find_sample_submission(directory: Path) -> Optional[Path]:
    """Return the sample submission CSV if present."""
    for candidate in ("sample_submission.csv", "sampleSubmission.csv"):
        p = directory / candidate
        if p.exists():
            return p
    return None


def _train_and_predict(comp_dir: Path) -> Optional[Path]:
    """
    Fit a simple baseline model on the training data and generate predictions
    for the test / sample-submission IDs.  Returns the path to the submission
    CSV, or None if the data could not be parsed.
    """
    train_csv = _find_csv(comp_dir)
    sample_sub = _find_sample_submission(comp_dir)

    if train_csv is None or sample_sub is None:
        log.warning("Cannot locate train.csv or sample_submission.csv in %s", comp_dir)
        return None

    try:
        train_df = pd.read_csv(train_csv)
        sample_df = pd.read_csv(sample_sub)
    except Exception as exc:
        log.warning("CSV read error: %s", exc)
        return None

    # Heuristic: target is the last column of the training file
    if train_df.shape[1] < 2:
        log.warning("Training file has fewer than 2 columns – skipping.")
        return None

    target_col = train_df.columns[-1]
    feature_cols = [c for c in train_df.columns if c != target_col]

    # Keep only numeric features for simplicity
    X_train = train_df[feature_cols].select_dtypes(include="number").fillna(0)
    y_train = train_df[target_col]

    is_classification = (
        y_train.dtype == object or y_train.nunique() < MAX_UNIQUE_VALUES_FOR_CLASSIFICATION
    )
    if is_classification:
        le = LabelEncoder()
        y_enc = le.fit_transform(y_train.astype(str))
        model = DummyClassifier(strategy="most_frequent")
        model.fit(X_train, y_enc)
    else:
        model = DummyRegressor(strategy="mean")
        model.fit(X_train, y_train)

    # Build prediction data frame aligned with sample submission
    pred_col = [c for c in sample_df.columns if c != sample_df.columns[0]]
    if not pred_col:
        log.warning("Cannot identify prediction column in sample submission.")
        return None
    pred_col = pred_col[0]

    n_rows = len(sample_df)
    X_pred = pd.DataFrame(0, index=range(n_rows), columns=X_train.columns)
    raw_preds = model.predict(X_pred)

    if is_classification:
        raw_preds = le.inverse_transform(raw_preds)

    sample_df[pred_col] = raw_preds
    out_path = comp_dir / "submission.csv"
    sample_df.to_csv(out_path, index=False)
    log.info("Submission file written: %s", out_path)
    return out_path


def _submit(api: KaggleApiExtended, competition: str, submission_path: Path) -> None:
    try:
        api.competition_submit(
            file_name=str(submission_path),
            message=SUBMISSION_MESSAGE,
            competition=competition,
        )
        log.info("✅ Submitted to %s", competition)
    except Exception as exc:
        log.warning("Submission to %s failed: %s", competition, exc)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    api = _build_api()
    competitions = _list_active_competitions(api)

    results: list[dict] = []
    for comp in competitions:
        name = comp.ref if hasattr(comp, "ref") else str(comp)
        log.info("─── Processing competition: %s ───", name)
        comp_dir = DATA_DIR / name

        if not _download_data(api, name, comp_dir):
            results.append({"competition": name, "status": "skipped (rules not accepted)"})
            continue

        submission_path = _train_and_predict(comp_dir)
        if submission_path is None:
            results.append({"competition": name, "status": "skipped (data parse error)"})
            continue

        _submit(api, name, submission_path)
        results.append({"competition": name, "status": "submitted"})

    log.info("\n=== Summary ===")
    for r in results:
        log.info("  %-50s  %s", r["competition"], r["status"])

    log.info("✅ Kaggle automation run complete.")


if __name__ == "__main__":
    main()

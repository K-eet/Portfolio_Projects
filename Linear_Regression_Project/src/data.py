"""Download, extract, and load the Open University Learning Analytics Dataset.

The dataset is described at https://analyse.kmi.open.ac.uk/open_dataset
and is published under CC-BY 4.0.

As of September 2026 the download link on the Open University site returns
an HTTP 404, and the dataset page itself redirects to a general landing page.
The same archive, deposited by the dataset authors, is served by the UC Irvine
Machine Learning Repository as dataset 349. This module downloads from UCI and
verifies the archive against a known SHA-256 so that a substituted or truncated
file is caught rather than silently analysed.

Run directly to fetch the data and print a summary of every table:

    python -m src.data
"""

from __future__ import annotations

import hashlib
import shutil
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

# Where the dataset is documented. Cite this, not the mirror.
OULAD_HOME = "https://analyse.kmi.open.ac.uk/open_dataset"

# Where the archive is actually retrievable.
DOWNLOAD_URL = (
    "https://archive.ics.uci.edu/static/public/349/"
    "open+university+learning+analytics+dataset.zip"
)

# Verified 2026-09-17. A mismatch means the file changed; stop and investigate.
EXPECTED_SHA256 = "f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4"

ARCHIVE_NAME = "oulad.zip"

# Missing values are encoded as a literal "?" throughout OULAD, not as blanks.
NA_VALUES = ["?"]

# Explicit dtypes keep studentVle (10.6 million rows) inside a few hundred MB
# and stop pandas inferring float64 for columns that are conceptually integers.
DTYPES: dict[str, dict[str, str]] = {
    "studentInfo": {
        "code_module": "category",
        "code_presentation": "category",
        "id_student": "int32",
        "gender": "category",
        "region": "category",
        "highest_education": "category",
        "imd_band": "object",  # cleaned into an ordered category in src/clean.py
        "age_band": "category",
        "num_of_prev_attempts": "int8",
        "studied_credits": "int16",
        "disability": "category",
        "final_result": "category",
    },
    "studentVle": {
        "code_module": "category",
        "code_presentation": "category",
        "id_student": "int32",
        "id_site": "int32",
        "date": "int16",  # negative before the module starts
        "sum_click": "int16",
    },
    "studentRegistration": {
        "code_module": "category",
        "code_presentation": "category",
        "id_student": "int32",
    },
    "studentAssessment": {
        "id_assessment": "int32",
        "id_student": "int32",
        "date_submitted": "int16",
        "is_banked": "int8",
    },
    "assessments": {
        "code_module": "category",
        "code_presentation": "category",
        "id_assessment": "int32",
        "assessment_type": "category",
    },
    "courses": {
        "code_module": "category",
        "code_presentation": "category",
        "module_presentation_length": "int16",
    },
    "vle": {
        "id_site": "int32",
        "code_module": "category",
        "code_presentation": "category",
        "activity_type": "category",
    },
}

TABLES = tuple(DTYPES)


def _sha256(path: Path) -> str:
    """Return the SHA-256 of a file, read in chunks to bound memory."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def download_archive(data_dir: Path, force: bool = False) -> Path:
    """Download the OULAD archive into ``data_dir`` and verify it.

    The file is written to a temporary name and renamed only once it is
    complete, so an interrupted download can never be mistaken for a good
    cached copy on a later run.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    archive = data_dir / ARCHIVE_NAME

    if archive.exists() and not force:
        if _sha256(archive) == EXPECTED_SHA256:
            print(f"Archive already present and verified: {archive}")
            return archive
        print("Cached archive failed its checksum. Downloading again.")

    print(f"Downloading from {DOWNLOAD_URL}")
    partial = archive.with_suffix(".zip.part")
    with urllib.request.urlopen(DOWNLOAD_URL, timeout=120) as response:
        with partial.open("wb") as handle:
            shutil.copyfileobj(response, handle)

    # The Open University URL serves an HTML page from a path ending in .zip.
    # Check the magic bytes so that failure mode produces a clear message.
    with partial.open("rb") as handle:
        if handle.read(4) != b"PK\x03\x04":
            partial.unlink(missing_ok=True)
            raise RuntimeError(
                f"{DOWNLOAD_URL} did not return a zip archive. "
                "The server most likely returned an HTML error page."
            )

    actual = _sha256(partial)
    if actual != EXPECTED_SHA256:
        partial.unlink(missing_ok=True)
        raise RuntimeError(
            "Downloaded archive does not match the expected checksum.\n"
            f"  expected {EXPECTED_SHA256}\n"
            f"  actual   {actual}\n"
            "The published file may have changed. Do not analyse it until "
            "you know why."
        )

    partial.rename(archive)
    print(f"Downloaded and verified {archive.stat().st_size / 1e6:.1f} MB")
    return archive


def extract_archive(archive: Path, data_dir: Path) -> None:
    """Extract the CSV files from the archive, skipping any already present."""
    with zipfile.ZipFile(archive) as zf:
        members = [n for n in zf.namelist() if n.endswith(".csv")]
        missing = [n for n in members if not (data_dir / n).exists()]
        if not missing:
            print(f"All {len(members)} CSV files already extracted.")
            return
        print(f"Extracting {len(missing)} CSV files to {data_dir}")
        zf.extractall(data_dir, members=missing)


def ensure_data(data_dir: Path | str = "data") -> Path:
    """Make sure the extracted CSV files are on disk. Returns the data directory."""
    data_dir = Path(data_dir)
    archive = download_archive(data_dir)
    extract_archive(archive, data_dir)
    return data_dir


def load_table(name: str, data_dir: Path | str = "data") -> pd.DataFrame:
    """Load one OULAD table with correct dtypes and missing-value handling."""
    if name not in DTYPES:
        raise KeyError(f"Unknown table {name!r}. Expected one of {TABLES}.")
    path = Path(data_dir) / f"{name}.csv"
    return pd.read_csv(path, dtype=DTYPES[name], na_values=NA_VALUES)


def load_all(data_dir: Path | str = "data") -> dict[str, pd.DataFrame]:
    """Load every OULAD table into a dictionary keyed by table name."""
    return {name: load_table(name, data_dir) for name in TABLES}


def summarise(tables: dict[str, pd.DataFrame]) -> None:
    """Print the shape and the missing value count of every column."""
    for name, df in tables.items():
        rows, cols = df.shape
        print(f"\n{name}  ({rows:,} rows x {cols} columns)")
        missing = df.isna().sum()
        for column in df.columns:
            count = int(missing[column])
            share = count / rows * 100 if rows else 0.0
            flag = "" if count == 0 else f"   <- {share:.1f}% missing"
            print(f"    {column:<28} {str(df[column].dtype):<10} {count:>9,}{flag}")


def main() -> None:
    data_dir = ensure_data()
    print("\nLoading tables. studentVle is large and takes a moment.")
    summarise(load_all(data_dir))


if __name__ == "__main__":
    main()

"""
get_data.py
Download the Companies House monthly snapshot and cut it down to the segment.

The source file is ~400MB zipped and ~2GB as CSV across roughly 5 million
companies, which is too large to commit and too slow to re-read on every
iteration. This script does the expensive pass once — stream, filter, discard —
and writes data/segment.csv, a few thousand rows that the rest of the pipeline
and the notebook can load in a second.

Re-run this only when the segment definition in config.py changes (SIC codes or
geography). Changing the *weights* does not require a re-run: the filter and
the score are separate steps on purpose.

Usage:  python get_data.py
"""

import os
import zipfile

import pandas as pd
import requests

import config
from scoring import parse_sic_code

# 15 of the 55 columns. Naming them explicitly keeps peak memory in the low
# hundreds of MB rather than several GB, and documents what the score is
# allowed to see.
WANTED_COLUMNS = [
    "CompanyName",
    "CompanyNumber",
    "RegAddress.AddressLine1",
    "RegAddress.PostTown",
    "RegAddress.PostCode",
    "CompanyCategory",
    "CompanyStatus",
    "IncorporationDate",
    "Accounts.NextDueDate",
    "Accounts.LastMadeUpDate",
    "Accounts.AccountCategory",
    "ConfStmtNextDueDate",
    "Mortgages.NumMortCharges",
    "Mortgages.NumMortOutstanding",
    "SICCode.SicText_1",
    "SICCode.SicText_2",
    "SICCode.SicText_3",
    "SICCode.SicText_4",
]

CHUNK_ROWS = 250_000


def download(url, destination):
    """Stream the snapshot to disk, skipping if it is already there."""
    if os.path.exists(destination):
        size_mb = os.path.getsize(destination) / 1e6
        print(f"Using cached {destination} ({size_mb:,.0f} MB)")
        return

    print(f"Downloading {url}")
    print("~400 MB — this takes a few minutes.")
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        written = 0
        with open(destination, "wb") as handle:
            for block in response.iter_content(chunk_size=1 << 20):
                handle.write(block)
                written += len(block)
                if written % (50 << 20) < (1 << 20):
                    print(f"  {written / 1e6:,.0f} MB")
    print(f"Wrote {destination} ({os.path.getsize(destination) / 1e6:,.0f} MB)")


def postcode_area(postcode):
    """The letter prefix of a UK postcode: 'SW1A 1AA' -> 'SW'.

    This is the outward code's alphabetic head, which is what identifies the
    London postal district group. Returns '' for blanks and malformed values.
    """
    text = str(postcode or "").strip().upper()
    letters = ""
    for character in text:
        if character.isalpha():
            letters += character
        else:
            break
    return letters


def is_in_segment(row):
    """Does this company belong in the target segment at all?

    Three gates, all cheap, applied before any scoring: the company must be
    trading, be registered in a London postal district, and declare at least
    one SIC code the vendor's product speaks to. Everything that survives is
    then *ranked* by score — the filter decides membership, the score decides
    order.
    """
    if str(row["CompanyStatus"]).strip() != "Active":
        return False

    if postcode_area(row["RegAddress.PostCode"]) not in config.LONDON_POSTCODE_AREAS:
        return False

    for column in ("SICCode.SicText_1", "SICCode.SicText_2",
                   "SICCode.SicText_3", "SICCode.SicText_4"):
        if parse_sic_code(row[column]) in config.SIC_RELEVANCE:
            return True
    return False


def main():
    os.makedirs(config.RAW_DIR, exist_ok=True)
    zip_path = os.path.join(config.RAW_DIR, os.path.basename(config.BULK_URL))
    download(config.BULK_URL, zip_path)

    with zipfile.ZipFile(zip_path) as archive:
        csv_name = next(n for n in archive.namelist() if n.lower().endswith(".csv"))
        print(f"Reading {csv_name} in {CHUNK_ROWS:,}-row chunks ...")

        kept = []
        scanned = 0
        with archive.open(csv_name) as handle:
            # Several header fields carry a leading space in the published
            # file, so match on the stripped name and rename after reading.
            reader = pd.read_csv(
                handle,
                chunksize=CHUNK_ROWS,
                usecols=lambda name: name.strip() in WANTED_COLUMNS,
                dtype=str,
                encoding="latin-1",
                # The September 2026 snapshot contains at least one row with an
                # extra field (company 08652773, reported on the Companies
                # House developer forum). Skipping it loses one company from
                # five million rather than aborting the run.
                on_bad_lines="skip",
            )
            for chunk in reader:
                chunk.columns = [c.strip() for c in chunk.columns]
                scanned += len(chunk)
                kept.append(chunk[chunk.apply(is_in_segment, axis=1)])
                print(f"  scanned {scanned:,} — kept {sum(len(k) for k in kept):,}")

    segment = pd.concat(kept, ignore_index=True)
    segment.to_csv(config.SEGMENT_CSV, index=False, encoding="utf-8")
    print(f"\nWrote {config.SEGMENT_CSV}: {len(segment):,} companies "
          f"from {scanned:,} scanned ({len(segment) / scanned:.3%} of the register)")


if __name__ == "__main__":
    main()

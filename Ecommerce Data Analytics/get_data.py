"""Download the source dataset and write data.csv in the format the notebooks expect.

The Online Retail dataset (541,909 rows) is too large to commit. This fetches it
from the UCI ML Repository (no login required) and reproduces the CSV layout the
notebooks read: string InvoiceDate as %m/%d/%Y %H:%M, UTF-8 encoding.

Run once before the notebooks:  python get_data.py
"""
import io
import urllib.request
import zipfile

import pandas as pd

URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"


def main():
    print(f"Downloading {URL} ...")
    raw = urllib.request.urlopen(URL, timeout=120).read()
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        xlsx_name = next(n for n in z.namelist() if n.lower().endswith(".xlsx"))
        df = pd.read_excel(z.open(xlsx_name), engine="openpyxl")

    # Notebook 1 parses InvoiceDate with format="%m/%d/%Y %H:%M", so serialize to match.
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"]).dt.strftime("%m/%d/%Y %H:%M")
    df.to_csv("data.csv", index=False, encoding="utf-8")
    print(f"Wrote data.csv: {len(df):,} rows x {df.shape[1]} columns")


if __name__ == "__main__":
    main()

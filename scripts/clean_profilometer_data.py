#!/usr/bin/env python3
import sys
from pathlib import Path
import pandas as pd
import numpy as np

def clean_profilometer_csv(input_path: Path, sep: str, skiprows: int) -> pd.DataFrame:
    """
    Load a raw profilometer CSV, strip metadata + 'Å', convert Height → µm, drop bad rows.
    """
    df = pd.read_csv(
        input_path,
        sep=sep,
        skiprows=skiprows,
        usecols=[0,1],
        names=["Position","Height_raw"],
        header=0,
        encoding="latin1",
        engine="python",
    )
    df["Height"] = (
        pd.to_numeric(
            df["Height_raw"]
              .astype(str)
              .str.replace(r"[^0-9\.\-]", "", regex=True)
              .str.strip(),
            errors="coerce"
        )
    )
    return df.dropna(subset=["Height"])[["Position","Height"]].reset_index(drop=True)

def main():
    project_root = Path(__file__).parent.parent
    raw_dir  = project_root / "data" / "profilometer" / "raw"
    proc_dir = project_root / "data" / "profilometer" / "processed"
    proc_dir.mkdir(parents=True, exist_ok=True)

    # Define your files and how to parse them
    file_params = {
        "7s.csv":  {"sep": ",",  "skiprows": 12},
        "40s.csv": {"sep": "\t", "skiprows": 12}
    }

    # CLEAN step
    for fname, cfg in file_params.items():
        infile  = raw_dir  / fname
        outfile = proc_dir / fname

        df_clean = clean_profilometer_csv(
            infile,
            sep=cfg["sep"],
            skiprows=cfg["skiprows"]
        )
        df_clean.to_csv(outfile, index=False)
        print(f"Cleaned {fname}: {len(df_clean)} rows → {outfile}")

    # VALIDATION step
    tol = 1e-6  # µm tolerance for height comparison
    all_passed = True

    for fname, cfg in file_params.items():
        infile   = raw_dir  / fname
        cleaned_mem = clean_profilometer_csv(
            infile,
            sep=cfg["sep"],
            skiprows=cfg["skiprows"]
        )
        proc_df = pd.read_csv(proc_dir / fname)

        # Reset indices for 1-to-1 comparison
        cleaned_mem = cleaned_mem.reset_index(drop=True)
        proc_df     = proc_df.reset_index(drop=True)

        # Check row counts
        if len(cleaned_mem) != len(proc_df):
            print(f" {fname}: Row count mismatch raw→proc: {len(cleaned_mem)} vs {len(proc_df)}")
            all_passed = False

        # Check Position column
        if not cleaned_mem["Position"].equals(proc_df["Position"]):
            print(f" {fname}: Position column mismatch")
            all_passed = False

        # Check Height within tolerance
        diffs = np.abs(cleaned_mem["Height"] - proc_df["Height"])
        maxdiff = diffs.max()
        if maxdiff > tol:
            idx = diffs.idxmax()
            print(f" {fname}: Height mismatch max diff = {maxdiff:.2e} µm at row {idx}")
            print("   raw:", cleaned_mem.iloc[idx].to_dict())
            print("  proc:", proc_df.iloc[idx].to_dict())
            all_passed = False
        else:
            print(f" {fname}: Height match within {tol} µm (max diff {maxdiff:.2e})")

    if all_passed:
        print("\n All files cleaned and validated successfully!")
        sys.exit(0)
    else:
        print("\n Some validation checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
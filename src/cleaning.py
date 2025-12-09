# src/cleaning.py
from pathlib import Path
import pandas as pd

from .scoring import add_question_scores, add_summary_scores


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "Psychology Study Results.xlsx"
PROCESSED_PATH = ROOT / "data" / "processed" / "study_results_clean.csv"


def load_and_combine() -> pd.DataFrame:
    SHEET_MAP = {
        "CG": "Psychology Study - CG",
        "EG": "Psychology Study - EG",
    }
    frames = []
    for group_code, sheet_name in SHEET_MAP.items():
        df_sheet = pd.read_excel(RAW_PATH, sheet_name=sheet_name)

        # Keep only real participant rows: Timestamp must be a valid datetime
        if "Timestamp" in df_sheet.columns:
            mask = pd.to_datetime(df_sheet["Timestamp"], errors="coerce").notna()
            df_sheet = df_sheet[mask]

        df_sheet["group"] = group_code
        frames.append(df_sheet)

    df = pd.concat(frames, ignore_index=True)
    return df


def tidy_columns(df: pd.DataFrame, n_questions: int = 20) -> pd.DataFrame:
    """
    Extract correctness + confidence columns in order,
    ignoring question text, probability, weighted score, etc.
    Also keep a participant name column for easy reference.
    """

    # ---- identify score + confidence columns ----
    score_cols = [c for c in df.columns if c.endswith("[Score]")]
    conf_cols = [c for c in df.columns if c.startswith("How confident")]

    cols = list(df.columns)
    score_cols = sorted(score_cols, key=lambda c: cols.index(c))
    conf_cols = sorted(conf_cols, key=lambda c: cols.index(c))

    if len(score_cols) != n_questions:
        print(f"⚠ WARNING: Expected {n_questions} score columns but found {len(score_cols)}")
    if len(conf_cols) != n_questions:
        print(f"⚠ WARNING: Expected {n_questions} confidence columns but found {len(conf_cols)}")

    # Drop non-participant / junk rows based on the first score column
    first_score_col = score_cols[0]
    mask = pd.to_numeric(df[first_score_col], errors="coerce").notna()
    df = df[mask].copy()  # copy() avoids chained-assignment warnings

    # ---- participant name column ----
    name_candidates = [c for c in df.columns if "What is your name" in c]
    if name_candidates:
        participant = df[name_candidates[0]]
    else:
        if "Timestamp" in df.columns:
            participant = df["Timestamp"].astype(str)
        else:
            participant = pd.Series(range(1, len(df) + 1), index=df.index)

    # ---- build a fresh, compact DataFrame from a dict ----
    data = {
        "participant": participant,
        "group": df["group"],
    }

    for i, (sc, cc) in enumerate(zip(score_cols, conf_cols), start=1):
        data[f"correct_{i}"] = pd.to_numeric(df[sc], errors="coerce")
        data[f"conf_{i}"] = pd.to_numeric(df[cc], errors="coerce")

    clean_df = pd.DataFrame(data)

    # Reorder columns nicely (just in case)
    cols_order = (
        ["participant", "group"]
        + [f"correct_{i}" for i in range(1, n_questions + 1)]
        + [f"conf_{i}" for i in range(1, n_questions + 1)]
    )
    clean_df = clean_df[cols_order]

    return clean_df


def make_processed(n_questions: int = 20) -> pd.DataFrame:
    """
    Full pipeline:
      - load CG/EG sheets
      - tidy column names
      - compute per-question p, ABS, CWS
      - compute participant-level totals for accuracy, ABS, CWS
      - save to data/processed/study_results_clean.csv
    """
    df = load_and_combine()
    df = tidy_columns(df, n_questions=n_questions)

    # Compute all 3 scoring systems
    df = add_question_scores(df, n_questions, use_abs=True, use_cws=True)
    df = add_summary_scores(df, n_questions, use_abs=True, use_cws=True)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"Saved cleaned data to {PROCESSED_PATH}")

    return df


if __name__ == "__main__":
    make_processed()
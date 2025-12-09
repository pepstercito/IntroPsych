# src/scoring.py
import pandas as pd


def confidence_to_prob(conf_series: pd.Series) -> pd.Series:
    """
    Map confidence 1–7 to probability 0–1.
    1 -> 0.0, 7 -> 1.0
    """
    return (conf_series - 1) / 6


# ---------- ABS (Augmented Brier Score) ---------- #

def abs_for_question(p: pd.Series, y: pd.Series) -> pd.Series:
    """
    Augmented Brier Score for one question.

    p: probability 0–1
    y: correctness (0 or 1)
    ABS = (1 - (p - y)^2) + 0.5y
    """
    return (1 - (p - y) ** 2) + 0.5 * y


# ---------- CWS (Custom confidence-weighted score) ---------- #

def cws_for_question(p: pd.Series, y: pd.Series) -> pd.Series:
    """
    Custom confidence-weighted score.

    Correct:  0.6 + 0.4 p   (range 0.6–1.0)
    Wrong:    0.4 - 0.4 p   (range 0.0–0.4)

    This guarantees:
      confident correct > guessed correct > unconfident wrong > confident wrong
      and all correct > all wrong.
    """
    correct_part = 0.6 + 0.4 * p
    wrong_part = 0.4 - 0.4 * p
    return y * correct_part + (1 - y) * wrong_part


# ---------- Attach per-question scores to dataframe ---------- #

def add_question_scores(
    df: pd.DataFrame,
    n_questions: int = 20,
    use_abs: bool = True,
    use_cws: bool = True,
) -> pd.DataFrame:
    """
    For each question i, create:

      p_i      – probability from confidence
      abs_i    – ABS score   (if use_abs)
      cws_i    – custom CWS  (if use_cws)

    Expects columns:
      conf_i   – confidence 1–7
      correct_i– 0/1 correctness
    """
    for i in range(1, n_questions + 1):
        conf_col = f"conf_{i}"
        y_col = f"correct_{i}"
        p_col = f"p_{i}"

        df[p_col] = confidence_to_prob(df[conf_col])

        if use_abs:
            df[f"abs_{i}"] = abs_for_question(df[p_col], df[y_col])
        if use_cws:
            df[f"cws_{i}"] = cws_for_question(df[p_col], df[y_col])

    return df


# ---------- Participant-level summaries ---------- #

def add_summary_scores(
    df: pd.DataFrame,
    n_questions: int = 20,
    use_abs: bool = True,
    use_cws: bool = True,
) -> pd.DataFrame:
    """
    Compute participant-level metrics:

      total_correct
      accuracy
      mean_conf
      total_abs  – sum of ABS_i  (if use_abs)
      total_cws  – sum of CWS_i  (if use_cws)
    """
    correct_cols = [f"correct_{i}" for i in range(1, n_questions + 1)]
    conf_cols = [f"conf_{i}" for i in range(1, n_questions + 1)]

    df["total_correct"] = df[correct_cols].sum(axis=1)
    df["accuracy"] = df["total_correct"] / n_questions
    df["mean_conf"] = df[conf_cols].mean(axis=1)

    if use_abs:
        abs_cols = [f"abs_{i}" for i in range(1, n_questions + 1)]
        df["total_abs"] = df[abs_cols].sum(axis=1)

    if use_cws:
        cws_cols = [f"cws_{i}" for i in range(1, n_questions + 1)]
        df["total_cws"] = df[cws_cols].sum(axis=1)

    return df
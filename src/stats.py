# src/stats.py
import numpy as np
import pandas as pd
from scipy import stats


def group_descriptives(df: pd.DataFrame, dv: str, group_col: str = "group") -> pd.DataFrame:
    """
    Simple descriptives (n, mean, sd, se) for CG vs EG on a given DV.
    """
    rows = []
    for grp, sub in df.groupby(group_col):
        x = sub[dv].dropna()
        n = x.shape[0]
        rows.append(
            {
                "group": grp,
                "n": n,
                "mean": x.mean(),
                "sd": x.std(ddof=1),
                "se": x.std(ddof=1) / np.sqrt(n) if n > 0 else np.nan,
            }
        )
    return pd.DataFrame(rows)


def independent_t(df: pd.DataFrame, dv: str,
                  group_col: str = "group",
                  g1: str = "CG", g2: str = "EG") -> dict:
    """
    Welch's t-test for dv between two groups.
    Returns a dict with t, p, means, and Cohen's d.
    """
    x1 = df.loc[df[group_col] == g1, dv].dropna()
    x2 = df.loc[df[group_col] == g2, dv].dropna()

    t, p = stats.ttest_ind(x1, x2, equal_var=False)

    # Cohen's d (pooled SD)
    n1, n2 = len(x1), len(x2)
    s1, s2 = x1.std(ddof=1), x2.std(ddof=1)
    pooled_var = ((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2)
    d = (x1.mean() - x2.mean()) / np.sqrt(pooled_var)

    return {
        "dv": dv,
        "group1": g1,
        "group2": g2,
        "mean1": x1.mean(),
        "mean2": x2.mean(),
        "t": t,
        "p": p,
        "cohens_d": d,
        "n1": n1,
        "n2": n2,
    }
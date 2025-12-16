"""
CareTrack - Patient Risk Triage Rules

Reusable functions extracted from the Q3 analysis (HTML report).
- Risk levels are based on disease_score thresholds (max_score split into thirds)
- Optional feature engineering: HIV-positive patients get a 30% risk uplift
"""

from __future__ import annotations
import pandas as pd


def compute_thresholds(score_series: pd.Series) -> tuple[float, float]:
    """
    Split the maximum score into 3 equal parts.
    threshold_1 = max/3
    threshold_2 = 2*max/3
    """
    max_score = float(score_series.max())
    threshold_1 = max_score / 3
    threshold_2 = 2 * max_score / 3
    return threshold_1, threshold_2


def classify_risk(score: float, threshold_1: float, threshold_2: float) -> str:
    """
    Classify risk using the thresholds:
    - Low Risk: score <= threshold_1
    - Medium Risk: threshold_1 < score <= threshold_2
    - High Risk: score > threshold_2
    """
    if score <= threshold_1:
        return "Low Risk"
    elif score <= threshold_2:
        return "Medium Risk"
    return "High Risk"


def add_hiv_adjusted_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Feature engineering (Q3e):
    If HIV_positive == 1, increase disease_score by 30% (score * 1.3).
    If HIV_positive column does not exist, assume 0 for all patients.
    Adds:
      - HIV_positive (0/1)
      - adjusted_disease_score
    """
    out = df.copy()
    out["HIV_positive"] = out.get("HIV_positive", 0)
    out["HIV_positive"] = out["HIV_positive"].fillna(0).astype(int)

    out["adjusted_disease_score"] = out.apply(
        lambda row: row["disease_score"] * 1.3 if row["HIV_positive"] == 1 else row["disease_score"],
        axis=1,
    )
    return out


def assign_risk_levels(
    df: pd.DataFrame,
    score_col: str = "disease_score",
    risk_col: str = "risk_level",
) -> pd.DataFrame:
    """
    Adds a risk_level column based on score_col using the 'max/3' thresholds logic.
    """
    out = df.copy()
    t1, t2 = compute_thresholds(out[score_col])
    out[risk_col] = out[score_col].apply(lambda s: classify_risk(float(s), t1, t2))
    return out


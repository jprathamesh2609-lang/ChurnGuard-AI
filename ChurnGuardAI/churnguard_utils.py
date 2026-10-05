"""
Reusable prediction code for CHURNGUARD AI (used by the Streamlit app and for testing).
It mirrors the functions defined in churn_prediction.ipynb.
"""
import json
import os

import joblib
import numpy as np
import pandas as pd

ADDON_COLS = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
DECISION_THRESHOLD = 0.50
ACTIONS = {
    "HIGH": "Priority retention: personal call / targeted offer / move to a longer contract.",
    "MEDIUM": "Monitor and nudge: service check-in, add-on trial, loyalty communication.",
    "LOW": "No action needed: routine engagement only.",
}


def engineer_features(data: pd.DataFrame) -> pd.DataFrame:
    d = data.copy()
    d["num_addons"] = (d[ADDON_COLS] == "Yes").sum(axis=1)
    d["protection_services"] = (d[["OnlineSecurity", "TechSupport"]] == "Yes").sum(axis=1)
    avg = d["TotalCharges"] / d["tenure"].clip(lower=1)
    d["avg_monthly_spend"] = np.where(d["tenure"] > 0, avg, d["MonthlyCharges"])
    d["charge_vs_avg"] = d["MonthlyCharges"] - d["avg_monthly_spend"]
    d["tenure_group"] = pd.cut(d["tenure"], bins=[-1, 12, 24, 48, 72],
                               labels=["0-12", "13-24", "25-48", "49-72"]).astype(str)
    d["has_family"] = np.where((d["Partner"] == "Yes") | (d["Dependents"] == "Yes"), "Yes", "No")
    return d


def load_artifacts(model_dir: str = "models"):
    model = joblib.load(os.path.join(model_dir, "churnguard_model.joblib"))
    with open(os.path.join(model_dir, "churnguard_metadata.json")) as f:
        meta = json.load(f)
    return model, meta


def build_customer_row(customer_data: dict, meta: dict) -> pd.DataFrame:
    row = dict(meta["defaults"])
    row.update(customer_data)
    if "TotalCharges" not in customer_data:
        row["TotalCharges"] = row["tenure"] * row["MonthlyCharges"]
    return pd.DataFrame([row])[meta["base_columns"]]


def risk_level(probability: float, meta: dict) -> str:
    if probability >= meta["high_threshold"]:
        return "HIGH"
    if probability >= meta["medium_threshold"]:
        return "MEDIUM"
    return "LOW"


def predict_churn(customer_data: dict, model, meta: dict) -> dict:
    row = engineer_features(build_customer_row(customer_data, meta))
    probability = float(model.predict_proba(row)[0, 1])
    level = risk_level(probability, meta)
    return {"predicted_churn": "YES" if probability >= DECISION_THRESHOLD else "NO",
            "churn_probability": probability, "risk_level": level, "suggested_action": ACTIONS[level]}

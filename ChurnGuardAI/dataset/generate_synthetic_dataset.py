"""
Generates a synthetic customer-churn dataset that follows the IBM Telco Customer Churn schema
(21 columns, 7043 rows).

WHY THIS FILE EXISTS
The official IBM Telco CSV could not be downloaded while this project was being built
(no internet access). To keep the project fully runnable, a dataset with the SAME columns,
value formats and data-quality quirks (e.g. blank TotalCharges for tenure = 0) was generated.

TO USE THE REAL DATA
Replace dataset/customer_churn.csv with the official IBM Telco CSV (or the CSV provided by
MainCrafts) and re-run the notebook. No code change is needed - all column names match.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 7043


def pick(options, probs, size=N):
    return rng.choice(options, size=size, p=probs)


gender = pick(["Male", "Female"], [0.5, 0.5])
senior = pick([0, 1], [0.84, 0.16])
partner = pick(["Yes", "No"], [0.48, 0.52])
dependents = np.where(partner == "Yes", pick(["Yes", "No"], [0.42, 0.58]), pick(["Yes", "No"], [0.09, 0.91]))
contract = pick(["Month-to-month", "One year", "Two year"], [0.55, 0.21, 0.24])

# tenure depends on contract (long contracts -> longer tenure)
tenure = np.empty(N, dtype=int)
shape = {"Month-to-month": (1.1, 3.2), "One year": (2.0, 2.0), "Two year": (3.2, 1.4)}
for c, (a, b) in shape.items():
    idx = contract == c
    tenure[idx] = np.clip((rng.beta(a, b, idx.sum()) * 71 + 1).round(), 1, 72).astype(int)
zero = rng.choice(N, 11, replace=False)  # brand-new customers -> blank TotalCharges (as in the real data)
tenure[zero] = 0

phone = pick(["Yes", "No"], [0.90, 0.10])
multi = np.where(phone == "No", "No phone service", pick(["Yes", "No"], [0.47, 0.53]))
internet = pick(["DSL", "Fiber optic", "No"], [0.34, 0.44, 0.22])


def addon(p_yes):
    return np.where(internet == "No", "No internet service", pick(["Yes", "No"], [p_yes, 1 - p_yes]))


security, backup, device, techsup = addon(0.29), addon(0.34), addon(0.34), addon(0.29)
stv, smov = addon(0.38), addon(0.39)
paperless = pick(["Yes", "No"], [0.59, 0.41])
payment = pick(["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"],
               [0.34, 0.23, 0.22, 0.21])

# monthly charges are built from the services taken (like the real data)
mc = np.where(phone == "Yes", 20.0, 0.0)
mc = mc + np.select([internet == "DSL", internet == "Fiber optic"], [25.0, 55.0], 0.0)
for col, price in [(multi, 5), (security, 5), (backup, 5), (device, 5), (techsup, 5), (stv, 10), (smov, 10)]:
    mc = mc + np.where(col == "Yes", price, 0.0)
mc = np.where((phone == "No") & (internet == "No"), 20.0, mc)
mc = np.clip(mc + rng.normal(0, 2.5, N), 18.25, 118.75).round(2)

total = np.round(mc * tenure * rng.normal(1.0, 0.02, N), 2)

# churn probability: logistic model built from realistic business drivers
z = (-0.35
     + np.select([contract == "Month-to-month", contract == "One year"], [1.25, -0.25], -1.45)
     - 0.035 * tenure
     + np.where(internet == "Fiber optic", 0.75, np.where(internet == "DSL", -0.10, -0.75))
     + np.where(security == "No", 0.35, 0) + np.where(techsup == "No", 0.35, 0)
     + np.where(backup == "No", 0.10, 0) + np.where(device == "No", 0.08, 0)
     + np.where(payment == "Electronic check", 0.55, 0)
     + np.where(paperless == "Yes", 0.25, 0)
     + np.where(senior == 1, 0.30, 0)
     + np.where(dependents == "Yes", -0.30, 0) + np.where(partner == "Yes", -0.10, 0)
     + 0.012 * (mc - 65))
p = 1 / (1 + np.exp(-(z - 1.38)))
churn = np.where(rng.random(N) < p, "Yes", "No")


def make_id():
    return f"{rng.integers(1000, 9999)}-{''.join(rng.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), 5))}"


ids, seen = [], set()
while len(ids) < N:
    s = make_id()
    if s not in seen:
        seen.add(s)
        ids.append(s)

df = pd.DataFrame({
    "customerID": ids, "gender": gender, "SeniorCitizen": senior, "Partner": partner, "Dependents": dependents,
    "tenure": tenure, "PhoneService": phone, "MultipleLines": multi, "InternetService": internet,
    "OnlineSecurity": security, "OnlineBackup": backup, "DeviceProtection": device, "TechSupport": techsup,
    "StreamingTV": stv, "StreamingMovies": smov, "Contract": contract, "PaperlessBilling": paperless,
    "PaymentMethod": payment, "MonthlyCharges": mc, "TotalCharges": total.astype(str), "Churn": churn})
df.loc[df["tenure"] == 0, "TotalCharges"] = " "  # blank string, exactly like the IBM file
df.to_csv("dataset/customer_churn.csv", index=False)
print(df.shape, "churn rate:", round((df.Churn == "Yes").mean(), 3))

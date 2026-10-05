"""
Builds report/ChurnGuardAI_Project_Report.pdf from:
  - report/results.json  (written by churn_prediction.ipynb)
  - images/*.png         (written by churn_prediction.ipynb)
  - dataset/customer_churn.csv (for the dataset preview)

Usage (from the project root):   python report/generate_report.py
Requires:  pip install reportlab pillow pandas
"""
import datetime
import json
import os

import pandas as pd
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph,
                                Spacer, Table, TableStyle)

CANDIDATE = "Your Name"          # <-- change to your name before generating the final PDF

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "images")
OUT = os.path.join(ROOT, "report", "ChurnGuardAI_Project_Report.pdf")
R = json.load(open(os.path.join(ROOT, "report", "results.json")))

# ------------------------------------------------------------------ fonts
FONT, FONT_B, FONT_I, UNICODE = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", False
for base in ["/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "C:/Windows/Fonts", "/Library/Fonts"]:
    reg, bold, obl = [os.path.join(base, n) for n in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf")]
    if all(os.path.exists(p) for p in (reg, bold, obl)):
        pdfmetrics.registerFont(TTFont("DV", reg)); pdfmetrics.registerFont(TTFont("DV-B", bold)); pdfmetrics.registerFont(TTFont("DV-I", obl))
        FONT, FONT_B, FONT_I, UNICODE = "DV", "DV-B", "DV-I", True
        break


def T(s):
    """Make text safe for the chosen font (Helvetica has no rupee sign / arrows)."""
    s = str(s)
    if not UNICODE:
        for a, b in {"₹": "Rs.", "→": "->", "≥": ">=", "≈": "~", "≠": "!=", "✔": "OK", "–": "-", "—": "-", "×": "x"}.items():
            s = s.replace(a, b)
    return s


# ------------------------------------------------------------------ styles
NAVY, RED, LIGHT, GREY = colors.HexColor("#1F3A5F"), colors.HexColor("#D1495B"), colors.HexColor("#EEF3F8"), colors.HexColor("#5A6470")
body = ParagraphStyle("body", fontName=FONT, fontSize=9.6, leading=14, alignment=TA_JUSTIFY, spaceAfter=6)
small = ParagraphStyle("small", parent=body, fontSize=8, leading=10.5, textColor=GREY, alignment=TA_CENTER, spaceAfter=10)
h1 = ParagraphStyle("h1", fontName=FONT_B, fontSize=15, leading=19, textColor=NAVY, spaceBefore=12, spaceAfter=7, keepWithNext=1)
h2 = ParagraphStyle("h2", fontName=FONT_B, fontSize=11, leading=14, textColor=NAVY, spaceBefore=8, spaceAfter=4, keepWithNext=1)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=3, spaceAfter=3, alignment=0)
cell = ParagraphStyle("cell", fontName=FONT, fontSize=8, leading=10)
cellb = ParagraphStyle("cellb", parent=cell, fontName=FONT_B, textColor=colors.white)
sec_no = [0]


def P(t, st=body):
    return Paragraph(T(t), st)


def H1(t):
    sec_no[0] += 1
    return Paragraph(T(f"{sec_no[0]}. {t}"), h1)


def H2(t):
    return Paragraph(T(t), h2)


def B(items):
    return [Paragraph(T(i), bullet, bulletText="•" if UNICODE else "-") for i in items]


def fig(name, caption, width=15.5 * cm):
    path = os.path.join(IMG, name)
    w, h = PILImage.open(path).size
    return KeepTogether([Image(path, width=width, height=width * h / w), Paragraph(T(caption), small)])


def table(data, widths, header=True, hl_rows=(), font=8):
    rows = [[Paragraph(T(c), cellb if (header and i == 0) else cell) for c in r] for i, r in enumerate(data)]
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D3DE")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
             ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT])]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), NAVY))
    for r in hl_rows:
        style.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#FBE3E6")))
    t.setStyle(TableStyle(style))
    return t


def f3(x):
    return f"{x:.3f}"


def pct(x):
    return f"{x:.1f}%"


# ------------------------------------------------------------------ page decoration
def on_page(canvas, doc):
    canvas.saveState()
    if doc.page > 1:
        canvas.setFont(FONT, 7.5); canvas.setFillColor(GREY)
        canvas.drawString(2 * cm, 1.2 * cm, T("CHURNGUARD AI — MainCrafts SkillSprint · Artificial Intelligence & Machine Learning"))
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
        canvas.setStrokeColor(colors.HexColor("#C9D3DE")); canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY); canvas.rect(0, A4[1] - 12 * cm, A4[0], 12 * cm, fill=1, stroke=0)
    canvas.setFillColor(RED); canvas.rect(0, A4[1] - 12.35 * cm, A4[0], 0.35 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT_B, 34); canvas.drawString(2.2 * cm, A4[1] - 6.2 * cm, "CHURNGUARD AI")
    canvas.setFont(FONT, 15); canvas.drawString(2.2 * cm, A4[1] - 7.5 * cm, "Customer Churn Prediction & Retention Intelligence System")
    canvas.setFont(FONT, 10.5); canvas.drawString(2.2 * cm, A4[1] - 9.4 * cm, "Project Report  ·  MainCrafts 2-Day Skill Certification Program")
    canvas.drawString(2.2 * cm, A4[1] - 10.2 * cm, "Domain: Artificial Intelligence & Machine Learning")
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=2.2 * cm,
                      title="CHURNGUARD AI - Project Report", author=CANDIDATE)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")
cover_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, A4[1] - 14.5 * cm - doc.bottomMargin, id="c")
doc.addPageTemplates([PageTemplate(id="cover", frames=[cover_frame], onPage=cover, autoNextPageTemplate="main"),
                      PageTemplate(id="main", frames=[frame], onPage=on_page)])

# ------------------------------------------------------------------ content
FM, BT = R["final_metrics"], R["baseline_table"]
CM = R["confusion_matrix"]
final_short = R["selected_model"].split(". ", 1)[1]
is_replica = "replica" in R["dataset_name"].lower()
S = []

# ---- cover
S += [Spacer(1, 0.6 * cm),
      P(f"<b>Candidate:</b> {CANDIDATE}", ParagraphStyle("c1", parent=body, fontSize=11, alignment=0)),
      P(f"<b>Date:</b> {datetime.date.today():%d %B %Y}", ParagraphStyle("c2", parent=body, fontSize=11, alignment=0)),
      P("<b>Environment:</b> Python · pandas · scikit-learn · Google Colab / Jupyter", ParagraphStyle("c3", parent=body, fontSize=11, alignment=0)),
      Spacer(1, 0.5 * cm),
      table([["Headline result (unseen test customers)", ""],
             ["Selected model", final_short],
             ["Recall / Precision / F1", f"{FM['Recall']:.1%} / {FM['Precision']:.1%} / {FM['F1 Score']:.3f}"],
             ["ROC-AUC", f3(FM["ROC-AUC"])],
             ["Dataset", f"{R['dataset_name']} — {R['records']:,} customers"]], [6.5 * cm, 10.5 * cm], font=9),
      PageBreak()]

# ---- 1 title / 2 problem / 3 objective
S += [H1("Project Title"), P("<b>CHURNGUARD AI — Customer Churn Prediction &amp; Retention Intelligence System.</b> "
                            "A supervised machine-learning classification workflow that predicts whether a telecom customer is likely to churn.")]

S += [H1("Problem Statement"),
      P("Businesses lose customers for many reasons, and they usually find out <b>after</b> the customer has already decided to leave. "
        "At that point retention is expensive or impossible. The problem addressed here is to learn, from historical customer records, "
        "which customers are likely to churn so that the company can act <i>before</i> the customer leaves.")]

S += [H1("Objective"),
      *B(["Analyse customer data and identify the patterns that separate customers who churn from those who stay.",
          "Prepare the data (cleaning, encoding, scaling, feature engineering) inside leak-free scikit-learn pipelines.",
          "Train and compare at least two classification models and select one with a justified metric (recall / F1, not accuracy alone).",
          "Predict churn probability and a HIGH / MEDIUM / LOW risk level for new customers.",
          "Identify the features that influence predictions and turn the findings into practical business recommendations."])]

# ---- 4 dataset
S += [H1("Dataset Description")]
S += [P(f"The project uses the <b>Telco Customer Churn schema</b> (IBM sample dataset): {R['records']:,} customers and {R['columns_raw']} columns. "
        f"The target is <b>Churn</b> (Yes/No); the remaining columns describe demographics (gender, senior citizen, partner, dependents), "
        f"account information (tenure, contract, payment method, paperless billing, monthly and total charges) and subscribed services "
        f"(phone, internet, security, backup, protection, support, streaming). Overall churn rate: <b>{R['overall_churn_rate']:.1f}%</b> "
        f"(an imbalanced problem).")]
if is_replica:
    S += [P("<b>Important note on data provenance.</b> The official IBM CSV could not be downloaded in the environment where this project was "
            "assembled (no internet access). The file in <i>dataset/customer_churn.csv</i> is therefore a <b>schema-identical replica</b> "
            "(same 21 columns, value formats and data-quality quirks such as blank <i>TotalCharges</i> for new customers) generated by "
            "<i>dataset/generate_synthetic_dataset.py</i>. All figures in this report belong to that file. Replacing the CSV with the "
            "official IBM / MainCrafts file and re-running the notebook and <i>report/generate_report.py</i> regenerates every number, "
            "chart and statement without any code change.",
            ParagraphStyle("note", parent=body, backColor=colors.HexColor("#FFF6E0"), borderPadding=6, borderColor=colors.HexColor("#EDAE49"), borderWidth=0.6))]
S += [Spacer(1, 4),
      table([["Property", "Value"],
             ["Records", f"{R['records']:,}"], ["Columns (raw)", str(R["columns_raw"])],
             ["Input features used", f"{R['features_raw']} original (+ {len(R['new_features'])} engineered)"],
             ["Numerical features", ", ".join(R["numeric_features"])],
             ["Categorical features", f"{len(R['categorical_features'])} columns (contract, internet service, payment method, ...)"],
             ["Target", "Churn (Yes = 1, No = 0)"],
             ["Missing / blank values", f"{R['blank_totalcharges_fixed']} blank TotalCharges strings (tenure = 0); {R['missing_raw_nan']} NaN before conversion"],
             ["Duplicate records", str(R["duplicates"])],
             ["Train / test split", f"{R['train_test']['train']:,} / {R['train_test']['test']:,} (80 / 20, stratified, random_state = 42)"]],
            [5 * cm, 12 * cm])]

df_prev = pd.read_csv(os.path.join(ROOT, "dataset", "customer_churn.csv")).head(5)
cols = ["customerID", "tenure", "Contract", "InternetService", "PaymentMethod", "MonthlyCharges", "TotalCharges", "Churn"]
prev = [cols] + df_prev[cols].astype(str).values.tolist()
S += [Spacer(1, 6), H2("Dataset preview (first 5 rows, selected columns)"),
      table(prev, [2.3 * cm, 1.4 * cm, 2.8 * cm, 2.4 * cm, 3.4 * cm, 1.9 * cm, 1.8 * cm, 1.2 * cm])]

# ---- 5 tech
S += [H1("Technologies Used"),
      table([["Tool", "Purpose"],
             ["Python 3", "Programming language"], ["Google Colab / Jupyter", "Free hosted notebook environment"],
             ["pandas, NumPy", "Data loading, cleaning, aggregation, numeric operations"],
             ["Matplotlib, Seaborn", "Exploratory analysis and result visualisations"],
             ["scikit-learn", "Train/test split, OneHotEncoder, StandardScaler, ColumnTransformer, Pipeline, models, GridSearchCV, permutation importance, metrics"],
             ["joblib", "Saving / loading the trained model"], ["ReportLab", "Generating this PDF report"],
             ["Streamlit (optional)", "Web interface — CHURNGUARD AI Customer Risk Predictor"]], [4.5 * cm, 12.5 * cm])]

# ---- 6 methodology
S += [H1("Methodology"),
      P("The notebook follows the required end-to-end workflow and explains <i>why</i> each step is done:"),
      table([["Stage", "What was done", "Why"],
             ["1. Data understanding", "Shape, dtypes, missing values, duplicates, statistics, target definition", "Know the data before changing it; find hidden problems"],
             ["2. Cleaning", "TotalCharges to numeric; blanks filled with 0; ID dropped; categories inspected", "Models need clean numeric input; no leakage of identifiers"],
             ["3. Exploration", "6 visualisations, each with a written conclusion", "Discover churn drivers and class imbalance"],
             ["4. Feature preparation", "Stratified 80/20 split; one-hot encoding in a pipeline; engineered features", "Test set must represent unseen data; pipelines prevent leakage"],
             ["5. Model training", "Logistic Regression and Random Forest baselines, then improved variants", "Compare a simple and a complex model"],
             ["6. Evaluation", "Accuracy, precision, recall, F1, ROC-AUC, confusion matrix, 5-fold CV", "Accuracy is misleading on imbalanced churn data"],
             ["7. Prediction", "predict_churn() returns probability, risk level and suggested action", "Make the model usable for new customers"],
             ["8. Business insight", "Risk bands, feature importance, recommendations, limitations", "Turn predictions into decisions"]],
            [3.3 * cm, 8 * cm, 5.7 * cm])]

# ---- 7 preprocessing
S += [H1("Data Preprocessing"),
      table([["Issue found", "Action", "Justification"],
             ["TotalCharges stored as text (blank strings)", "pd.to_numeric(errors='coerce')", "Column is numeric by meaning"],
             [f"{R['blank_totalcharges_fixed']} missing TotalCharges", "Filled with 0 (not deleted, not mean)",
              "All these customers have tenure = 0, i.e. nothing billed yet; deleting rows loses real customers, the mean would invent spend"],
             ["customerID", "Dropped", "Unique identifier, no predictive meaning"],
             [f"Duplicate rows ({R['duplicates']})", "Checked before dropping the ID; drop_duplicates()", "Avoid double-counting"],
             ["'No internet service' / 'No phone service'", "Kept as separate categories", "They carry real information (no such service)"],
             ["Categorical text columns", "OneHotEncoder(handle_unknown='ignore') in a ColumnTransformer", "Models need numbers; unknown categories will not crash prediction"],
             ["Numeric scale differences", "StandardScaler (Day 2 pipelines)", "Removes the optimiser ConvergenceWarning of the unscaled baseline"],
             ["Class imbalance", "class_weight ('balanced')", "Missing a churner is the costly error"]],
            [4.6 * cm, 5.4 * cm, 7 * cm]),
      P(f"<b>Engineered features:</b> {', '.join(R['new_features'])}.")]

# ---- 8 EDA
S += [H1("Exploratory Analysis"),
      P("Key observations drawn from the actual data (each is also written under its chart in the notebook):"),
      *B([R["findings"][0], R["findings"][1],
          f"Churners have a median tenure of {R['tenure_median']['Yes']:.0f} months versus {R['tenure_median']['No']:.0f} months for customers who stayed.",
          f"Churners pay more per month on average (₹{R['mean_monthly_charges']['Yes']:.2f} vs ₹{R['mean_monthly_charges']['No']:.2f}).",
          f"By internet service, churn is highest for {max(R['churn_by_internet'], key=R['churn_by_internet'].get)} "
          f"({max(R['churn_by_internet'].values()):.1f}%); by payment method it is highest for "
          f"{max(R['churn_by_payment'], key=R['churn_by_payment'].get)} ({max(R['churn_by_payment'].values()):.1f}%)."]),
      fig("01_churn_distribution.png", "Figure 1 — Churn distribution: the classes are imbalanced, so accuracy alone is misleading.", 8.5 * cm),
      fig("02_churn_vs_contract.png", "Figure 2 — Churn vs contract type.", 11 * cm),
      fig("03_churn_vs_tenure.png", "Figure 3 — Churn vs tenure: churners are concentrated among newer customers.", 12 * cm),
      fig("04_churn_vs_monthly_charges.png", "Figure 4 — Churn vs monthly charges.", 9 * cm),
      fig("05_churn_vs_internet_payment.png", "Figure 5 — Churn rate by internet service and payment method.", 15.5 * cm),
      fig("06_correlation_heatmap.png", "Figure 6 — Correlation of numeric features with churn.", 10 * cm)]

# ---- 9 models tested
S += [H1("Models Tested"),
      P("Two baseline models were required; four further candidates were tested on Day 2 to improve the result:"),
      *B(["<b>Logistic Regression</b> — simple, fast, interpretable linear baseline.",
          "<b>Random Forest</b> (200 trees) — non-linear ensemble baseline. It reaches 100% accuracy on training data but less on test data, a clear sign of overfitting.",
          "<b>Logistic Regression + engineered features + scaling</b>.",
          "<b>Logistic Regression + engineered features + class weighting</b> (handles class imbalance).",
          "<b>Gradient Boosting + engineered features</b> (another algorithm).",
          f"<b>Random Forest + engineered features + class weighting, tuned with GridSearchCV</b> (best parameters: "
          f"{', '.join(k.replace('model__', '') + '=' + str(v) for k, v in R['best_params'].items())})."]),
      P("Candidates were ranked by <b>5-fold cross-validated F1 on the training data only</b>; the test set was used purely to report performance.")]

# ---- 10 evaluation
exp = R["experiment_table"]
rows = [["Experiment", "CV F1", "Acc.", "Prec.", "Recall", "F1", "AUC"]]
hl = []
for i, e in enumerate(exp, start=1):
    rows.append([e["Experiment"], f3(e["CV F1 (train)"]), f3(e["Accuracy"]), f3(e["Precision"]), f3(e["Recall"]), f3(e["F1 Score"]), f3(e["ROC-AUC"])])
    if e["Experiment"] == R["selected_model"]:
        hl.append(i)
S += [H1("Evaluation Results"),
      H2("Day 1 baseline comparison (test set)"),
      table([["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]] +
            [[b["Model"], f3(b["Accuracy"]), f3(b["Precision"]), f3(b["Recall"]), f3(b["F1 Score"]), f3(b["ROC-AUC"])] for b in BT],
            [5 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm]),
      Spacer(1, 6), H2("All experiments (selected model highlighted)"),
      table(rows, [6.6 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm, 1.7 * cm], hl_rows=hl),
      Spacer(1, 6),
      fig("08_model_comparison.png", "Figure 7 — Precision, recall and F1 of every experiment on the test set.", 14 * cm),
      H2("Which metric matters most?"),
      P("<b>Recall on the churn class, balanced against F1.</b> A false negative (predicting 'stay' for a customer who leaves) silently loses "
        "the customer and all of their future revenue; a false positive only wastes a retention offer. Accuracy is not used to choose the "
        "model because only about " + f"{R['overall_churn_rate']:.0f}% of customers churn, so a model that never predicts churn would already look accurate. "
        "F1 prevents 'buying' recall by flagging everyone."),
      H2("Improvement documented (Challenge A)"),
      table([["", "Model", "F1", "Recall", "Precision"],
             ["Before", R["before"]["name"].split(". ", 1)[1], f3(R["before"]["f1"]), f3(R["before"]["recall"]), f3(R["before"]["precision"])],
             ["After", R["after"]["name"].split(". ", 1)[1], f3(R["after"]["f1"]), f3(R["after"]["recall"]), f3(R["after"]["precision"])]],
            [1.8 * cm, 8.2 * cm, 2.3 * cm, 2.3 * cm, 2.4 * cm]),
      Spacer(1, 4),
      P("<b>What changed and why:</b> class weighting was applied so the model treats a missed churner as more costly (the business requirement "
        "from Question 5), and engineered features and scaling were tested to summarise customer behaviour and fix the optimiser warning. "
        "Recall rose at the price of lower precision — more customers are flagged, some of whom would have stayed. That trade-off is a business decision.")]

# ---- 11 final model
S += [H1("Final Model"),
      P(f"<b>Selected model:</b> {final_short}. It was chosen by the highest cross-validated F1 on the training data and evaluated once on the "
        f"{R['train_test']['test']:,} held-out customers."),
      table([["Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"],
             [f3(FM["Accuracy"]), f3(FM["Precision"]), f3(FM["Recall"]), f3(FM["F1 Score"]), f3(FM["ROC-AUC"])]], [3.4 * cm] * 5),
      Spacer(1, 6),
      table([["", "Predicted: Stay", "Predicted: Churn"],
             ["Actual: Stay", f"TN = {CM['TN']}", f"FP = {CM['FP']}"],
             ["Actual: Churn", f"FN = {CM['FN']}", f"TP = {CM['TP']}"]], [4 * cm, 4.5 * cm, 4.5 * cm]),
      Spacer(1, 4),
      P(f"Of {CM['TP'] + CM['FN']} customers who really churned, the model catches {CM['TP']} ({CM['TP'] / (CM['TP'] + CM['FN']):.1%}) and misses {CM['FN']}. "
        f"It raises {CM['FP']} false alarms among {CM['TN'] + CM['FP']} customers who stayed. <b>TP</b> = correctly flagged churner (can be saved); "
        f"<b>TN</b> = correctly ignored loyal customer; <b>FP</b> = wasted retention offer; <b>FN</b> = silent loss (the most costly error)."),
      fig("09_final_confusion_matrix_roc.png", "Figure 8 — Final model: confusion matrix and ROC curve (test set).", 15.5 * cm),
      H2("Feature importance"),
      P("Permutation importance (drop in F1 when one original column is shuffled on the test set) shows what the model relies on:"),
      fig("10_feature_importance.png", "Figure 9 — Top 10 features influencing predictions.", 12 * cm),
      P("Importance describes what the model uses, not why customers leave: it shows association, not causation.")]

# ---- 12 business insights
bt = R["band_table"]
S += [H1("Business Insights"),
      *B(R["findings"]),
      H2("Risk levels (Challenge B)"),
      P(f"Probabilities are converted to risk levels: <b>HIGH</b> ≥ {R['thresholds']['high']:.2f}, <b>MEDIUM</b> ≥ {R['thresholds']['medium']:.2f}, otherwise <b>LOW</b>. "
        "The thresholds are a business choice justified by the churn rate actually observed inside each band on the test set (below). "
        "Because the final model is class-weighted, its probabilities are not calibrated frequencies and should be used for ranking."),
      table([["Risk level", "Customers", "Share of customers", "Actual churn rate", "Churners captured"]] +
            [[b["Risk"], str(int(b["Customers"])), pct(b["Share of customers (%)"]), pct(b["Actual churn rate (%)"]), pct(b["Churners captured (%)"])] for b in bt],
            [3 * cm, 2.8 * cm, 3.8 * cm, 3.8 * cm, 3.6 * cm]),
      Spacer(1, 6), fig("11_risk_bands.png", "Figure 10 — Actual churn rate inside each predicted risk band.", 9 * cm),
      H2("Example predictions for new customers"),
      table([["Customer profile", "Key inputs", "Churn probability", "Risk"]] +
            [[name, "; ".join(f"{k}: {v}" for k, v in R["demo_inputs"][name].items() if k in ("Contract", "tenure", "MonthlyCharges", "InternetService")),
              f"{p['churn_probability']:.1%}", p["risk_level"]] for name, p in R["demo_predictions"].items()],
            [4.6 * cm, 7 * cm, 2.9 * cm, 2.5 * cm]),
      H2("Recommendation"),
      P(R["business_recommendation"]),
      *B(["HIGH risk → personal outreach or targeted offer.", "MEDIUM risk → automated nudges and service check-ins.", "LOW risk → routine engagement only."])]

# ---- 13 limitations / 14 future
S += [H1("Limitations"), *B(R["limitations"])]
S += [H1("Future Improvements"),
      *B(["Add a cost-based decision threshold using real retention-offer cost and customer lifetime value.",
          "Test gradient-boosting libraries (XGBoost / LightGBM) and probability calibration.",
          "Explain individual predictions with SHAP values.",
          "Use time-stamped data and survival analysis to predict <i>when</i> a customer is likely to leave.",
          "Run an A/B test of retention offers to measure real (causal) uplift.",
          "Deploy the Streamlit app, monitor data drift and retrain regularly."])]

# ---- evidence
S += [PageBreak(), H1("Project Evidence Checklist"),
      table([["Required evidence", "Where to find it"],
             ["Dataset preview", "Section 4 of this report; notebook Step 4 (df.head())"],
             ["EDA visualisations", "Figures 1-6; images/01 … 06; notebook Step 6"],
             ["Model evaluation", "Evaluation Results tables, Figure 7; notebook Steps 10-12 and Challenge A"],
             ["Confusion matrix", "Figure 8; images/07 and images/09; notebook Step 13 and Challenge A"],
             ["Final prediction", "Business Insights (example predictions); notebook Steps 14 and Challenge B"],
             ["Final result", "Final Model section; notebook Challenge C ('CHURNGUARD AI — FINAL RESULTS')"]], [5 * cm, 12 * cm])]

doc.build(S)
print("Report written to", OUT)

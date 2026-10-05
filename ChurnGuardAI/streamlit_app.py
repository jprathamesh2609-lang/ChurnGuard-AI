"""
CHURNGUARD AI - Customer Risk Predictor (optional advanced challenge)

Run locally:   pip install streamlit
               streamlit run streamlit_app.py
(Run the notebook first so that models/churnguard_model.joblib exists.)
"""
import streamlit as st

from churnguard_utils import load_artifacts, predict_churn

st.set_page_config(page_title="CHURNGUARD AI", page_icon="🛡️")


@st.cache_resource
def get_model():
    return load_artifacts("models")


model, meta = get_model()
opts = meta["categorical_options"]
defaults = meta["defaults"]

st.title("🛡️ CHURNGUARD AI — Customer Risk Predictor")
st.caption("Enter customer details. Fields you leave at their default use typical values from the training data.")

col1, col2 = st.columns(2)
with col1:
    tenure = st.slider("Tenure (months)", 0, 72, 5)
    monthly = st.number_input("Monthly charges (₹)", 18.0, 120.0, 79.5, step=0.5)
    contract = st.selectbox("Contract", opts["Contract"], index=opts["Contract"].index("Month-to-month"))
    internet = st.selectbox("Internet service", opts["InternetService"], index=opts["InternetService"].index("Fiber optic"))
with col2:
    payment = st.selectbox("Payment method", opts["PaymentMethod"], index=opts["PaymentMethod"].index("Electronic check"))
    paperless = st.selectbox("Paperless billing", opts["PaperlessBilling"], index=opts["PaperlessBilling"].index(defaults["PaperlessBilling"]))
    security = st.selectbox("Online security", opts["OnlineSecurity"], index=opts["OnlineSecurity"].index(defaults["OnlineSecurity"]))
    techsup = st.selectbox("Tech support", opts["TechSupport"], index=opts["TechSupport"].index(defaults["TechSupport"]))

if st.button("Assess churn risk", type="primary"):
    customer = {"tenure": tenure, "MonthlyCharges": monthly, "Contract": contract, "InternetService": internet,
                "PaymentMethod": payment, "PaperlessBilling": paperless, "OnlineSecurity": security, "TechSupport": techsup}
    r = predict_churn(customer, model, meta)
    st.subheader(f"Prediction: {r['risk_level']} CHURN RISK")
    st.metric("Churn probability", f"{r['churn_probability']:.1%}")
    {"HIGH": st.error, "MEDIUM": st.warning, "LOW": st.success}[r["risk_level"]](f"Suggested action: {r['suggested_action']}")
    st.caption("A prediction is a probability, not a certainty.")

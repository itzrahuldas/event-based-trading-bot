import streamlit as st
import sys
from pathlib import Path

# Add project root to sys.path
root_path = Path(__file__).parent.parent.parent
sys.path.append(str(root_path))
import pandas as pd
import plotly.express as px
from pathlib import Path
from src.dashboard.inference import ModelPredictor

# Page Config
st.set_page_config(
    page_title="Sentinel: Customer Retention Engine",
    page_icon="🛡️",
    layout="wide"
)

# Constants
DATA_PATH = "data/processed/cleaned_data.parquet"

@st.cache_resource
def load_predictor():
    return ModelPredictor()

@st.cache_data
def load_data():
    if Path(DATA_PATH).exists():
        return pd.read_parquet(DATA_PATH)
    else:
        st.error(f"Data file not found at {DATA_PATH}. Please run the pipeline.")
        return None

def main():
    st.title("🛡️ Sentinel: Customer Retention Engine")
    
    # Load resources
    try:
        predictor = load_predictor()
        df = load_data()
    except Exception as e:
        st.error(f"Failed to initialize: {e}")
        return

    if df is None:
        return

    # Tabs
    tab1, tab2 = st.tabs(["📊 Executive Overview", "🔍 Customer Inspector"])

    # --- Tab 1: Executive Overview ---
    with tab1:
        st.header("Portfolio Health Check")
        
        # Top Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_customers = len(df)
        churn_rate = (df['churn'].mean() * 100) if 'churn' in df.columns else 0
        avg_charges = df['monthly_charges'].mean()
        high_risk_volume = len(df[df['churn'] == 1]) if 'churn' in df.columns else 0

        col1.metric("Total Customers", f"{total_customers:,}")
        col2.metric("Churn Rate", f"{churn_rate:.1f}%")
        col3.metric("Avg Monthly Charges", f"${avg_charges:.2f}")
        col4.metric("High Risk Volume", f"{high_risk_volume:,}")

        st.markdown("---")
        
        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Tenure Distribution by Churn")
            if 'churn' in df.columns:
                fig = px.histogram(df, x="tenure", color="churn", nbins=20, 
                                   title="Customer Tenure vs Churn",
                                   color_discrete_map={0: "green", 1: "red"},
                                   labels={"churn": "Churn Status"})
                st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Monthly Charges Distribution")
            fig2 = px.box(df, y="monthly_charges", x="churn" if 'churn' in df.columns else None,
                          color="churn" if 'churn' in df.columns else None,
                          title="Monthly Charges Spread",
                          color_discrete_map={0: "green", 1: "red"})
            st.plotly_chart(fig2, use_container_width=True)

    # --- Tab 2: Customer Inspector ---
    with tab2:
        st.header("Real-time Risk Scoring")
        
        col_input, col_pred = st.columns([1, 2])
        
        with col_input:
            st.subheader("Customer Profile")
            with st.form("prediction_form"):
                tenure = st.slider("Tenure (Months)", 0, 72, 12)
                monthly_charges = st.number_input("Monthly Charges ($)", 0.0, 200.0, 50.0)
                total_charges = st.number_input("Total Charges ($)", 0.0, 10000.0, 500.0)
                contract_type = st.selectbox("Contract Type", ["Month-to-Month", "One Year", "Two Year"])
                internet_service = st.selectbox("Internet Service", ["Fiber Optic", "DSL", "No"]) # Not used in model currently but good for UI
                
                submitted = st.form_submit_button("Predict Risk")
        
        with col_pred:
            if submitted:
                # Prepare input
                input_data = {
                    "tenure": tenure,
                    "monthly_charges": monthly_charges,
                    "total_charges": total_charges,
                    "contract_type": contract_type
                }
                
                # Predict
                prob, pred_class = predictor.predict_single(input_data)
                
                # Display Result
                st.subheader("Risk Assessment")
                
                delta_color = "inverse" if pred_class == 1 else "normal"
                risk_label = "HIGH RISK" if pred_class == 1 else "SAFE"
                risk_color = "red" if pred_class == 1 else "green"
                
                st.metric(label="Churn Probability", value=f"{prob:.1%}", delta=risk_label, delta_color=delta_color)
                
                st.markdown(f"### Status: :{risk_color}[{risk_label}]")
                st.progress(float(prob))
                
                # Explanation (Feature Importance)
                st.markdown("---")
                st.subheader("Model Drivers (Global Importance)")
                importance_df = predictor.get_feature_importance()
                if not importance_df.empty:
                    st.dataframe(importance_df.head(5), hide_index=True)
            else:
                st.info("👈 Enter customer details and click Predict Risk")

if __name__ == "__main__":
    main()

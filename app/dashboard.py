from pathlib import Path
import base64
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="FinRisk-X | Financial Risk Intelligence",
    page_icon="📊",
    layout="wide"
)

ROOT = Path(r"C:\Users\lenovo\Desktop\FinRisk-X")
DATA = ROOT / "data" / "processed"
FIG = ROOT / "reports" / "figures"

# ============================================================
# FILES
# ============================================================

DASHBOARD = DATA / "finrisk_dashboard_data.csv"
KPI = DATA / "finrisk_dashboard_kpis.csv"

AGE = DATA / "fairness_age_analysis.csv"
EMP = DATA / "fairness_employment_analysis.csv"
AGE_DIS = DATA / "fairness_age_disparity.csv"
EMP_DIS = DATA / "fairness_employment_disparity.csv"

# ============================================================
# LOADERS
# ============================================================

@st.cache_data
def load(path, required=True):
    if not path.exists():
        if required:
            st.error(f"File not found:\n{path}")
            st.stop()
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Could not read {path.name}: {e}")
        st.stop()


df = load(DASHBOARD)
kpi = load(KPI, False)
age_df = load(AGE, False)
emp_df = load(EMP, False)
age_dis = load(AGE_DIS, False)
emp_dis = load(EMP_DIS, False)

# ============================================================
# CLEAN DATA
# ============================================================

if "customer_id" in df:
    df["customer_id"] = df["customer_id"].astype(str)

numeric = [
    "finrisk_score",
    "credit_risk_score",
    "temporal_risk_score",
    "fraud_risk_score",
    "graph_risk_score",
    "financial_health_risk_score",
    "calibrated_credit_probability",
    "credit_uncertainty_score",
    "credit_confidence_score",
    "age",
    "annual_income",
    "employment_years",
    "dependents",
    "savings",
    "existing_debt",
    "credit_score"
]

for c in numeric:
    if c in df:
        df[c] = pd.to_numeric(df[c], errors="coerce")

if "human_review_required" in df:
    df["human_review_required"] = (
        df["human_review_required"]
        .astype(str)
        .str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False,
            "yes": True,
            "no": False
        })
        .fillna(False)
    )
else:
    df["human_review_required"] = False

# ============================================================
# HELPERS
# ============================================================

def svg(name):
    path = FIG / name
    if path.exists():
        data = path.read_text(encoding="utf-8")
        encoded = base64.b64encode(data.encode()).decode()
        st.markdown(
            f'<img src="data:image/svg+xml;base64,{encoded}" '
            f'style="width:100%">',
            unsafe_allow_html=True
        )
        st.download_button(
            "Download SVG",
            data,
            file_name=name,
            mime="image/svg+xml"
        )

def metric(label, value):
    st.metric(label, value)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 FinRisk-X")
st.sidebar.caption("Financial Risk Intelligence Framework")

page = st.sidebar.radio(
    "Navigation",
    [
        "Executive Overview",
        "Customer Risk Explorer",
        "Risk Intelligence",
        "Uncertainty Analysis",
        "Decision Intelligence",
        "Fairness Analysis"
    ]
)

with st.sidebar.expander("🔧 Diagnostics"):
    st.write("Project:", ROOT)
    st.write("Rows:", len(df))
    st.write("Columns:", list(df.columns))

# ============================================================
# 1. EXECUTIVE OVERVIEW
# ============================================================

if page == "Executive Overview":

    st.title("📊 FinRisk-X Executive Overview")
    st.write(
        "Multi-modal, temporal and explainable financial risk intelligence."
    )

    total = len(df)
    avg = df["finrisk_score"].mean()
    median = df["finrisk_score"].median()
    high = (df["finrisk_score"] >= 50).sum()
    critical = (df["finrisk_score"] > 75).sum()

    a, b, c, d, e = st.columns(5)

    with a:
        metric("Customers", f"{total:,}")
    with b:
        metric("Average Risk", f"{avg:.2f}")
    with c:
        metric("Median Risk", f"{median:.2f}")
    with d:
        metric("High Risk", f"{high:,}")
    with e:
        metric("Critical Risk", f"{critical:,}")

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(
            df,
            x="finrisk_score",
            nbins=30,
            title="FinRisk Score Distribution"
        )
        st.plotly_chart(fig, width="stretch")

    with c2:
        if "risk_category" in df:
            fig = px.pie(
                df,
                names="risk_category",
                title="Risk Category Distribution"
            )
            st.plotly_chart(fig, width="stretch")

    components = [
        "credit_risk_score",
        "temporal_risk_score",
        "fraud_risk_score",
        "graph_risk_score",
        "financial_health_risk_score"
    ]

    available = [x for x in components if x in df]

    if available:
        means = df[available].mean().sort_values(ascending=False)
        fig = px.bar(
            x=means.index,
            y=means.values,
            title="Average Risk Component Scores",
            labels={"x": "Component", "y": "Average Score"}
        )
        st.plotly_chart(fig, width="stretch")

# ============================================================
# 2. CUSTOMER EXPLORER
# ============================================================

elif page == "Customer Risk Explorer":

    st.title("🔎 Customer Risk Explorer")

    customers = df["customer_id"].tolist()

    customer = st.selectbox(
        "Select Customer",
        customers
    )

    row = df[df["customer_id"] == customer].iloc[0]

    a, b, c, d = st.columns(4)

    with a:
        metric("FinRisk", f"{row['finrisk_score']:.2f}")

    with b:
        metric("Credit Risk", f"{row['credit_risk_score']:.2f}")

    with c:
        metric("Fraud Risk", f"{row['fraud_risk_score']:.2f}")

    with d:
        metric(
            "Uncertainty",
            f"{row.get('credit_uncertainty_score', 0):.3f}"
        )

    st.divider()

    components = {
        "Credit": row.get("credit_risk_score", 0),
        "Temporal": row.get("temporal_risk_score", 0),
        "Fraud": row.get("fraud_risk_score", 0),
        "Graph": row.get("graph_risk_score", 0),
        "Financial Health": row.get(
            "financial_health_risk_score", 0
        )
    }

    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=list(components.values()),
            theta=list(components.keys()),
            fill="toself",
            name="Risk Profile"
        )
    )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title="Customer Risk Profile"
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Customer Information")

    info = {
        "Age": row.get("age", "N/A"),
        "Employment": row.get("employment_type", "N/A"),
        "Income": row.get("annual_income", "N/A"),
        "Employment Years": row.get("employment_years", "N/A"),
        "Credit Score": row.get("credit_score", "N/A"),
        "Savings": row.get("savings", "N/A"),
        "Existing Debt": row.get("existing_debt", "N/A")
    }

    st.dataframe(
        pd.DataFrame(info.items(), columns=["Attribute", "Value"]),
        width="stretch",
        hide_index=True
    )

    st.subheader("Decision")

    st.info(row.get("decision", "N/A"))
    st.write("**Reason:**", row.get("decision_reason", "N/A"))
    st.write("**Recommended Action:**", row.get(
        "recommended_action", "N/A"
    ))

# ============================================================
# 3. RISK INTELLIGENCE
# ============================================================

elif page == "Risk Intelligence":

    st.title("🧠 Risk Intelligence")

    components = [
        "credit_risk_score",
        "temporal_risk_score",
        "fraud_risk_score",
        "graph_risk_score",
        "financial_health_risk_score"
    ]

    available = [x for x in components if x in df]

    if available:

        stats = df[available].describe().T
        st.subheader("Risk Component Statistics")
        st.dataframe(stats.round(3), width="stretch")

        means = df[available].mean().sort_values(ascending=False)

        fig = px.bar(
            x=means.index,
            y=means.values,
            title="Risk Component Benchmarking"
        )

        st.plotly_chart(fig, width="stretch")

        if len(available) >= 2:

            corr = df[available].corr()

            fig = px.imshow(
                corr,
                text_auto=".2f",
                title="Risk Component Correlation"
            )

            st.plotly_chart(fig, width="stretch")

    st.subheader("Research Analysis")

    svg("risk_component_benchmarking.svg")
    svg("risk_component_correlation.svg")

# ============================================================
# 4. UNCERTAINTY
# ============================================================

elif page == "Uncertainty Analysis":

    st.title("📐 Uncertainty & Calibration Analysis")

    uncertainty = df.get(
        "credit_uncertainty_score",
        pd.Series([0] * len(df))
    )

    avg_u = uncertainty.mean()
    high_u = (uncertainty >= 0.40).sum()
    low_u = (uncertainty < 0.20).sum()

    a, b, c = st.columns(3)

    with a:
        metric("Average Uncertainty", f"{avg_u:.3f}")

    with b:
        metric("High Uncertainty", f"{high_u:,}")

    with c:
        metric("Low Uncertainty", f"{low_u:,}")

    fig = px.histogram(
        df,
        x="credit_uncertainty_score",
        nbins=30,
        title="Credit Uncertainty Distribution"
    )

    fig.add_vline(
        x=0.40,
        line_dash="dash",
        annotation_text="Human Review Threshold"
    )

    st.plotly_chart(fig, width="stretch")

    fig = px.scatter(
        df,
        x="credit_uncertainty_score",
        y="finrisk_score",
        title="Risk vs Uncertainty",
        opacity=0.5
    )

    fig.add_vline(x=0.40, line_dash="dash")
    fig.add_hline(y=50, line_dash="dash")

    st.plotly_chart(fig, width="stretch")

    st.subheader("Research Figures")

    svg("credit_probability_calibration.svg")
    svg("credit_uncertainty_distribution.svg")
    svg("human_review_routing.svg")

# ============================================================
# 5. DECISION INTELLIGENCE
# ============================================================

elif page == "Decision Intelligence":

    st.title("⚖️ Decision Intelligence")

    if "decision" in df:

        decision_counts = df["decision"].value_counts()

        a, b = st.columns(2)

        with a:
            fig = px.pie(
                values=decision_counts.values,
                names=decision_counts.index,
                title="Decision Distribution"
            )
            st.plotly_chart(fig, width="stretch")

        with b:
            avg_risk = df.groupby(
                "decision"
            )["finrisk_score"].mean().sort_values()

            fig = px.bar(
                x=avg_risk.index,
                y=avg_risk.values,
                title="Average Risk by Decision"
            )
            st.plotly_chart(fig, width="stretch")

        review = df["human_review_required"].sum()
        review_rate = review / len(df) * 100

        a, b = st.columns(2)

        with a:
            metric("Human Reviews", f"{review:,}")

        with b:
            metric("Review Rate", f"{review_rate:.2f}%")

        st.subheader("Decision Records")

        cols = [
            "customer_id",
            "finrisk_score",
            "risk_category",
            "decision",
            "decision_reason",
            "recommended_action",
            "decision_confidence"
        ]

        cols = [x for x in cols if x in df]

        st.dataframe(
            df[cols].head(100),
            width="stretch",
            hide_index=True
        )

    st.subheader("Research Figures")

    svg("decision_distribution.svg")
    svg("average_risk_by_decision.svg")
    svg("uncertainty_aware_decision_routing.svg")

# ============================================================
# 6. FAIRNESS
# ============================================================

elif page == "Fairness Analysis":

    st.title("⚖️ Fairness & Bias Analysis")

    st.warning(
        "Disparity metrics are screening indicators, not proof of "
        "discrimination. Differences may reflect risk patterns, "
        "data quality, sample size or other factors."
    )

    if not age_df.empty:

        st.subheader("Age Group Analysis")
        st.dataframe(
            age_df.round(3),
            width="stretch",
            hide_index=True
        )

        numeric_cols = age_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:
            risk_col = next(
                (
                    x for x in numeric_cols
                    if "risk" in x.lower()
                ),
                numeric_cols[-1]
            )

            group_col = age_df.columns[0]

            fig = px.bar(
                age_df,
                x=group_col,
                y=risk_col,
                title="Risk by Age Group"
            )

            st.plotly_chart(fig, width="stretch")

    if not emp_df.empty:

        st.subheader("Employment Analysis")

        st.dataframe(
            emp_df.round(3),
            width="stretch",
            hide_index=True
        )

        numeric_cols = emp_df.select_dtypes(
            include="number"
        ).columns.tolist()

        if numeric_cols:
            risk_col = next(
                (
                    x for x in numeric_cols
                    if "risk" in x.lower()
                ),
                numeric_cols[-1]
            )

            group_col = emp_df.columns[0]

            fig = px.bar(
                emp_df,
                x=group_col,
                y=risk_col,
                title="Risk by Employment Type"
            )

            st.plotly_chart(fig, width="stretch")

    if not age_dis.empty:
        st.subheader("Age Disparity Analysis")
        st.dataframe(
            age_dis.round(3),
            width="stretch",
            hide_index=True
        )

    if not emp_dis.empty:
        st.subheader("Employment Disparity Analysis")
        st.dataframe(
            emp_dis.round(3),
            width="stretch",
            hide_index=True
        )

    st.subheader("Research Figures")

    svg("fairness_age_average_risk.svg")
    svg("fairness_age_high_risk_rate.svg")
    svg("fairness_employment_average_risk.svg")
    svg("fairness_employment_high_risk_rate.svg")

# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "FinRisk-X | Multi-Modal, Temporal and Explainable "
    "Financial Risk Intelligence Framework"
)
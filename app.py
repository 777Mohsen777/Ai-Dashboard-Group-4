
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Compact Excavator Dashboard", layout="wide")
st.title("📊 Excavator Dashboard (Clean Build)")

st.markdown("""
#### Upload Excel File with Columns:
- `Operating Hour`
- `Temperature`
- `Vibration`
- `Pressure`
- `Component_Type`
""")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

@st.cache_data
def load_data(file):
    return pd.read_excel(file)

def smooth_series(x, y):
    smoothed = lowess(y, x, frac=0.05, return_sorted=False)
    return smoothed

def line_chart(df, metric):
    fig, ax = plt.subplots(figsize=(7, 3))
    df["Operating Hour"] = pd.to_numeric(df["Operating Hour"], errors='coerce')
    for comp in df["Component_Type"].unique():
        comp_df = df[df["Component_Type"] == comp].copy()
        comp_df = comp_df.sort_values("Operating Hour")
        smoothed = smooth_series(comp_df["Operating Hour"], comp_df[metric])
        ax.plot(comp_df["Operating Hour"], smoothed, label=f"{comp}", linewidth=1.8)
    ax.set_title(f"{metric} vs Operating Hour", fontsize=12)
    ax.set_xlabel("Operating Hour")
    ax.set_ylabel(metric)
    ax.legend(fontsize=6, title="Component Type")
    ax.grid(True, linestyle="--", alpha=0.3)
    st.pyplot(fig)

def gauge(title, value, min_val, max_val, zones):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 12}},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "gray"},
            'steps': [{'range': zone[0], 'color': zone[1]} for zone in zones]
        }
    ))
    fig.update_layout(height=160, margin=dict(t=10, b=10, l=10, r=10))
    return fig

def component_zone(df):
    st.markdown("### 📉 Trends")
    c1, c2, c3 = st.columns(3)
    with c1:
        line_chart(df, "Temperature")
    with c2:
        line_chart(df, "Vibration")
    with c3:
        line_chart(df, "Pressure")

if uploaded_file:
    df = load_data(uploaded_file)
    expected = {"Operating Hour", "Temperature", "Vibration", "Pressure", "Component_Type"}
    if not expected.issubset(set(df.columns)):
        st.error(f"Missing columns: {expected - set(df.columns)}")
    else:
        df = df.sort_values("Operating Hour")
        component_zone(df)

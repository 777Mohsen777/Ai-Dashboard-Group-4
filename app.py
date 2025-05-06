
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Equipment Sensor Dashboard", layout="wide")
st.title("📊 Equipment Sensor Monitoring Dashboard")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file).round(3)
    st.success("✅ File uploaded successfully!")
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    failure_temp = df[df['Temperature'] >= 120].head(1)
    failure_vib = df[df['Vibration'] >= 2].head(1)
    failure_pres = df[df['Pressure'] <= 230].head(1)

    def plot_graph(ax, x, y, label, color, ylabel, title, failure_df):
        ax.scatter(df[x], df[y], color=color, s=5, label=label, alpha=0.6)
        smoothed = lowess(df[y], df[x], frac=0.02)
        ax.plot(smoothed[:, 0], smoothed[:, 1], color='black', linewidth=1.5, label='Performance')
        if not failure_df.empty:
            ax.scatter(failure_df[x], failure_df[y], color='red', s=100, marker='X', label='Failure')
        ax.set_xlabel("Operating Hours")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xlim([0, 5000])
        ax.set_ylim(bottom=0)
        ax.legend(fontsize=8)

    st.markdown("### 📈 Sensor Performance")
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.8))
    plot_graph(axs[0], 'Operating_Hours', 'Temperature', 'Engine Oil Temp', 'red', 'Temperature (°C)', 'Engine Temp Performance', failure_temp)
    plot_graph(axs[1], 'Operating_Hours', 'Vibration', 'Chassis Vibration', 'blue', 'Vibration (g)', 'Vibration Performance', failure_vib)
    plot_graph(axs[2], 'Operating_Hours', 'Pressure', 'Hydraulic Oil Pressure', 'green', 'Pressure (psi)', 'Hydraulic Pressure Performance', failure_pres)
    st.pyplot(fig)

    st.markdown("### 🧭 Live Performance Gauges")
    valid_df = df.dropna(subset=['Temperature', 'Vibration', 'Pressure'])
    if not valid_df.empty:
        latest = valid_df.iloc[-1]
        temp_val, vib_val, pres_val = float(latest['Temperature']), float(latest['Vibration']), float(latest['Pressure'])

        if pres_val <= 230:
            st.error("⚠️ WARNING: Hydraulic Pressure is below safe threshold!")

        def create_gauge(title, value, min_val, max_val, ranges):
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': title},
                gauge={
                    'axis': {'range': [min_val, max_val]},
                    'bar': {'color': "darkgray"},
                    'steps': [{'range': r[0], 'color': r[1]} for r in ranges]
                }
            ))
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            return fig

        col1, col2, col3 = st.columns(3)
        with col1:
            st.plotly_chart(create_gauge("Engine Temperature (°C)", temp_val, 0, 150, [
                ((0, 70), 'lightgreen'), ((70, 80), 'yellow'),
                ((80, 100), 'orange'), ((100, 120), 'red'), ((120, 150), 'black')
            ]), use_container_width=True)
        with col2:
            st.plotly_chart(create_gauge("Chassis Vibration (g)", vib_val, 0, 2.5, [
                ((0, 0.4), 'lightgreen'), ((0.4, 1), 'yellow'),
                ((1, 1.5), 'orange'), ((1.5, 2), 'red'), ((2, 2.5), 'black')
            ]), use_container_width=True)
        with col3:
            st.plotly_chart(create_gauge("Hydraulic Pressure (psi)", pres_val, 0, 400, [
                ((0, 230), 'white'), ((230, 260), 'red'),
                ((260, 270), 'orange'), ((270, 290), 'yellow'),
                ((290, 320), 'lightgreen'), ((320, 350), 'black'), ((350, 400), 'black')
            ]), use_container_width=True)
    else:
        st.error("❌ Sensor values are missing or invalid in the last row. Please check your data.")

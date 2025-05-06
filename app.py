import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess

# Set Streamlit page config
st.set_page_config(page_title="Equipment Sensor Dashboard", layout="wide")

st.title("📊 Equipment Sensor Monitoring Dashboard")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = df.round(3)

    st.success("✅ File uploaded successfully!")
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # Detect first failure values for each sensor
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
        ax.legend(fontsize=8)

    st.markdown("### 📈 Sensor Performance")
    fig, axs = plt.subplots(1, 3, figsize=(12, 3))
    plot_graph(axs[0], 'Operating_Hours', 'Temperature', 'Engine Oil Temp', 'red', 'Temperature (°C)', 'Engine Temp Performance', failure_temp)
    plot_graph(axs[1], 'Operating_Hours', 'Vibration', 'Chassis Vibration', 'blue', 'Vibration (g)', 'Vibration Performance', failure_vib)
    plot_graph(axs[2], 'Operating_Hours', 'Pressure', 'Hydraulic Oil Pressure', 'green', 'Pressure (psi)', 'Hydraulic Pressure Performance', failure_pres)
    st.pyplot(fig)

    st.markdown("### 🧭 Live Performance Gauges")

    latest = df.iloc[-1]
    temp_val = latest['Temperature']
    vib_val = latest['Vibration']
    pres_val = latest['Pressure']

    if pres_val <= 230:
        st.error("⚠️ WARNING: Hydraulic Pressure is below safe threshold!")

    def create_gauge(title, value, min_val, max_val, ranges, unit):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': ranges[0], 'color': 'white'},
                    {'range': ranges[1], 'color': 'red'},
                    {'range': ranges[2], 'color': 'orange'},
                    {'range': ranges[3], 'color': 'yellow'},
                    {'range': ranges[4], 'color': 'lightgreen'},
                    {'range': ranges[5], 'color': 'black'},
                ]
            }
        ))
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
        return fig

    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(create_gauge("Engine Temperature (°C)", temp_val, 0, 150,
                                      [(0, 70), (71, 80), (81, 100), (101, 120), (121, 140), (141, 150)], "°C"), use_container_width=True)
    with col2:
        st.plotly_chart(create_gauge("Chassis Vibration (g)", vib_val, 0, 2.5,
                                      [(0, 0.4), (0.41, 1), (1.01, 1.5), (1.51, 2), (2.01, 2.5), (2.5, 2.5)], "g"), use_container_width=True)
    with col3:
        st.plotly_chart(create_gauge("Hydraulic Pressure (psi)", pres_val, 0, 400,
                                      [(0, 230), (231, 250), (251, 270), (271, 280), (281, 350), (351, 400)], "psi"), use_container_width=True)

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Equipment Sensor Dashboard", layout="wide")
st.title("📊 Equipment Sensor Monitoring Dashboard")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df = df.round(3)
    st.success("✅ File uploaded successfully!")
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    # Detect first failure values
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

    latest = df.iloc[-1]
    temp_val = latest['Temperature']
    vib_val = latest['Vibration']
    pres_val = latest['Pressure']

    if pres_val <= 230:
        st.error("⚠️ WARNING: Hydraulic Pressure is below safe threshold!")

    def create_gauge(title, value, min_val, max_val, steps):
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [min_val, max_val]},
                'bar': {'color': "black"},
                'steps': steps
            }
        ))
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200)
        return fig

    col1, col2, col3 = st.columns(3)
    with col1:
        steps_temp = [{'range': (0, 70), 'color': 'lightgreen'},
                      {'range': (70, 80), 'color': 'yellow'},
                      {'range': (80, 100), 'color': 'orange'},
                      {'range': (100, 120), 'color': 'red'}]
        st.plotly_chart(create_gauge("Engine Temperature (°C)", temp_val, 0, 150, steps_temp), use_container_width=True)

    with col2:
        steps_vib = [{'range': (0, 0.4), 'color': 'lightgreen'},
                     {'range': (0.4, 1), 'color': 'yellow'},
                     {'range': (1, 1.5), 'color': 'orange'},
                     {'range': (1.5, 2), 'color': 'red'}]
        st.plotly_chart(create_gauge("Chassis Vibration (g)", vib_val, 0, 2.5, steps_vib), use_container_width=True)

    with col3:
        steps_pres = [{'range': (0, 230), 'color': 'white'},
                      {'range': (230, 260), 'color': 'red'},
                      {'range': (260, 270), 'color': 'orange'},
                      {'range': (270, 290), 'color': 'yellow'},
                      {'range': (290, 320), 'color': 'lightgreen'},
                      {'range': (320, 350), 'color': 'black'}]
        st.plotly_chart(create_gauge("Hydraulic Pressure (psi)", pres_val, 0, 400, steps_pres), use_container_width=True)

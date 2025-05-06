
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Equipment Sensor Monitoring Dashboard", layout="wide")

st.title("📊 Equipment Sensor Monitoring Dashboard")

uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.success("✅ File uploaded successfully!")
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    fig3, ax3 = plt.subplots()

    sns.scatterplot(data=df, x="Operating_Hours", y="Temperature", color="red", ax=ax1, label="Engine Oil Temp")
    temp_smooth = lowess(df["Temperature"], df["Operating_Hours"])
    ax1.plot(temp_smooth[:, 0], temp_smooth[:, 1], color="black", label="Performance")
    failures_temp = df[df["Temperature"] >= 120]
    ax1.scatter(failures_temp["Operating_Hours"], failures_temp["Temperature"], color="red", s=100, label="Failure", marker="X")
    ax1.set_ylim(0, 150)
    ax1.set_title("Engine Temperature Performance")
    ax1.set_ylabel("Temperature (°C)")
    ax1.set_xlabel("Operating Hours")
    ax1.legend()

    sns.scatterplot(data=df, x="Operating_Hours", y="Vibration", color="blue", ax=ax2, label="Chassis Vibration")
    vib_smooth = lowess(df["Vibration"], df["Operating_Hours"])
    ax2.plot(vib_smooth[:, 0], vib_smooth[:, 1], color="black", label="Performance")
    failures_vib = df[df["Vibration"] >= 2]
    ax2.scatter(failures_vib["Operating_Hours"], failures_vib["Vibration"], color="red", s=100, label="Failure", marker="X")
    ax2.set_ylim(0, 2.5)
    ax2.set_title("Vibration Performance")
    ax2.set_ylabel("Vibration (g)")
    ax2.set_xlabel("Operating Hours")
    ax2.legend()

    sns.scatterplot(data=df, x="Operating_Hours", y="Pressure", color="green", ax=ax3, label="Hydraulic Oil Pressure")
    press_smooth = lowess(df["Pressure"], df["Operating_Hours"])
    ax3.plot(press_smooth[:, 0], press_smooth[:, 1], color="black", label="Performance")
    failures_press = df[df["Pressure"] <= 230]
    ax3.scatter(failures_press["Operating_Hours"], failures_press["Pressure"], color="red", s=100, label="Failure", marker="X")
    ax3.set_ylim(0, 400)
    ax3.set_title("Hydraulic Oil Pressure Performance")
    ax3.set_ylabel("Pressure (psi)")
    ax3.set_xlabel("Operating Hours")
    ax3.legend()

    st.pyplot(fig1)
    st.pyplot(fig2)
    st.pyplot(fig3)

    st.subheader("🟢 Live Performance Gauges")

    latest_row = df.iloc[-1]
    pressure_warning = latest_row["Pressure"] <= 230
    if pressure_warning:
        st.error("⚠️ WARNING: Hydraulic Pressure is below safe threshold!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_row["Temperature"],
            title={"text": "Engine Temperature (°C)"},
            gauge={
                "axis": {"range": [None, 120]},
                "bar": {"color": "black"},
                "steps": [
                    {"range": [0, 70], "color": "lightgreen"},
                    {"range": [70, 80], "color": "yellow"},
                    {"range": [80, 100], "color": "orange"},
                    {"range": [100, 120], "color": "red"},
                ]
            }
        )), use_container_width=True)

    with col2:
        st.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_row["Vibration"],
            title={"text": "Chassis Vibration (g)"},
            gauge={
                "axis": {"range": [None, 2]},
                "bar": {"color": "black"},
                "steps": [
                    {"range": [0, 0.4], "color": "lightgreen"},
                    {"range": [0.4, 1], "color": "yellow"},
                    {"range": [1, 1.5], "color": "orange"},
                    {"range": [1.5, 2], "color": "red"},
                ]
            }
        )), use_container_width=True)

    with col3:
        st.plotly_chart(go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_row["Pressure"],
            title={"text": "Hydraulic Pressure (psi)"},
            gauge={
                "axis": {"range": [None, 320]},
                "bar": {"color": "black"},
                "steps": [
                    {"range": [290, 320], "color": "lightgreen"},
                    {"range": [270, 290], "color": "yellow"},
                    {"range": [260, 270], "color": "orange"},
                    {"range": [0, 260], "color": "red"},
                ]
            }
        )), use_container_width=True)

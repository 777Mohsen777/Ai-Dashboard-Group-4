
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess
from io import BytesIO

st.set_page_config(page_title="Full PDF Export Dashboard", layout="wide")
st.title("📊 Equipment Sensor Dashboard")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    plt.style.use("dark_background")
    st.markdown("""
        <style>
        body, .stApp, .block-container { background-color: #0e1117; color: white; }
        .stPlotlyChart, .stButton, .stDataFrame, .stMarkdown, .stSlider { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

def rating_color(val, limits):
    for threshold, percent, color in limits:
        if val <= threshold:
            return percent, color
    return 0, "black"

def donut_chart_matplotlib(title, percent, color):
    fig, ax = plt.subplots(figsize=(2.5, 2.5))
    ax.pie([percent, 100 - percent], radius=1.0, startangle=90, colors=[color, "#f0f0f0"],
           wedgeprops=dict(width=0.3, edgecolor='white'))
    ax.set(aspect="equal")
    ax.text(0, 0, f"{percent:.0f}%", ha='center', va='center', fontsize=12, color='black' if color != 'black' else 'white')
    ax.set_title(title)
    return fig

def plot_sensor_data(df, failures):
    fig, axs = plt.subplots(1, 3, figsize=(10, 3), dpi=100, constrained_layout=True)
    metrics = [("Temperature", "Temp (°C)", "red"),
               ("Vibration", "Vibration (g)", "blue"),
               ("Pressure", "Pressure (psi)", "green")]
    for i, (col, ylabel, color) in enumerate(metrics):
        ax = axs[i]
        ax.scatter(df["Operating_Hours"], df[col], s=3, c=color, label=col)
        smooth = lowess(df[col], df["Operating_Hours"], frac=0.02)
        ax.plot(smooth[:, 0], smooth[:, 1], color="black", lw=1.5, label="Performance")
        if not failures[i].empty:
            ax.scatter(failures[i]["Operating_Hours"], failures[i][col],
                       color="red", s=60, marker="X", label="Failure")
        ax.set_title(col)
        ax.set_xlabel("Hrs")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=6)
    return fig

if uploaded_file:
    df = pd.read_excel(uploaded_file).round(3)
    st.success("✅ File uploaded successfully!")
    st.dataframe(df.head(), height=120)

    # Failures
    f_temp = df[df['Temperature'] >= 120].head(1)
    f_vib = df[df['Vibration'] >= 2].head(1)
    f_pres = df[df['Pressure'] <= 230].head(1)
    failures = [f_temp, f_vib, f_pres]

    st.markdown("#### Sensor Performance")
    sensor_fig = plot_sensor_data(df, failures)
    st.pyplot(sensor_fig)

    df_clean = df.dropna()
    selected_hour = st.slider("Select Operating Hour", int(df_clean["Operating_Hours"].min()),
                              int(df_clean["Operating_Hours"].max()))
    row = df_clean.iloc[(df_clean["Operating_Hours"] - selected_hour).abs().argsort()[:1]]
    temp, vib, pres = float(row["Temperature"]), float(row["Vibration"]), float(row["Pressure"])

    st.markdown("#### Health Ratings")
    r1, c1 = rating_color(temp, [(70, 100, "green"), (80, 75, "yellow"), (100, 45, "orange"), (120, 15, "red")])
    r2, c2 = rating_color(vib, [(0.4, 100, "green"), (1, 75, "yellow"), (1.5, 45, "orange"), (2, 15, "red")])
    r3, c3 = rating_color(pres, [(230, 15, "red"), (260, 45, "orange"), (290, 75, "yellow"), (320, 100, "green")])

    if st.button("📄 Download PDF Report"):
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            # Page 1: Sensor Graphs
            pdf.savefig(sensor_fig)
            # Page 2: Summary
            fig2, ax = plt.subplots(figsize=(6, 1.8))
            ax.axis("off")
            text = f"Selected Hour: {selected_hour}\nTemp: {temp} °C | Vibration: {vib} g | Pressure: {pres} psi"
            ax.text(0.5, 0.5, text, ha="center", va="center", fontsize=12)
            pdf.savefig(fig2)
            # Page 3: Donut charts
            d1 = donut_chart_matplotlib("Temp", r1, c1)
            d2 = donut_chart_matplotlib("Vibration", r2, c2)
            d3 = donut_chart_matplotlib("Pressure", r3, c3)
            pdf.savefig(d1)
            pdf.savefig(d2)
            pdf.savefig(d3)
        buffer.seek(0)
        st.download_button("📥 Save PDF", data=buffer, file_name="dashboard_with_ratings.pdf", mime="application/pdf")

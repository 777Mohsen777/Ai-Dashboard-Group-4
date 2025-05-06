
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess
from io import BytesIO

st.set_page_config(page_title="Final Dashboard", layout="wide")
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

def gauge_plot(title, value, min_val, max_val, zones):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "gray"},
            'steps': [{'range': zone[0], 'color': zone[1]} for zone in zones]
        }
    ))
    fig.update_layout(height=200, margin=dict(t=10, b=10, l=10, r=10))
    return fig

def donut_chart(title, percent, color):
    fig = go.Figure(data=[go.Pie(values=[percent, 100 - percent], hole=0.7,
                                 marker_colors=[color, "#f0f0f0"],
                                 textinfo="none")])
    fig.update_layout(
        showlegend=False,
        annotations=[
            dict(text=f"{int(percent)}%", x=0.5, y=0.5, font_size=18, showarrow=False),
            dict(text=title, x=0.5, y=0.2, font_size=12, showarrow=False)
        ],
        height=200,
        width=200,
        margin=dict(t=10, b=10, l=10, r=10)
    )
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

    st.markdown("#### Live Performance Gauges")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(gauge_plot("Temp (°C)", temp, 0, 150, [((0, 70), "lightgreen"), ((70, 80), "yellow"),
            ((80, 100), "orange"), ((100, 120), "red"), ((120, 150), "black")]), use_container_width=True)
    with c2:
        st.plotly_chart(gauge_plot("Vibration (g)", vib, 0, 2.5, [((0, 0.4), "lightgreen"), ((0.4, 1), "yellow"),
            ((1, 1.5), "orange"), ((1.5, 2), "red"), ((2, 2.5), "black")]), use_container_width=True)
    with c3:
        st.plotly_chart(gauge_plot("Pressure (psi)", pres, 0, 400, [((0, 230), "white"), ((230, 260), "red"),
            ((260, 270), "orange"), ((270, 290), "yellow"), ((290, 320), "lightgreen"), ((320, 400), "black")]), use_container_width=True)

    st.markdown("#### Component Health Ratings")
    r1, c1 = rating_color(temp, [(70, 100, "green"), (80, 75, "yellow"), (100, 45, "orange"), (120, 15, "red")])
    r2, c2 = rating_color(vib, [(0.4, 100, "green"), (1, 75, "yellow"), (1.5, 45, "orange"), (2, 15, "red")])
    r3, c3 = rating_color(pres, [(230, 15, "red"), (260, 45, "orange"), (290, 75, "yellow"), (320, 100, "green")])

    d1, d2, d3 = donut_chart("Temp", r1, c1), donut_chart("Vibration", r2, c2), donut_chart("Pressure", r3, c3)
    col1, col2, col3 = st.columns(3)
    with col1: st.plotly_chart(d1, use_container_width=True)
    with col2: st.plotly_chart(d2, use_container_width=True)
    with col3: st.plotly_chart(d3, use_container_width=True)

    
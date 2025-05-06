
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess
import plotly.graph_objects as go
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Unified PDF Dashboard", layout="wide")
st.title("📊 Unified Dashboard Snapshot")

uploaded_file = st.file_uploader("📂 Upload Excel", type=["xlsx"])
dark_mode = st.sidebar.toggle("🌙 Dark Mode")

if dark_mode:
    plt.style.use("dark_background")
    st.markdown("""
        <style>
        body, .stApp, .block-container { background-color: #0e1117; color: white; }
        .stPlotlyChart, .stButton, .stDataFrame, .stMarkdown, .stSlider { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

def donut_image(percent, label, color):
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.pie([percent, 100 - percent], startangle=90, colors=[color, "#f0f0f0"],
           wedgeprops=dict(width=0.3, edgecolor='w'))
    ax.text(0, 0, f"{percent:.0f}%", ha='center', va='center', fontsize=12)
    ax.set_title(label)
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=150)
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf)

def rating_color(val, limits):
    for threshold, percent, color in limits:
        if val <= threshold:
            return percent, color
    return 0, "black"

if uploaded_file:
    df = pd.read_excel(uploaded_file).round(3)
    st.success("✅ File uploaded successfully")
    df = df.dropna()
    selected_hour = st.slider("Select Hour", int(df["Operating_Hours"].min()), int(df["Operating_Hours"].max()))
    row = df.iloc[(df["Operating_Hours"] - selected_hour).abs().argsort()[:1]]
    temp, vib, pres = float(row["Temperature"]), float(row["Vibration"]), float(row["Pressure"])

    st.markdown("### Dashboard Components")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Temperature (°C)", f"{temp}")
    with col2:
        st.metric("Vibration (g)", f"{vib}")
    with col3:
        st.metric("Pressure (psi)", f"{pres}")

    r1, c1 = rating_color(temp, [(70, 100, "green"), (80, 75, "yellow"), (100, 45, "orange"), (120, 15, "red")])
    r2, c2 = rating_color(vib, [(0.4, 100, "green"), (1, 75, "yellow"), (1.5, 45, "orange"), (2, 15, "red")])
    r3, c3 = rating_color(pres, [(230, 15, "red"), (260, 45, "orange"), (290, 75, "yellow"), (320, 100, "green")])

    # Create one large figure
    fig, axs = plt.subplots(1, 3, figsize=(10, 3))
    for ax, col, color, ylab in zip(axs, ['Temperature', 'Vibration', 'Pressure'],
                                    ['red', 'blue', 'green'],
                                    ['Temp (°C)', 'Vibration (g)', 'Pressure (psi)']):
        ax.scatter(df['Operating_Hours'], df[col], c=color, s=3)
        smooth = lowess(df[col], df['Operating_Hours'], frac=0.02)
        ax.plot(smooth[:, 0], smooth[:, 1], 'k', lw=1.5)
        ax.set_title(col)
        ax.set_xlabel("Hrs")
        ax.set_ylabel(ylab)
    fig.tight_layout()
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=150)
    buffer.seek(0)
    sensor_image = Image.open(buffer)
    plt.close(fig)

    # Compose donut summary image
    donut1 = donut_image(r1, "Temp", c1)
    donut2 = donut_image(r2, "Vibration", c2)
    donut3 = donut_image(r3, "Pressure", c3)
    width = sensor_image.width
    full_height = sensor_image.height + donut1.height + 40

    # Merge everything into one image
    final_image = Image.new("RGB", (width, full_height), "white")
    final_image.paste(sensor_image, (0, 0))
    final_image.paste(donut1, (0, sensor_image.height + 10))
    final_image.paste(donut2, (donut1.width + 10, sensor_image.height + 10))
    final_image.paste(donut3, (2 * donut1.width + 20, sensor_image.height + 10))

    # Export to PDF
    pdf_buffer = BytesIO()
    final_image.save(pdf_buffer, format="PDF")
    pdf_buffer.seek(0)
    st.download_button("📥 Download Full Dashboard PDF", data=pdf_buffer,
                       file_name="full_dashboard_snapshot.pdf", mime="application/pdf")

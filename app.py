
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Equipment Sensor Dashboard", layout="wide")
st.title("📊 Equipment Sensor Monitoring Dashboard")

uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

def temp_rating(val):
    if val <= 70:
        return 100, "green"
    elif val <= 80:
        return 75, "yellow"
    elif val <= 100:
        return 45, "orange"
    elif val <= 120:
        return 15, "red"
    else:
        return 0, "black"

def vib_rating(val):
    if val <= 0.4:
        return 100, "green"
    elif val <= 1:
        return 75, "yellow"
    elif val <= 1.5:
        return 45, "orange"
    elif val <= 2:
        return 15, "red"
    else:
        return 0, "black"

def pres_rating(val):
    if val >= 320:
        return 100, "green"
    elif val >= 290:
        return 75, "yellow"
    elif val >= 270:
        return 45, "orange"
    elif val >= 230:
        return 15, "red"
    else:
        return 0, "black"

def donut_chart(title, percent, color):
    return go.Figure(data=[
        go.Pie(
            values=[percent, 100 - percent],
            hole=0.7,
            marker_colors=[color, "#f0f0f0"],
            textinfo='none',
            hoverinfo='skip'
        )
    ]).update_layout(
        showlegend=False,
        annotations=[
            dict(text=f"{int(percent)}%", x=0.5, y=0.5, font_size=24, showarrow=False),
            dict(text=title, x=0.5, y=0.2, font_size=14, showarrow=False)
        ],
        margin=dict(t=10, b=10, l=10, r=10),
        height=250,
        width=250
    )

if uploaded_file:
    df = pd.read_excel(uploaded_file).round(3)
    st.success("✅ File uploaded successfully!")
    st.subheader("📄 Data Preview")
    st.dataframe(df.head())

    failure_temp = df[df['Temperature'] >= 120].head(1)
    failure_vib = df[df['Vibration'] >= 2].head(1)
    failure_pres = df[df['Pressure'] <= 230].head(1)

    st.markdown("### 📈 Sensor Performance")
    fig, axs = plt.subplots(1, 3, figsize=(10, 2.8))
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
    plot_graph(axs[0], 'Operating_Hours', 'Temperature', 'Engine Oil Temp', 'red', 'Temperature (°C)', 'Engine Temp Performance', failure_temp)
    plot_graph(axs[1], 'Operating_Hours', 'Vibration', 'Chassis Vibration', 'blue', 'Vibration (g)', 'Vibration Performance', failure_vib)
    plot_graph(axs[2], 'Operating_Hours', 'Pressure', 'Hydraulic Oil Pressure', 'green', 'Pressure (psi)', 'Hydraulic Pressure Performance', failure_pres)
    st.pyplot(fig)

    st.markdown("### ⏱️ Select Specific Operating Hour")
    valid_df = df.dropna(subset=['Operating_Hours', 'Temperature', 'Vibration', 'Pressure'])
    if not valid_df.empty:
        selected_hour = st.slider("Select Operating Hour:", int(valid_df['Operating_Hours'].min()), int(valid_df['Operating_Hours'].max()), step=1)
        row = valid_df.iloc[(valid_df['Operating_Hours'] - selected_hour).abs().argsort()[:1]]
        temp_val, vib_val, pres_val = float(row['Temperature']), float(row['Vibration']), float(row['Pressure'])

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

        st.markdown("### 🧭 Live Performance Gauges")
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

        st.markdown("### 💠 Component Health Ratings")
        r1, c1 = temp_rating(temp_val)
        r2, c2 = vib_rating(vib_val)
        r3, c3 = pres_rating(pres_val)
        col4, col5, col6 = st.columns(3)
        with col4:
            st.plotly_chart(donut_chart("Temperature", r1, c1), use_container_width=True)
        with col5:
            st.plotly_chart(donut_chart("Vibration", r2, c2), use_container_width=True)
        with col6:
            st.plotly_chart(donut_chart("Pressure", r3, c3), use_container_width=True)

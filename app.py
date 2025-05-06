import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Sensor Data Dashboard", layout="wide")
st.title("📊 Equipment Sensor Monitoring Dashboard")

uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx"])

def draw_gauge(title, value, max_val, steps, bar_color):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [0, max_val]},
            'bar': {'color': 'lightgray'},
        'gauge': {
            'axis': {'range': [None, max_value]},
            'steps': steps,
            'threshold': None
        },
        'pointer': {'color': 'black'},
        'value': failure_value if failure_value else value,
            'steps': steps
        }
    ))

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("✅ File uploaded successfully!")
        st.subheader("📄 Data Preview")
        st.dataframe(df.head())

        required_columns = ['Operating_Hours', 'Temperature', 'Vibration', 'Pressure']
        if all(col in df.columns for col in required_columns):

            failure_temp = df[df['Temperature'] >= 120]
            failure_vib = df[df['Vibration'] > 2.0]
            failure_press = df[df['Pressure'] < 230]

            col1, col2, col3 = st.columns(3)

            with col1:
                fig1, ax1 = plt.subplots(figsize=(4.5, 2.8))
                ax1.scatter(df['Operating_Hours'], df['Temperature'], color='red', alpha=0.5, s=10, label='Engine Oil Temp')
                smoothed = lowess(df['Temperature'], df['Operating_Hours'], frac=0.1)
                ax1.plot(smoothed[:, 0], smoothed[:, 1], color='black', linewidth=2, label='Performance')
                ax1.scatter(failure_temp['Operating_Hours'], failure_temp['Temperature'], color='red', marker='x', s=130, linewidths=2.5, label='Failure')
                ax1.set_title("Engine Temperature Performance")
                ax1.set_xlabel("Operating Hours")
                ax1.set_ylabel("Temperature (°C)")
                ax1.set_ylim(0, 150)
                ax1.set_xlim(left=0)
                ax1.grid(True)
                ax1.legend()
                st.pyplot(fig1)

            with col2:
                fig2, ax2 = plt.subplots(figsize=(4.5, 2.8))
                ax2.scatter(df['Operating_Hours'], df['Vibration'], color='blue', alpha=0.5, s=10, label='Chassis Vibration')
                smoothed = lowess(df['Vibration'], df['Operating_Hours'], frac=0.1)
                ax2.plot(smoothed[:, 0], smoothed[:, 1], color='black', linewidth=2, label='Performance')
                ax2.scatter(failure_vib['Operating_Hours'], failure_vib['Vibration'], color='red', marker='x', s=130, linewidths=2.5, label='Failure')
                ax2.set_title("Vibration Performance")
                ax2.set_xlabel("Operating Hours")
                ax2.set_ylabel("Vibration (g)")
                ax2.set_ylim(0, 2.5)
                ax2.set_xlim(left=0)
                ax2.grid(True)
                ax2.legend()
                st.pyplot(fig2)

            with col3:
                fig3, ax3 = plt.subplots(figsize=(4.5, 2.8))
                ax3.scatter(df['Operating_Hours'], df['Pressure'], color='green', alpha=0.5, s=10, label='Hydraulic Oil Pressure')
                smoothed = lowess(df['Pressure'], df['Operating_Hours'], frac=0.1)
                ax3.plot(smoothed[:, 0], smoothed[:, 1], color='black', linewidth=2, label='Performance')
                ax3.scatter(failure_press['Operating_Hours'], failure_press['Pressure'], color='red', marker='x', s=130, linewidths=2.5, label='Failure')
                ax3.set_title("Hydraulic Oil Pressure Performance")
                ax3.set_xlabel("Operating Hours")
                ax3.set_ylabel("Pressure (psi)")
                ax3.set_ylim(0, 400)
                ax3.set_xlim(left=0)
                ax3.grid(True)
                ax3.legend()
                st.pyplot(fig3)

            # Latest values
            latest_temp = df['Temperature'].dropna().iloc[-1]
            latest_vib = df['Vibration'].dropna().iloc[-1]
            latest_press = df['Pressure'].dropna().iloc[-1]

            st.subheader("📟 Live Performance Gauges")

            # Warnings
            if latest_temp >= 120:
                st.error("⚠️ WARNING: Engine Temperature has exceeded the safe limit!")
            if latest_vib > 2.0:
                st.error("⚠️ WARNING: Vibration level is critically high!")
            if latest_press < 230:
                st.error("⚠️ WARNING: Hydraulic Pressure is below safe threshold!")

            g1, g2, g3 = st.columns(3)

            with g1:
                temp_gauge = draw_gauge("Engine Temperature (°C)", latest_temp, 120, [
                    {'range': [0, 70], 'color': "lightgreen"},
                    {'range': [71, 80], 'color': "yellow"},
                    {'range': [81, 100], 'color': "orange"},
                    {'range': [101, 120], 'color': "red"}], "darkred")
                st.plotly_chart(temp_gauge, use_container_width=True)

            with g2:
                vib_gauge = draw_gauge("Chassis Vibration (g)", latest_vib, 2.0, [
                    {'range': [0, 0.4], 'color': "lightgreen"},
                    {'range': [0.41, 1.0], 'color': "yellow"},
                    {'range': [1.01, 1.5], 'color': "orange"},
                    {'range': [1.51, 2.0], 'color': "red"}], "darkblue")
                st.plotly_chart(vib_gauge, use_container_width=True)

            with g3:
                press_gauge = draw_gauge("Hydraulic Pressure (psi)", latest_press, 320, [
                    {'range': [0, 260], 'color': "red"},
                    {'range': [260, 270], 'color': "orange"},
                    {'range': [270, 290], 'color': "yellow"},
                    {'range': [290, 320], 'color': "lightgreen"}], "darkgreen")
                st.plotly_chart(press_gauge, use_container_width=True)

        else:
            st.warning("⚠️ Excel file must include: Operating_Hours, Temperature, Vibration, Pressure")
    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("👆 Upload an Excel file to begin.")

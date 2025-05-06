import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Sensor Data Dashboard", layout="wide")
st.title("📊 Equipment Sensor Monitoring Dashboard")

uploaded_file = st.file_uploader("📤 Upload your Excel file", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("✅ File uploaded successfully!")

        st.subheader("📄 Data Preview")
        st.dataframe(df.head())

        required_columns = ['Operating_Hours', 'Temperature', 'Vibration', 'Pressure']
        if all(col in df.columns for col in required_columns):

            # Detect failure points
            failure_temp = df[df['Temperature'] >= 120]
            failure_vib = df[df['Vibration'] > 2.0]
            failure_press = df[df['Pressure'] < 230]

            fig, axes = plt.subplots(1, 3, figsize=(24, 6), constrained_layout=True)

            # Engine Temperature performance
            axes[0].scatter(df['Operating_Hours'], df['Temperature'], color='red', alpha=0.4, label='Raw')
            smoothed = lowess(df['Temperature'], df['Operating_Hours'], frac=0.1)
            axes[0].plot(smoothed[:, 0], smoothed[:, 1], color='black', linewidth=2, label='Performance')
            axes[0].scatter(failure_temp['Operating_Hours'], failure_temp['Temperature'], color='red', marker='x', s=100, label='Failure')
            axes[0].set_title("Engine Temperature Performance")
            axes[0].set_xlabel("Operating Hours")
            axes[0].set_ylabel("Temperature (°C)")
            axes[0].set_ylim(0, 150)
            axes[0].grid(True)
            axes[0].legend()

            # Vibration performance
            axes[1].scatter(df['Operating_Hours'], df['Vibration'], color='blue', alpha=0.4, label='Raw')
            smoothed = lowess(df['Vibration'], df['Operating_Hours'], frac=0.1)
            axes[1].plot(smoothed[:, 0], smoothed[:, 1], color='black', linewidth=2, label='Performance')
            axes[1].scatter(failure_vib['Operating_Hours'], failure_vib['Vibration'], color='red', marker='x', s=100, label='Failure')
            axes[1].set_title("Vibration Performance")
            axes[1].set_xlabel("Operating Hours")
            axes[1].set_ylabel("Vibration (g)")
            axes[1].set_ylim(0, 2.5)
            axes[1].grid(True)
            axes[1].legend()

            # Hydraulic Oil Pressure performance
            axes[2].scatter(df['Operating_Hours'], df['Pressure'], color='green', alpha=0.4, label='Raw')
            smoothed = lowess(df['Pressure'], df['Operating_Hours'], frac=0.1)
            axes[2].plot(smoothed[:, 0], smoothed[:, 1], color='black', linewidth=2, label='Performance')
            axes[2].scatter(failure_press['Operating_Hours'], failure_press['Pressure'], color='red', marker='x', s=100, label='Failure')
            axes[2].set_title("Hydraulic Oil Pressure Performance")
            axes[2].set_xlabel("Operating Hours")
            axes[2].set_ylabel("Pressure (psi)")
            axes[2].set_ylim(0, 400)
            axes[2].grid(True)
            axes[2].legend()

            st.pyplot(fig)

        else:
            st.warning("⚠️ Excel file must include these columns: Operating_Hours, Temperature, Vibration, Pressure")
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("👆 Upload an Excel file to begin.")

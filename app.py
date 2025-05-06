import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.nonparametric.smoothers_lowess import lowess

st.set_page_config(page_title="Sensor Data Dashboard", layout="wide")
st.title("📊 Simplified Sensor Data Dashboard")

uploaded_file = st.file_uploader("📤 Upload your Excel file (must have Operating_Hours, Temperature, Vibration, Pressure)", type=["xlsx"])

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("✅ File uploaded successfully!")

        st.subheader("📄 Data Preview")
        st.dataframe(df.head())

        required_columns = ['Operating_Hours', 'Temperature', 'Vibration', 'Pressure']
        if all(col in df.columns for col in required_columns):
            # Setup multi-plot layout
            fig, axes = plt.subplots(1, 3, figsize=(21, 5))  # wide layout

            # Temperature vs Operating Hours
            axes[0].scatter(df['Operating_Hours'], df['Temperature'], color='red', alpha=0.4, label='Raw Data')
            temp_smooth = lowess(df['Temperature'], df['Operating_Hours'], frac=0.1)
            axes[0].plot(temp_smooth[:, 0], temp_smooth[:, 1], color='black', linewidth=2, label='LOWESS')
            axes[0].set_title("Temperature vs Operating Hours")
            axes[0].set_xlabel("Operating Hours")
            axes[0].set_ylabel("Temperature (°C)")
            axes[0].grid(True)
            axes[0].legend()

            # Vibration vs Operating Hours
            axes[1].scatter(df['Operating_Hours'], df['Vibration'], color='blue', alpha=0.4, label='Raw Data')
            vib_smooth = lowess(df['Vibration'], df['Operating_Hours'], frac=0.1)
            axes[1].plot(vib_smooth[:, 0], vib_smooth[:, 1], color='black', linewidth=2, label='LOWESS')
            axes[1].set_title("Vibration vs Operating Hours")
            axes[1].set_xlabel("Operating Hours")
            axes[1].set_ylabel("Vibration (g)")
            axes[1].grid(True)
            axes[1].legend()

            # Pressure vs Operating Hours
            axes[2].scatter(df['Operating_Hours'], df['Pressure'], color='green', alpha=0.4, label='Raw Data')
            pres_smooth = lowess(df['Pressure'], df['Operating_Hours'], frac=0.1)
            axes[2].plot(pres_smooth[:, 0], pres_smooth[:, 1], color='black', linewidth=2, label='LOWESS')
            axes[2].set_title("Pressure vs Operating Hours")
            axes[2].set_xlabel("Operating Hours")
            axes[2].set_ylabel("Pressure (bar)")
            axes[2].grid(True)
            axes[2].legend()

            st.pyplot(fig)

        else:
            st.warning("⚠️ Excel file must include these columns: " + ", ".join(required_columns))
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("👆 Upload an Excel file to start.")

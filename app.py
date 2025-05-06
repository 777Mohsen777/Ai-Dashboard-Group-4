import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
            # Temperature Plot
            fig1, ax1 = plt.subplots()
            ax1.plot(df['Operating_Hours'], df['Temperature'], color='red')
            ax1.set_title("Temperature vs Operating Hours")
            ax1.set_xlabel("Operating Hours")
            ax1.set_ylabel("Temperature (°C)")
            st.pyplot(fig1)

            # Vibration Plot
            fig2, ax2 = plt.subplots()
            ax2.plot(df['Operating_Hours'], df['Vibration'], color='blue')
            ax2.set_title("Vibration vs Operating Hours")
            ax2.set_xlabel("Operating Hours")
            ax2.set_ylabel("Vibration (g)")
            st.pyplot(fig2)

            # Pressure Plot
            fig3, ax3 = plt.subplots()
            ax3.plot(df['Operating_Hours'], df['Pressure'], color='green')
            ax3.set_title("Pressure vs Operating Hours")
            ax3.set_xlabel("Operating Hours")
            ax3.set_ylabel("Pressure (bar)")
            st.pyplot(fig3)
        else:
            st.warning("⚠️ Excel file must include these columns: " + ", ".join(required_columns))
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("👆 Upload an Excel file to start.")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set page title and layout
st.set_page_config(page_title="Sensor Data Dashboard", layout="wide")

st.title("📊 Sensor Data Upload & Visualization")

# Step 1: Upload Excel file
uploaded_file = st.file_uploader("📤 Upload your Excel (.xlsx) file", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Step 2: Read the uploaded Excel file
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.success("✅ File uploaded successfully!")

        # Step 3: Display a preview of the data
        st.subheader("📄 Data Preview")
        st.dataframe(df.head())

        # Step 4: Detect numeric columns
        numeric_cols = df.select_dtypes(include='number').columns.tolist()

        if len(numeric_cols) >= 2:
            # Step 5: Let user pick X and Y for chart
            x_axis = st.selectbox("Select X-axis", numeric_cols)
            y_axis = st.selectbox("Select Y-axis", numeric_cols, index=1)

            # Step 6: Plot line chart
            st.subheader(f"📈 {y_axis} vs {x_axis}")
            fig, ax = plt.subplots()
            ax.plot(df[x_axis], df[y_axis], marker='o')
            ax.set_xlabel(x_axis)
            ax.set_ylabel(y_axis)
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.warning("⚠️ Your file must contain at least two numeric columns.")
    except Exception as e:
        st.error(f"❌ Failed to read Excel file: {e}")
else:
    st.info("👆 Upload your Excel file above to begin.")


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="Compact Excavator Dashboard", layout="wide")
st.title("📊 Excavator Dashboard (Final Clean Version)")

st.markdown("""
#### Upload Excel File with Columns:
- `Operating Hour`
- `Temperature`
- `Vibration`
- `Pressure`
- `Component_Type`
""")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

@st.cache_data
def load_data(file):
    return pd.read_excel(file)

def line_chart(df, metric):
    fig, ax = plt.subplots(figsize=(7, 3))
    df["Operating Hour"] = pd.to_numeric(df["Operating Hour"], errors='coerce')
    for comp in df["Component_Type"].unique():
        comp_df = df[df["Component_Type"] == comp].copy()
        comp_df = comp_df.sort_values("Operating Hour")
        comp_df[f"{metric}_smooth"] = comp_df[metric].rolling(window=10, min_periods=1).mean()
        ax.plot(comp_df["Operating Hour"], comp_df[f"{metric}_smooth"], label=comp, linewidth=1.4)
    ax.set_title(f"{metric} vs Operating Hour", fontsize=12)
    ax.set_xlabel("Operating Hour")
    ax.set_ylabel(metric)
    ax.legend(fontsize=6)
    st.pyplot(fig)

def gauge(title, value, min_val, max_val, zones):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title, 'font': {'size': 12}},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "gray"},
            'steps': [{'range': zone[0], 'color': zone[1]} for zone in zones]
        }
    ))
    fig.update_layout(height=160, margin=dict(t=10, b=10, l=10, r=10))
    return fig

def donut(title, percent, color):
    fig = go.Figure(data=[go.Pie(values=[percent, 100 - percent], hole=0.65,
                                 marker_colors=[color, "#f0f0f0"],
                                 textinfo="none")])
    fig.update_layout(
        showlegend=False,
        annotations=[
            dict(text=f"{int(percent)}%", x=0.5, y=0.5, font_size=14, showarrow=False),
            dict(text=title, x=0.5, y=0.2, font_size=10, showarrow=False)
        ],
        height=160,
        width=160,
        margin=dict(t=10, b=10, l=10, r=10)
    )
    return fig

def component_zone(df):
    st.markdown("### 📉 Trends")
    c1, c2, c3 = st.columns(3)
    with c1:
        line_chart(df, "Temperature")
    with c2:
        line_chart(df, "Vibration")
    with c3:
        line_chart(df, "Pressure")

    st.markdown("### 📍 Gauges and Health")
    for comp in df['Component_Type'].unique():
        comp_df = df[df['Component_Type'] == comp].iloc[-1]
        st.markdown(f"#### {comp}")
        g1, g2, g3 = st.columns(3)
        with g1:
            st.plotly_chart(gauge("Temp", comp_df['Temperature'], 0, 150,
                                  [((0, 70), "green"), ((70, 100), "yellow"), ((100, 120), "orange"), ((120, 150), "red")]), use_container_width=True)
        with g2:
            st.plotly_chart(gauge("Vib", comp_df['Vibration'], 0, 2.5,
                                  [((0, 0.4), "green"), ((0.4, 1), "yellow"), ((1, 1.5), "orange"), ((1.5, 2.5), "red")]), use_container_width=True)
        with g3:
            st.plotly_chart(gauge("Pres", comp_df['Pressure'], 0, 400,
                                  [((0, 230), "red"), ((230, 260), "orange"), ((260, 290), "yellow"), ((290, 320), "lightgreen"), ((320, 400), "black")]), use_container_width=True)

        d1 = max(0, int((1 - comp_df['Temperature'] / 150) * 100))
        d2 = max(0, int((1 - comp_df['Vibration'] / 2.5) * 100))
        d3 = max(0, int((1 - (400 - comp_df['Pressure']) / 400) * 100))
        #
            [comp_df['Temperature'], comp_df['Vibration'], 400 - comp_df['Pressure']], [150, 2.5, 400])]
        dchart1, dchart2, dchart3 = donut("Temp", d1, "green"), donut("Vib", d2, "green"), donut("Pres", d3, "red")
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(dchart1, use_container_width=True)
        with c2: st.plotly_chart(dchart2, use_container_width=True)
        with c3: st.plotly_chart(dchart3, use_container_width=True)

if uploaded_file:
    df = load_data(uploaded_file)
    expected = {"Operating Hour", "Temperature", "Vibration", "Pressure", "Component_Type"}
    if not expected.issubset(set(df.columns)):
        st.error(f"Missing columns: {expected - set(df.columns)}")
    else:
        df = df.sort_values("Operating Hour")
        component_zone(df)

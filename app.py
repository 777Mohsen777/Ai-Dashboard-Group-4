
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(page_title="Equipment Sensor Dashboard", layout="wide")
st.title("Excavator Component Dashboard")

st.markdown("""
## Upload Excel File with These Column Headers (Any Order):
- `Operating Hour`
- `Temperature`
- `Vibration`
- `Pressure`
- `Component_Type`

Ensure the values are numeric and without units.
""")

uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

@st.cache_data
def load_data(file):
    return pd.read_excel(file)

def line_chart(df, metric):
    fig, ax = plt.subplots(figsize=(10, 4))
    df["Operating Hour"] = pd.to_numeric(df["Operating Hour"], errors='coerce')
    for comp in df["Component_Type"].unique():
        comp_df = df[df["Component_Type"] == comp].copy()
        comp_df = comp_df.sort_values("Operating Hour")
        comp_df[f"{metric}_smooth"] = comp_df[metric].rolling(window=10, min_periods=1).mean()
        ax.plot(comp_df["Operating Hour"], comp_df[f"{metric}_smooth"], label=comp, linewidth=1.6)
    ax.set_title(f"{metric} vs Operating Hour", fontsize=14)
    ax.set_xlabel("Operating Hour", fontsize=12)
    ax.set_ylabel(metric, fontsize=12)
    ax.legend()
    st.pyplot(fig)

def gauge(title, value, min_val, max_val, zones):
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

def donut(title, percent, color):
    fig = go.Figure(data=[go.Pie(values=[percent, 100 - percent], hole=0.7,
                                 marker_colors=[color, "#e0e0e0"], textinfo="none")])
    fig.update_layout(showlegend=False, annotations=[
        dict(text=f"{int(percent)}%", x=0.5, y=0.5, font_size=18, showarrow=False),
        dict(text=title, x=0.5, y=0.2, font_size=12, showarrow=False)
    ], height=200, width=200, margin=dict(t=10, b=10, l=10, r=10))
    return fig

def component_zone(df):
    for metric in ["Temperature", "Vibration", "Pressure"]:
        st.markdown(f"## {metric} Over Operating Hour")
        line_chart(df, metric)

    st.markdown("## Gauges per Component")
    for comp in df['Component_Type'].unique():
        comp_df = df[df['Component_Type'] == comp].iloc[-1]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.plotly_chart(gauge(f"{comp} Temp", comp_df['Temperature'], 0, 150, [((0,70),'lightgreen'),((70,100),'yellow'),((100,120),'orange'),((120,150),'red')]), use_container_width=True)
        with c2:
            st.plotly_chart(gauge(f"{comp} Vib", comp_df['Vibration'], 0, 2.5, [((0,0.4),'lightgreen'),((0.4,1),'yellow'),((1,1.5),'orange'),((1.5,2.5),'red')]), use_container_width=True)
        with c3:
            st.plotly_chart(gauge(f"{comp} Pres", comp_df['Pressure'], 0, 400, [((230,260),'red'),((260,290),'orange'),((290,320),'yellow'),((320,400),'lightgreen')]), use_container_width=True)

    st.markdown("## Health Donut Charts")
    for comp in df['Component_Type'].unique():
        comp_df = df[df['Component_Type'] == comp].iloc[-1]
        r1, r2, r3 = [int((1 - v/threshold)*100) for v, threshold in zip(
            [comp_df['Temperature'], comp_df['Vibration'], 400 - comp_df['Pressure']],
            [150, 2.5, 400])]
        d1, d2, d3 = donut(f"{comp} Temp", r1, 'green'), donut(f"{comp} Vib", r2, 'blue'), donut(f"{comp} Pres", r3, 'red')
        c1, c2, c3 = st.columns(3)
        with c1: st.plotly_chart(d1, use_container_width=True)
        with c2: st.plotly_chart(d2, use_container_width=True)
        with c3: st.plotly_chart(d3, use_container_width=True)

if uploaded_file:
    df = load_data(uploaded_file)
    expected = {"Operating Hour", "Temperature", "Vibration", "Pressure", "Component_Type"}
    if not expected.issubset(set(df.columns)):
        st.error(f"Missing columns: {expected - set(df.columns)}")
    else:
        df = df.sort_values("Operating Hour")
        component_zone(df)

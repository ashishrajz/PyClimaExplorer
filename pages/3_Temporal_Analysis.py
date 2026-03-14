import streamlit as st
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# ==========================================
# 🎨 UI UPGRADES: Dark Liquid Glass Theme
# ==========================================
st.set_page_config(page_title="Temporal Analysis", layout="wide")

custom_css = """
<style>
    /* Global App Background */
    .stApp {
        background: linear-gradient(135deg, #09090b 0%, #171717 100%);
        color: #e2e8f0;
    }

    /* Typography Colors */
    h1, h2, h3, h4, h5, h6, p, span, label, .st-emotion-cache-10trblm {
        color: #e2e8f0 !important;
    }

    /* Liquid Glass Effect for Metrics, Selectboxes, Inputs, and Download Button */
    [data-testid="stMetric"],
    .stSelectbox div[data-baseweb="select"],
    [data-testid="stDownloadButton"] > button,
    [data-testid="stAlert"] {
        background: rgba(34, 211, 238, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(34, 211, 238, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        transition: all 0.3s ease-in-out;
    }
    
    /* FIX 1: Properly center the Label and Value inside the Metric boxes */
    [data-testid="stMetric"] {
        padding: 15px 10px !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important; /* Centers cross-axis */
        justify-content: center !important; /* Centers main-axis */
    }
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        text-align: center !important;
    }

    /* Download Button Hover State */
    [data-testid="stDownloadButton"] > button:hover {
        background: rgba(34, 211, 238, 0.2) !important;
        box-shadow: 0 0 15px rgba(34, 211, 238, 0.4) !important;
        transform: translateY(-2px);
        border: 1px solid rgba(34, 211, 238, 0.8) !important;
    }

    /* FIX 2: Only target the slider thumb so numbers don't get ugly background boxes */
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #22d3ee !important;
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.8) !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.title("📈 Temporal Climate Analysis")

# -----------------------
# LOAD DATA
# -----------------------

ds = st.session_state.get("dataset")
variable = st.session_state.get("variable")

if ds is None:
    st.warning("Load a dataset first.")
    st.stop()

dims = dict(ds.sizes)

time_dim = [d for d in dims if "time" in d][0]
lat_dim = "latitude" if "latitude" in dims else "lat"
lon_dim = "longitude" if "longitude" in dims else "lon"

# -----------------------
# DEFAULT LOCATION
# -----------------------

lat_default = st.session_state.get("selected_lat")
lon_default = st.session_state.get("selected_lon")

if lat_default is None:
    lat_default = float(ds[lat_dim].values[len(ds[lat_dim])//2])

if lon_default is None:
    lon_default = float(ds[lon_dim].values[len(ds[lon_dim])//2])

# -----------------------
# LOCATION SELECTION
# -----------------------

st.subheader("Select Location")

col1, col2 = st.columns(2)

with col1:
    lat_value = st.slider(
        "Latitude",
        float(ds[lat_dim].min()),
        float(ds[lat_dim].max()),
        float(lat_default)
    )

with col2:
    lon_value = st.slider(
        "Longitude",
        float(ds[lon_dim].min()),
        float(ds[lon_dim].max()),
        float(lon_default)
    )

# -----------------------
# EXTRACT TIME SERIES
# -----------------------

point_series = ds[variable].sel(
    {lat_dim: lat_value, lon_dim: lon_value},
    method="nearest"
)

time_values = ds[time_dim].values

df = pd.DataFrame({
    "time": time_values,
    "value": point_series.values
})

# -----------------------
# ROLLING AVERAGE
# -----------------------

st.subheader("Trend Controls")

rolling_window = st.selectbox(
    "Rolling Average",
    [None, 3, 6, 12]
)

if rolling_window:

    df["rolling"] = df["value"].rolling(
        rolling_window,
        center=True
    ).mean()

# -----------------------
# GLOBAL MEAN
# -----------------------

global_mean = ds[variable].mean(dim=[lat_dim, lon_dim])

df["global_mean"] = global_mean.values

# -----------------------
# TIME SERIES PLOT
# -----------------------

fig = px.line(
    df,
    x="time",
    y="value",
    labels={"value": variable},
    title=f"{variable} trend at ({lat_value:.2f}, {lon_value:.2f})",
    template="plotly_dark"
)

if rolling_window:

    fig.add_scatter(
        x=df["time"],
        y=df["rolling"],
        name=f"{rolling_window}-step rolling average",
        line=dict(color="#22d3ee", width=2)
    )

fig.add_scatter(
    x=df["time"],
    y=df["global_mean"],
    name="Global mean",
    line=dict(color="rgba(255, 255, 255, 0.5)", dash="dot")
)

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=0, r=0, t=40, b=0)
)

fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# STATISTICS
# -----------------------

st.subheader("Statistics")

unit = "mm" if variable == "tp" else ""

mean_val = df["value"].mean()
max_val = df["value"].max()
min_val = df["value"].min()
std_val = df["value"].std()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Mean", f"{mean_val:.2f} {unit}")
col2.metric("Maximum", f"{max_val:.2f} {unit}")
col3.metric("Minimum", f"{min_val:.2f} {unit}")
col4.metric("Std Dev", f"{std_val:.2f} {unit}")

# -----------------------
# DOWNLOAD DATA
# -----------------------

st.subheader("Export Data")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Time Series",
    csv,
    "climate_timeseries.csv",
    "text/csv"
)
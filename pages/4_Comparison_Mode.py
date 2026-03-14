import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==========================================
# 🎨 UI UPGRADES: Dark Liquid Glass Theme
# ==========================================
st.set_page_config(page_title="Climate Comparison", layout="wide")

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

    /* Liquid Glass Effect for Selectboxes and Alerts */
    .stSelectbox div[data-baseweb="select"],
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

    /* Sliders styling - safely targeting ONLY the thumb */
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #22d3ee !important;
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.8) !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.title("🔬 Climate Comparison Mode")

# -------------------------
# LOAD DATA
# -------------------------

ds = st.session_state.get("dataset")
variable = st.session_state.get("variable")

if ds is None:
    st.warning("Load dataset first.")
    st.stop()

dims = dict(ds.sizes)

time_dim = [d for d in dims if "time" in d][0]
lat_dim = "latitude" if "latitude" in dims else "lat"
lon_dim = "longitude" if "longitude" in dims else "lon"

time_values = ds[time_dim].values

# -------------------------
# MODE SELECTOR
# -------------------------

mode = st.selectbox(
    "Select Analysis Mode",
    [
        "Time Comparison",
        "Location Comparison",
        "Difference Map",
        "Location Correlation",
        "Climate Anomaly Map",
        "Regional Average Analysis"
    ]
)

# =====================================================
# 1 TIME COMPARISON
# =====================================================

if mode == "Time Comparison":

    st.subheader("Compare Two Time Periods")

    lat = st.slider("Latitude",
                    float(ds[lat_dim].min()),
                    float(ds[lat_dim].max()),
                    0.0)

    lon = st.slider("Longitude",
                    float(ds[lon_dim].min()),
                    float(ds[lon_dim].max()),
                    0.0)

    t1 = st.selectbox("Time 1", time_values)
    t2 = st.selectbox("Time 2", time_values, index=1 if len(time_values) > 1 else 0)

    v1 = ds[variable].sel({lat_dim: lat, lon_dim: lon, time_dim: t1}, method="nearest")
    v2 = ds[variable].sel({lat_dim: lat, lon_dim: lon, time_dim: t2}, method="nearest")

    df = pd.DataFrame({
        "Period": ["Time 1", "Time 2"],
        "Value": [float(v1.values), float(v2.values)]
    })

    fig = px.bar(df, x="Period", y="Value", template="plotly_dark", color_discrete_sequence=["#22d3ee"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 2 LOCATION COMPARISON
# =====================================================

if mode == "Location Comparison":

    st.subheader("Compare Two Locations")

    t = st.selectbox("Select Time", time_values)

    col1, col2 = st.columns(2)

    with col1:
        lat1 = st.slider("Lat 1", float(ds[lat_dim].min()), float(ds[lat_dim].max()), 0.0)
        lon1 = st.slider("Lon 1", float(ds[lon_dim].min()), float(ds[lon_dim].max()), 0.0)

    with col2:
        lat2 = st.slider(
    "Lat 2",
    float(ds[lat_dim].min()),
    float(ds[lat_dim].max()),
    float(ds[lat_dim].max()) * 0.3
)

        lon2 = st.slider(
    "Lon 2",
    float(ds[lon_dim].min()),
    float(ds[lon_dim].max()),
    float(ds[lon_dim].max()) * 0.3
)

    v1 = ds[variable].sel({lat_dim: lat1, lon_dim: lon1, time_dim: t}, method="nearest")
    v2 = ds[variable].sel({lat_dim: lat2, lon_dim: lon2, time_dim: t}, method="nearest")

    df = pd.DataFrame({
        "Location": ["Location 1", "Location 2"],
        "Value": [float(v1.values), float(v2.values)]
    })

    fig = px.bar(df, x="Location", y="Value", template="plotly_dark", color_discrete_sequence=["#22d3ee"])
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 3 DIFFERENCE MAP
# =====================================================

if mode == "Difference Map":

    st.subheader("Spatial Difference Map")

    t1 = st.selectbox("Time 1", time_values)
    t2 = st.selectbox("Time 2", time_values, index=1 if len(time_values) > 1 else 0)

    map1 = ds[variable].sel({time_dim: t1})
    map2 = ds[variable].sel({time_dim: t2})

    diff = map2 - map1

    diff = diff.coarsen({lat_dim:4, lon_dim:4}, boundary="trim").mean()

    lat = diff[lat_dim].values
    lon = diff[lon_dim].values

    fig = px.imshow(
        diff.values,
        x=lon,
        y=lat,
        origin="lower",
        color_continuous_scale="RdBu_r",
        template="plotly_dark",
        title="Difference Map"
    )

    # Replaced hardcoded #0e1117 with transparent glass background
    fig.update_layout(
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 4 LOCATION CORRELATION
# =====================================================

if mode == "Location Correlation":

    st.subheader("Compare Climate Trends Between Two Locations")

    col1, col2 = st.columns(2)

    with col1:
        lat1 = st.slider("Latitude A", float(ds[lat_dim].min()), float(ds[lat_dim].max()), 0.0)
        lon1 = st.slider("Longitude A", float(ds[lon_dim].min()), float(ds[lon_dim].max()), 0.0)

    with col2:
        lat2 = st.slider(
    "Latitude B",
    float(ds[lat_dim].min()),
    float(ds[lat_dim].max()),
    float(ds[lat_dim].max()) * 0.25
)

        lon2 = st.slider(
    "Longitude B",
    float(ds[lon_dim].min()),
    float(ds[lon_dim].max()),
    float(ds[lon_dim].max()) * 0.25
)
    series1 = ds[variable].sel({lat_dim: lat1, lon_dim: lon1}, method="nearest")
    series2 = ds[variable].sel({lat_dim: lat2, lon_dim: lon2}, method="nearest")

    df = pd.DataFrame({
        "time": time_values,
        "Location A": series1.values,
        "Location B": series2.values
    })

    fig = px.line(
        df,
        x="time",
        y=["Location A", "Location B"],
        template="plotly_dark",
        title="Climate Trend Comparison",
        color_discrete_sequence=["#22d3ee", "rgba(255,255,255,0.6)"] # Match theme
    )

    fig.update_traces(line=dict(width=3))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 5 CLIMATE ANOMALY MAP
# =====================================================

if mode == "Climate Anomaly Map":

    st.subheader("Climate Anomaly")

    t = st.selectbox("Select Time", time_values)

    climatology = ds[variable].mean(dim=time_dim)

    current = ds[variable].sel({time_dim: t})

    anomaly = current - climatology

    anomaly = anomaly.coarsen({lat_dim:4, lon_dim:4}, boundary="trim").mean()

    fig = px.imshow(
        anomaly.values,
        x=anomaly[lon_dim],
        y=anomaly[lat_dim],
        origin="lower",
        color_continuous_scale="RdBu_r",
        template="plotly_dark",
        title="Climate Anomaly"
    )

    fig.update_layout(height=600, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# 6 REGIONAL AVERAGE
# =====================================================

if mode == "Regional Average Analysis":

    st.subheader("Regional Climate Average")

    lat_min = st.slider("Min Latitude", float(ds[lat_dim].min()), float(ds[lat_dim].max()), -10.0)
    lat_max = st.slider("Max Latitude", float(ds[lat_dim].min()), float(ds[lat_dim].max()), 10.0)

    lon_min = st.slider("Min Longitude", float(ds[lon_dim].min()), float(ds[lon_dim].max()), -10.0)
    lon_max = st.slider("Max Longitude", float(ds[lon_dim].min()), float(ds[lon_dim].max()), 10.0)

    # ensure correct order
    lat1, lat2 = sorted([lat_min, lat_max])
    lon1, lon2 = sorted([lon_min, lon_max])

    # handle reversed latitude datasets
    lat_values = ds[lat_dim].values
    if lat_values[0] > lat_values[-1]:
        lat_slice = slice(lat2, lat1)
    else:
        lat_slice = slice(lat1, lat2)

    lon_slice = slice(lon1, lon2)

    region = ds[variable].sel(
        {lat_dim: lat_slice, lon_dim: lon_slice}
    )

    # compute mean
    regional_mean = region.mean(dim=[lat_dim, lon_dim], skipna=True)

    # convert to dataframe
    df = regional_mean.to_dataframe(name="regional_mean").reset_index()

    # drop NaN values
    df = df.dropna()

    if df.empty:
        st.error("Selected region contains no valid data. Try a larger area.")
        st.stop()

    fig = px.line(
        df,
        x=time_dim,
        y="regional_mean",
        template="plotly_dark",
        title="Regional Climate Trend"
    )

    # Updated line color from orange to theme cyan
    fig.update_traces(line=dict(color="#22d3ee", width=3))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(255,255,255,0.1)")

    st.plotly_chart(fig, use_container_width=True)
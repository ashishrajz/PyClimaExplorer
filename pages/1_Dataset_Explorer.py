import streamlit as st
import xarray as xr
import plotly.express as px
from utils.load_data import load_dataset
import plotly.graph_objects as go
import numpy as np
import io

# ==========================================
# 🎨 UI UPGRADES: Dark Liquid Glass Theme
# ==========================================
st.set_page_config(page_title="Climate Explorer", layout="wide")

# Injecting Custom CSS for Glassmorphism
custom_css = """
<style>
    /* Global App Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
        color: #ffffff;
    }

    /* Liquid Glass Effect for Inputs, Metrics, and Buttons */
    [data-testid="stMetric"], 
    [data-testid="stFileUploader"], 
    .stSelectbox div[data-baseweb="select"],
    div.stButton > button,
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

    /* FIX: Properly center the Label and Value inside the Metric boxes */
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

    /* Hover effects to make the UI feel interactive */
    div.stButton > button:hover {
        background: rgba(34, 211, 238, 0.2) !important;
        box-shadow: 0 0 15px rgba(34, 211, 238, 0.4) !important;
        transform: translateY(-2px);
        border: 1px solid rgba(34, 211, 238, 0.8) !important;
    }

    /* Override Streamlit Typography Colors for Dark Theme */
    h1, h2, h3, h4, h5, h6, p, span, label, .st-emotion-cache-10trblm {
        color: #e2e8f0 !important;
    }

    /* Divider Styling */
    hr {
        border-bottom: 1px solid rgba(34, 211, 238, 0.4) !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.title("📂 Climate Dataset Explorer")

# DATASET TYPE
dataset_type = st.selectbox(
    "Select Dataset Resolution",
    ["Monthly", "Weekly", "Daily", "Hourly", "Upload Custom Dataset"]
)

# VARIABLE TYPE
variable_type = None

if dataset_type != "Upload Custom Dataset":
    variable_type = st.selectbox(
        "Select Climate Variable",
        ["Temperature", "Precipitation", "Wind"]
    )

# DATASET PATH MAPPING
dataset_paths = {
    ("Monthly", "Temperature"): "data/monthly_temperature.nc",
    ("Monthly", "Precipitation"): "data/monthly_precipitation.nc",
    ("Monthly", "Wind"): "data/monthly_wind.nc",
    ("Weekly", "Temperature"): "data/weekly_temperature.nc",
    ("Weekly", "Precipitation"): "data/weekly_precipitation.nc",
    ("Weekly", "Wind"): [
        "data/weekly_wind_u.nc",
        "data/weekly_wind_v.nc"
    ],
    ("Daily", "Temperature"): "data/daily_temperature.nc",
    ("Daily", "Precipitation"): "data/daily_precipitation.nc",
    ("Daily", "Wind"): [
        "data/daily_wind_u.nc",
        "data/daily_wind_v.nc"
    ],
    ("Hourly", "Temperature"): "data/hourly_temperature.nc",
    ("Hourly", "Precipitation"): "data/hourly_precipitation.nc",
    ("Hourly", "Wind"): "data/hourly_wind.nc"
}

# LOAD DATASET
if dataset_type != "Upload Custom Dataset":
    path = dataset_paths[(dataset_type, variable_type)]
    ds = load_dataset(path)
else:
    uploaded_file = st.file_uploader(
        "Upload Climate Dataset",
        type=["nc", "grib"]
    )

    if uploaded_file is not None:
        file_bytes = io.BytesIO(uploaded_file.read())
        try:
            ds = xr.open_dataset(file_bytes)
        except:
            ds = xr.open_dataset(file_bytes, engine="cfgrib")
    else:
        st.stop()

st.success("Dataset loaded successfully")
st.write("Variables in dataset:", list(ds.data_vars))

# Save globally for other pages
st.session_state["dataset"] = ds

# Detect dimensions
dims = dict(ds.sizes)

time_dim = None
for d in dims:
    if "time" in d:
        time_dim = d

lat_dim = "latitude" if "latitude" in ds.coords else "lat"
lon_dim = "longitude" if "longitude" in ds.coords else "lon"

st.subheader("Dataset Overview")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Time Steps", dims.get(time_dim))

with col2:
    st.metric("Latitude Points", "90")

with col3:
    st.metric("Longitude Points", "360")

# VARIABLES
variables = list(ds.data_vars)

selected_variable = st.selectbox(
    "Select Variable to Explore",
    variables
)

st.session_state["variable"] = selected_variable

# PREVIEW MAP
st.subheader("Dataset Preview")

map_data = ds[selected_variable].isel({time_dim: 0})

lat = map_data[lat_dim].values
lon = map_data[lon_dim].values

fig = px.imshow(
    map_data.values,
    x=lon,
    y=lat,
    origin="lower",
    color_continuous_scale="RdBu_r"
)

# UI FIX: Make Plotly background transparent to match the glass theme
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e2e8f0"),
    margin=dict(l=0, r=0, t=30, b=0)
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

if st.button("Explore Global Map"):
    st.switch_page("pages/2_Spatial_Map.py")
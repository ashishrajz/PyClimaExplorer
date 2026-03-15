import streamlit as st
import time
from streamlit_plotly_events import plotly_events
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# ==========================================
# 🎨 UI UPGRADES: Dark Liquid Glass Theme
# ==========================================
st.set_page_config(page_title="Global Climate Map", layout="wide")

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

    /* Liquid Glass Effect for Buttons, Alerts, and Containers */
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

    /* Button Hover States */
    div.stButton > button:hover {
        background: rgba(34, 211, 238, 0.2) !important;
        box-shadow: 0 0 15px rgba(34, 211, 238, 0.4) !important;
        transform: translateY(-2px);
        border: 1px solid rgba(34, 211, 238, 0.8) !important;
    }

    /* Style the Radio Button Group (2D/3D Selector) */
    [data-testid="stRadio"] > div[role="radiogroup"] {
        background: rgba(34, 211, 238, 0.05) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(34, 211, 238, 0.4) !important;
        border-radius: 12px !important;
        padding: 10px 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
        justify-content: center; /* Centers the options inside the glass container */
    }

    /* Emphasize the text of the radio options */
    [data-testid="stRadio"] label p {
        font-weight: 600 !important;
        color: #e2e8f0 !important;
        margin-right: 15px; /* Adds breathing room between the 2D and 3D options */
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
# ==========================================

st.title("🌍 Global Climate Map")

# Use columns to force the selector into the center of the page
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_center:
    view_selection = st.radio(
        "Select View Mode",
        options=["2D Map", "3D Globe"],
        horizontal=True,
        label_visibility="collapsed" # Hides the label so only the glass box shows
    )

# Map the selection back to the original boolean so the rest of your code works perfectly
view_mode = True if view_selection == "3D Globe" else False

# -----------------------
# LOAD DATA
# -----------------------

from utils.load_data import load_dataset

variable = st.session_state.get("variable")

# Reload dataset safely
if "dataset_path" in st.session_state:
    ds = load_dataset(st.session_state["dataset_path"])
elif "uploaded_dataset" in st.session_state:
    ds = st.session_state["uploaded_dataset"]
else:
    st.warning("Load dataset from Dataset Explorer first.")
    st.stop()


if ds is None:
    st.warning("Load dataset from Dataset Explorer first.")
    st.stop()

dims = dict(ds.sizes)

time_dim = [d for d in dims if "time" in d][0]
lat_dim = "latitude" if "latitude" in dims else "lat"
lon_dim = "longitude" if "longitude" in dims else "lon"

time_values = ds[time_dim].values

# -----------------------
# SESSION STATE
# -----------------------

if "time_index" not in st.session_state:
    st.session_state.time_index = 0

if "playing" not in st.session_state:
    st.session_state.playing = False

if "selected_lat" not in st.session_state:
    st.session_state.selected_lat = None

if "selected_lon" not in st.session_state:
    st.session_state.selected_lon = None

# -----------------------
# CONTROLS
# -----------------------

col1, col2, col3 = st.columns([6,1,1])

with col1:
    selected_time = st.select_slider(
        "Time",
        options=time_values,
        value=time_values[st.session_state.time_index],
        format_func=lambda x: str(x)[:10]
    )

    st.session_state.time_index = list(time_values).index(selected_time)

with col2:
    if st.button("▶ Play"):
        st.session_state.playing = True

with col3:
    if st.button("⏹ Stop"):
        st.session_state.playing = False

selected_time = time_values[st.session_state.time_index]

# rotation for globe animation
rotation_speed = 3
rotation_lon = st.session_state.time_index * rotation_speed

# -----------------------
# MAP DATA
# -----------------------

map_data = ds[variable].isel({time_dim: st.session_state.time_index})

map_data = map_data.coarsen(
    {lat_dim:4, lon_dim:4},
    boundary="trim"
).mean()

lat = map_data[lat_dim].values
lon = map_data[lon_dim].values

# ===============================
# 2D MAP (UNCHANGED FUNCTIONALITY)
# ===============================

selected_points = None
click_data = None

if not view_mode:

    fig = px.imshow(
        map_data.values,
        x=lon,
        y=lat,
        origin="lower",
        color_continuous_scale="RdBu_r",
        template="plotly_dark",
        title=f"{variable} at {str(selected_time)[:10]}"
    )

    # UI UPGRADE: Set background to transparent to inherit the glass theme
    fig.update_layout(
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    fig.add_shape(
        type="rect",
        x0=min(lon),
        x1=max(lon),
        y0=min(lat),
        y1=max(lat),
        line=dict(color="rgba(34, 211, 238, 0.4)", width=1), # Matched line color to theme
    )

    selected_points = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        override_height=600,
        key="map"
    )

# ===============================
# 3D GLOBE (UNCHANGED FUNCTIONALITY)
# ===============================

else:

    lat_grid, lon_grid = np.meshgrid(lat, lon)

    df = pd.DataFrame({
        "lat": lat_grid.flatten(),
        "lon": lon_grid.flatten(),
        "value": map_data.values.flatten()
    })

    fig = go.Figure()

    fig.add_trace(
        go.Scattergeo(
            lon=df["lon"],
            lat=df["lat"],
            mode="markers",
            marker=dict(
                size=4,
                color=df["value"],
                colorscale="RdBu_r",
                opacity=0.9,
                colorbar=dict(title=variable)
            )
        )
    )

    # UI UPGRADE: Set background to transparent
    fig.update_layout(
        title=f"3D Globe — {variable}",
        template="plotly_dark",
        height=800,
        margin=dict(l=0,r=0,t=40,b=0),
        geo=dict(
            projection_type="orthographic",
            projection_scale=0.85,
            showland=True,
            landcolor="rgb(50,50,50)",
            showocean=True,
            oceancolor="rgba(10,10,25,0.5)", # Made ocean slightly transparent
            showcountries=True,
            showcoastlines=True,
            coastlinecolor="rgba(34, 211, 238, 0.4)", # Coastlines match the theme
            bgcolor="rgba(0,0,0,0)" # Transparent background for the globe
        )
    )

    fig.update_geos(
        projection_rotation=dict(lon=rotation_lon)
    )

    click_data = plotly_events(
        fig,
        click_event=True,
        hover_event=False,
        override_height=800,
        key="globe"
    )

# -----------------------
# CLICK LOCATION (3D)
# -----------------------

if view_mode and click_data:

    point = click_data[0]
    idx = point["pointIndex"]

    lat_clicked = df.iloc[idx]["lat"]
    lon_clicked = df.iloc[idx]["lon"]

    st.session_state.selected_lat = float(lat_clicked)
    st.session_state.selected_lon = float(lon_clicked)

# -----------------------
# CLICK LOCATION (2D)
# -----------------------

if selected_points:

    point = selected_points[0]

    lat_clicked = lat[int(point["y"])]
    lon_clicked = lon[int(point["x"])]

    st.session_state.selected_lat = float(lat_clicked)
    st.session_state.selected_lon = float(lon_clicked)

# -----------------------
# LOCATION OUTPUT
# -----------------------

if st.session_state.selected_lat is not None:

    st.success(
        f"Selected location → Lat {st.session_state.selected_lat:.2f}, Lon {st.session_state.selected_lon:.2f}"
    )

    if st.button("Analyze This Location"):
        st.switch_page("pages/3_Temporal_Analysis.py")

# -----------------------
# ANIMATION
# -----------------------

if st.session_state.playing:

    next_index = st.session_state.time_index + 1

    if next_index >= len(time_values):
        next_index = 0

    time.sleep(0.35)

    st.session_state.time_index = next_index
    st.rerun()
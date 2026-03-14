import xarray as xr
import streamlit as st

@st.cache_data
def load_dataset(path):

    # If multiple files (daily wind)
    if isinstance(path, list):
        ds = xr.merge([xr.open_dataset(p) for p in path])
    else:
        ds = xr.open_dataset(path)

    # Convert temperature if present
    if "t2m" in ds:
        ds["t2m"] = ds["t2m"] - 273.15

    # Create wind speed if wind components exist
    if "u10" in ds and "v10" in ds:
        ds["wind_speed"] = (ds["u10"]**2 + ds["v10"]**2) ** 0.5

    return ds
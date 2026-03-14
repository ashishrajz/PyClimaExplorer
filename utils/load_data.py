import xarray as xr
import streamlit as st
import os


@st.cache_data
def load_dataset(path):

    # Resolve absolute path (works on Streamlit Cloud)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    if isinstance(path, list):
        files = [os.path.join(BASE_DIR, p) for p in path]
        ds = xr.merge([xr.open_dataset(f) for f in files])
    else:
        file_path = os.path.join(BASE_DIR, path)
        ds = xr.open_dataset(file_path)

    # Convert temperature
    if "t2m" in ds:
        ds["t2m"] = ds["t2m"] - 273.15

    # Wind speed
    if "u10" in ds and "v10" in ds:
        ds["wind_speed"] = (ds["u10"]**2 + ds["v10"]**2) ** 0.5

    return ds

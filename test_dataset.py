import xarray as xr

ds = xr.open_dataset("data/climate_data.nc", engine="cfgrib")

print(ds)
import numpy as np
import xarray as xr

long_short_name_dict = {
    "2m_temperature": "t2m",
    "snow_depth": "sd",
    "snowfall": "sf",
    "snowmelt": "smlt",
    "surface_pressure": "sp",
    "sea_surface_temperature": "sst",
    "temperature_of_snow_layer": "tsn",
    "total_precipitation": "tp",
    "ice_temperature_layer_1": "istl1",
    "ice_temperature_layer_2": "istl2",
    "ice_temperature_layer_3": "istl3",
    "ice_temperature_layer_4": "istl4",
}

NO_AGG_LIT = "none"

ds_raw = xr.Dataset()
ds_raw["latitude"] = np.arange(-90, 90.1, 0.25)
ds_raw["longitude"] = np.arange(-180, 180.1, 0.25)
ds_05 = ds_raw.coarsen(latitude=2, longitude=2, boundary="trim").max()
ds_10 = ds_raw.coarsen(latitude=4, longitude=4, boundary="trim").max()


def get_lat_lon_range(spatial_resolution):
    if spatial_resolution == 0.25:
        lat_range = ds_raw.latitude.values
        lon_range = ds_raw.longitude.values
    elif spatial_resolution == 0.5:
        lat_range = ds_05.latitude.values
        lon_range = ds_05.longitude.values
    elif spatial_resolution == 1.0:
        lat_range = ds_10.latitude.values
        lon_range = ds_10.longitude.values
    else:
        raise ValueError("Invalid spatial_resolution")
    return lat_range, lon_range, lat_range[::-1]


def time_resolution_to_freq(time_resolution):
    if time_resolution == "hour":
        return "h"
    elif time_resolution == "day":
        return "D"
    elif time_resolution == "month":
        return "ME"
    elif time_resolution == "year":
        return "YE"
    else:
        raise ValueError("Invalid time_resolution")

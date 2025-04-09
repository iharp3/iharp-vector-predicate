import numpy as np
import pandas as pd
import xarray as xr

from .utils.const import get_lat_lon_range, time_resolution_to_freq


def gen_empty_xarray(
    min_lat,
    max_lat,
    min_lon,
    max_lon,
    start_datetime,
    end_datetime,
    temporal_resolution,
    spatial_resolution,
):
    lat_range, lon_range, lat_range_reverse = get_lat_lon_range(spatial_resolution)
    lat_start = lat_range.searchsorted(min_lat, side="left")
    lat_end = lat_range.searchsorted(max_lat, side="right")
    lat_reverse_start = len(lat_range) - lat_end
    lat_reverse_end = len(lat_range) - lat_start
    lon_start = lon_range.searchsorted(min_lon, side="left")
    lon_end = lon_range.searchsorted(max_lon, side="right")
    ds_empty = xr.Dataset()
    ds_empty["time"] = pd.date_range(
        start=start_datetime,
        end=end_datetime,
        freq=time_resolution_to_freq(temporal_resolution),
    )
    ds_empty["latitude"] = lat_range_reverse[lat_reverse_start:lat_reverse_end]
    ds_empty["longitude"] = lon_range[lon_start:lon_end]
    return ds_empty


class Metadata:
    def __init__(self, f_path):
        self.f_path = f_path
        self.df_meta = pd.read_csv(f_path)

    @staticmethod
    def _gen_xarray_for_meta_row(row, overwrite_temporal_resolution=None):
        if overwrite_temporal_resolution is not None:
            t_resolution = overwrite_temporal_resolution
        else:
            t_resolution = row.temporal_resolution
        return gen_empty_xarray(
            row.min_lat,
            row.max_lat,
            row.min_lon,
            row.max_lon,
            row.start_datetime,
            row.end_datetime,
            t_resolution,
            row.spatial_resolution,
        )

    @staticmethod
    def _mask_query_with_meta(ds_query, ds_meta):
        return (
            ds_query["time"].isin(ds_meta["time"])
            & ds_query["latitude"].isin(ds_meta["latitude"])
            & ds_query["longitude"].isin(ds_meta["longitude"])
        )

    def query_get_overlap_and_leftover(
        self,
        variable,
        start_datetime,
        end_datetime,
        min_lat,
        max_lat,
        min_lon,
        max_lon,
        temporal_resolution,
        spatial_resolution,
        aggregation,
    ):
        df_overlap = self.df_meta[
            (self.df_meta["variable"] == variable)
            & (self.df_meta["min_lat"] <= max_lat)
            & (self.df_meta["max_lat"] >= min_lat)
            & (self.df_meta["min_lon"] <= max_lon)
            & (self.df_meta["max_lon"] >= min_lon)
            & (pd.to_datetime(self.df_meta["start_datetime"]) <= pd.to_datetime(end_datetime))
            & (pd.to_datetime(self.df_meta["end_datetime"]) >= pd.to_datetime(start_datetime))
            & (self.df_meta["temporal_resolution"] == temporal_resolution)
            & (self.df_meta["spatial_resolution"] == spatial_resolution)
            & (self.df_meta["aggregation"] == aggregation)
        ]

        ds_query = gen_empty_xarray(
            min_lat,
            max_lat,
            min_lon,
            max_lon,
            start_datetime,
            end_datetime,
            temporal_resolution,
            spatial_resolution,
        )

        false_mask = xr.DataArray(
            data=np.zeros(
                (
                    ds_query.sizes["time"],
                    ds_query.sizes["latitude"],
                    ds_query.sizes["longitude"],
                ),
                dtype=bool,
            ),
            coords={
                "time": ds_query["time"],
                "latitude": ds_query["latitude"],
                "longitude": ds_query["longitude"],
            },
            dims=["time", "latitude", "longitude"],
        )

        for row in df_overlap.itertuples():
            ds_meta = self._gen_xarray_for_meta_row(row)
            mask = self._mask_query_with_meta(ds_query, ds_meta)
            false_mask = false_mask | mask

        leftover = false_mask.where(false_mask == False, drop=True)
        if leftover.values.size > 0:
            return df_overlap, leftover
        else:
            return df_overlap, None

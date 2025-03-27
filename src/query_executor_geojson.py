from datetime import datetime
import math
import cdsapi
import pandas as pd
import xarray as xr
import geojson
import pprint as pp

from query_executor import QueryExecutor
# from utils.const import time_resolution_to_freq
# from query_executor_get_raster import GetRasterExecutor

class GeoJsonExecutor(QueryExecutor):
    def __init__(
        self,
        variable: str,
        start_datetime: str,
        end_datetime: str,
        min_lat: float,
        max_lat: float, 
        min_lon: float,
        max_lon: float,
        temporal_resolution: str,
        spatial_resolution: float,
        aggregation: str,
        geojson_file: str,
    ):
        super().__init__(
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
            geojson_file,
        )
        self.geojson_file = geojson_file

    def _load_geojson(self):
        with open(self.geojson_file, 'r') as file:
            geojson_data = geojson.load(file)
        #pp.pprint((geojson_data))
        return geojson_data

    def execute(self):
        geojson_data = self._load_geojson()
        return geojson_data
        
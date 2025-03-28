from datetime import datetime
import math
import cdsapi
import pandas as pd
import xarray as xr
import geojson
import pprint as pp
import shapley.geometry

from query_executor import QueryExecutor
from utils.const import time_resolution_to_freq
from query_executor_get_raster import GetRasterExecutor

class GeoJsonExecutor(QueryExecutor):
    def __init__(
        self,
        variable: str,
        start_datetime: str,
        end_datetime: str,
        temporal_resolution: str,
        spatial_resolution: float,
        aggregation: str,
        geojson_file: str,
        min_lat: float = None,
        max_lat: float = None,
        min_lon: float = None,
        max_lon: float = None,
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
        )
        self.geojson_file = geojson_file

    def _load_geojson(self):
        with open(self.geojson_file, 'r') as file:
            geojson_data = geojson.load(file)
        #pp.pprint((geojson_data))
        return geojson_data

    def _extract_coordinates(self, geojson_data):
        coords = []
        coords.extend(geojson_data["coordinates"])
        return coords
    
    def _create_boudning_box(self, coordinates):
        longs = []
        lats = []
        for coord in coordinates:
            longs.append(coord[0])
            lats.append(coord[1])
        return min(longs), min(lats), max(longs), max(lats)
    
    # def _mask_raster_data(self, raster):
    #     longs = raster["longitude"]
    #     lats = raster["latitude"]
    
    def execute(self):
        geojson_data = self._load_geojson()
        geometry = geojson_data["features"][0]["geometry"]
        coords = self._extract_coordinates(geometry)
        min_lon, min_lat, max_lon, max_lat = self._create_boudning_box(coords[0])
        print(self.aggregation)
        raster = GetRasterExecutor(
            variable=self.variable,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            temporal_resolution=self.temporal_resolution,
            spatial_resolution=self.spatial_resolution,
            aggregation=self.aggregation
        )
        return raster.execute()
        
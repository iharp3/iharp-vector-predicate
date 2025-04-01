from datetime import datetime
import math
import cdsapi
import pandas as pd
import xarray as xr
import geopandas as gpd
import geojson
import pprint as pp
import numpy as np
import shapely.geometry
from shapely.vectorized import contains
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPolygon

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
        with open(self.geojson_file, 'r') as file:
            gdf = gpd.read_file(file)

        #pp.pprint((geojson_data))
        return geojson_data, gdf

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
    
    def _mask_raster_data(self, raster, polygon):
        lons = raster["longitude"].values
        lats = raster["latitude"].values
        mesh_lons, mesh_lats = np.meshgrid(lons, lats) # maybe add indexing='ij'
        # points = []
        # for lon,lat in zip(mesh_lons, mesh_lats):
        #     points.append(shapely.geometry.Point(lon, lat))
        points = np.vstack((mesh_lons.ravel(), mesh_lats.ravel())).T

        # mask = []
        # for lon, lat in points:
        #     point = shapely.geometry.Point(lon, lat)
        #     in_polygon = polygon.contains(point)
        #     mask.append(in_polygon)

        mask = contains(polygon, points[:, 0], points[:, 1])
        
        mask = np.array(mask)
        mask = mask.reshape(mesh_lons.shape)
        masked_data = raster.where(mask, other=np.nan)
        #raster["t2m"] = raster["t2m"].where(mask, other=np.nan)
        return masked_data
    
    def visualize_mask(self, raster, masked_raster, polygon):

        fig, axs = plt.subplots(1, 3, figsize=(18, 6))

        plt1 = axs[0].pcolormesh(raster.longitude, raster.latitude, raster.t2m.isel(valid_time=0))
        axs[0].set_title("Original Raster Data")
        fig.colorbar(plt1, ax=axs[0])

        masked_raster = self._mask_raster_data(raster, polygon)
        plt2 = axs[1].pcolormesh(masked_raster.longitude, masked_raster.latitude, masked_raster.t2m.isel(valid_time=0), cmap="binary") 
        axs[1].set_title("Mask")
        fig.colorbar(plt2, ax=axs[1])

        plt3 = axs[2].pcolormesh(masked_raster.longitude, masked_raster.latitude, masked_raster.t2m.isel(valid_time=0))
        axs[2].set_title("Masked Data")
        fig.colorbar(plt3, ax=axs[2])

        for ax in axs:
            x, y = polygon.exterior.xy
            ax.plot(x, y, color="red")
        plt.tight_layout()
        plt.savefig("data_plot.png")
        plt.show()
        plt.close()
    
    def execute(self):
        geojson_data, gdf = self._load_geojson()
        polygon = gdf.geometry.iloc[0]
        geometry = geojson_data["features"][0]["geometry"]
        coords = self._extract_coordinates(geometry)
        min_lon, min_lat, max_lon, max_lat = self._create_boudning_box(coords[0])
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
        
        masked_data = self._mask_raster_data(raster.execute(), polygon)
        print(masked_data)
        self.visualize_mask(raster.execute(), masked_data, polygon)
        print(raster)
        print(masked_data)
        if raster == masked_data:
            print("Mask Failed")
        else:
            print("Mask Succeeded")
        return masked_data
        
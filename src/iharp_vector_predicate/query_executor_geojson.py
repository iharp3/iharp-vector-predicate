from datetime import datetime
import pandas as pd
import xarray as xr
import geopandas as gpd
import numpy as np
from shapely.vectorized import contains
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PlotPolygon

from .query_executor import QueryExecutor
from .utils.const import time_resolution_to_freq
from .query_executor_get_raster import GetRasterExecutor

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
            gdf = gpd.read_file(file)
        return gdf

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
        points = np.vstack((mesh_lons.ravel(), mesh_lats.ravel())).T

        # mask = []
        # for lon, lat in points:
        #     point = shapely.geometry.Point(lon, lat)
        #     in_polygon = polygon.contains(point)
        #     mask.append(in_polygon)

        mask = contains(polygon, points[:, 0], points[:, 1])
        
        mask = np.array(mask)
        
        mask = mask.reshape(mesh_lons.shape)
        mask_da = xr.DataArray(mask, dims=["latitude", "longitude"], coords={"latitude": lats, "longitude": lons})

        masked_data = raster.where(mask_da, drop=False)
        # print(f'raster count: {raster.count()}')
        # print(raster.isel(valid_time=slice(0, 5)))
        # print(f'masked Data: {masked_data.count()}')
        # # original_valid = np.sum(~np.isnan(raster.t2m.values))
        # # masked_valid = np.sum(~np.isnan(masked_data.t2m.values))
        # # print(f"Original valid points: {original_valid}")
        # # print(f"Masked valid points: {masked_valid}")
        # #raster["t2m"] = raster["t2m"].where(mask, other=np.nan)
        return masked_data
    
    def _visualize_mask(self, raster, masked_raster, polygon):

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
        gdf = self._load_geojson()
        polygon = gdf.geometry.iloc[0]
        min_lon, min_lat, max_lon, max_lat = polygon.bounds
        # print(f"Longitude range: {min_lon} to {max_lon}")
        # print(f"Latitude range: {min_lat} to {max_lat}")
        # geometry = geojson_data["features"][0]["geometry"]
        # coords = self._extract_coordinates(geometry)
        # min_lon, min_lat, max_lon, max_lat = self._create_boudning_box(coords[0])
        print(f"Longitude range: {min_lon} to {max_lon}")
        print(f"Latitude range: {min_lat} to {max_lat}")
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
        original_data = raster.execute()
        masked_data = self._mask_raster_data(raster.execute(), polygon)
        # print(masked_data)
        self._visualize_mask(raster.execute(), masked_data, polygon)
        original_count = np.sum(~np.isnan(original_data.t2m.values))
        masked_count = np.sum(~np.isnan(masked_data.t2m.values))
        
        if original_count == masked_count:
            print("Mask Failed: Same number of valid points before and after masking")
        else:
            print(f"Mask Succeeded: Reduced from {original_count} to {masked_count} points")
        # masked_data = masked_data.dropna(dim="valid_time")
        # fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        # axes_flat = axs.flatten()

        # for i in range(4):
        #     im = axes_flat[i].pcolormesh(masked_data.longitude, masked_data.latitude, masked_data["t2m"][i,:,:])
        #     axes_flat[i].set_title(f'Slice {i}')
            
        # fig.colorbar(im, ax=axes_flat[0])
        # fig.colorbar(im, ax=axes_flat[1])
        # fig.colorbar(im, ax=axes_flat[2])
        # fig.colorbar(im, ax=axes_flat[3])
        # plt.tight_layout()
        # plt.show()
        return masked_data
        
from src.iharp_vector_predicate import GeoJsonExecutor

variable = "2m_temperature"
start_datetime = "2020-01-01 00:00:00"
end_datetime = "2023-12-31 23:00:00"
# inbound area
max_lat = 9
min_lat = 1
min_lon = 6
max_lon = 14
temporal_resolution = "year"
spatial_resolution = 0.25
aggregation = "max"
geojson_file = "/home/eldah001/iharp-vector-predicate/data/tri.geojson"

geojson = GeoJsonExecutor(
    variable=variable,
    start_datetime=start_datetime,
    end_datetime=end_datetime,
    temporal_resolution=temporal_resolution,
    spatial_resolution=spatial_resolution,
    aggregation=aggregation,
    geojson_file=geojson_file,
)

geojson_data = geojson.execute()
print(geojson_data)
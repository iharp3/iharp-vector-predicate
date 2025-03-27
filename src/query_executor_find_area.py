from query_executor import QueryExecutor
from query_executor_heatmap import HeatmapExecutor


class FindAreaExecutor(QueryExecutor):
    def __init__(
        self,
        variable: str,
        start_datetime: str,
        end_datetime: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        spatial_resolution: float,  # e.g., 0.25, 0.5, 1.0
        aggregation,  # e.g., "mean", "max", "min"
        heatmap_aggregation_method: str,  # e.g., "mean", "max", "min"
        filter_predicate: str,  # e.g., ">", "<", "==", "!=", ">=", "<="
        filter_value: float,
        metadata=None,  # metadata file path
    ):
        super().__init__(
            variable=variable,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon,
            temporal_resolution="hour",
            spatial_resolution=spatial_resolution,
            aggregation=aggregation,
            metadata=metadata,
        )
        self.heatmap_aggregation_method = heatmap_aggregation_method
        self.filter_predicate = filter_predicate
        self.filter_value = filter_value

    def execute(self):
        return self._execute_baseline()

    def _execute_baseline(self):
        heatmap_executor = HeatmapExecutor(
            self.variable,
            self.start_datetime,
            self.end_datetime,
            self.min_lat,
            self.max_lat,
            self.min_lon,
            self.max_lon,
            self.spatial_resolution,
            self.aggregation,
            self.heatmap_aggregation_method,
            metadata=self.metadata.f_path,
        )
        hm = heatmap_executor.execute()
        if self.filter_predicate == ">":
            res = hm.where(hm > self.filter_value, drop=False)
        elif self.filter_predicate == "<":
            res = hm.where(hm < self.filter_value, drop=False)
        elif self.filter_predicate == "==":
            res = hm.where(hm == self.filter_value, drop=False)
        elif self.filter_predicate == "!=":
            res = hm.where(hm != self.filter_value, drop=False)
        elif self.filter_predicate == ">=":
            res = hm.where(hm >= self.filter_value, drop=False)
        elif self.filter_predicate == "<=":
            res = hm.where(hm <= self.filter_value, drop=False)
        else:
            raise ValueError("Invalid filter_predicate")
        res = res.fillna(False)
        res = res.astype(bool)
        return res

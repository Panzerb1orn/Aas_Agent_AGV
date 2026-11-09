"""emission_service_config.py - Configuration classes for the emission service."""

from dataclasses import dataclass, field


@dataclass
class SubmodelElementConfig:
    """Reference to a SubmodelElement in any AAS repository."""
    base_url: str
    submodel_id: str
    id_short: str


@dataclass
class AGVConfig:
    """Configuration for aggregation settings in the emission service."""
    Battery_interval_seconds: int = 300    # Intervall zwischen Battery readings


@dataclass
class AGVServiceConfig:
    """Configuration for the emission service."""
    robot_enabled: bool = False
    robot_host: str = "192.168.10.28"
    robot_password: str = "zhaw"
    robot_port: int = 7171
    base_url: str = "http://localhost:8082"
    product_url: str = "http://localhost:8082"
    submodel_id: str = "https://www.example.com/subodel/partstorage/1"
    agv_submodel_id: str = "https://www.example.com/subodel/agv/1"
    sensor: SubmodelElementConfig = field(
        default_factory=lambda: SubmodelElementConfig(
            "http://localhost:8082",
            "http://example.com/submodel/monitoring",
            "sensorvalue0",
        )
    )
    station_index: int = 0

    # Production storage values
    value_idshort: str = "Red_parts"
    min_number_red_parts: str = "min_number_red_parts"
    min_battery_allowed_idshort: str = "min_battery_allowed"
    replenishment_goal: str = "ProductionStorage"

    # Aggregation settings
    AGV: AGVConfig = field(default_factory=lambda: AGVConfig())

    # Optional overrides for default paths
    Battery_trigger_path_override: str | None = None
    Battery_reset_path_override: str | None = None
    current_cf_submodel_override: str | None = None


    # Helper function for generating station paths
    def _station_path(self, suffix: str) -> str:
        """Generate the station path with the given suffix."""
        return f"Stations[{self.station_index}].{suffix}"

    # Set the default paths based on the station index if no overrides are provided.

    @property
    def Battery_trigger_path(self) -> str:
        """Get the battery trigger path, using override if available."""
        return self.Battery_trigger_path_override or self._station_path("triggeraggregation")

    @property
    def Battery_reset_path(self) -> str:
        """Get the battery reset path, using override if available."""
        return self.Battery_reset_path_override or self._station_path("resetaggregation")

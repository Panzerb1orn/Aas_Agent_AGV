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
    Battery_interval_seconds: int = 1    # Intervall zwischen Battery readings
    aggregation_max_count: int = 300         # Max Anzahl Schritte pro Lauf


@dataclass
class EmissionServiceConfig:
    """Configuration for the emission service."""
    # Mandatory fields:
    base_url: str
    product_url: str
    submodel_id: str
    sensor: SubmodelElementConfig
    station_index: int

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

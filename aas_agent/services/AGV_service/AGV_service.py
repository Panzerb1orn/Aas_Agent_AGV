"""AGV_service-py - Reads AGV Battery Percentage, current supply in Production Storage and sends job to AGV if necessary."""

import logging
import threading

from basyx.aas import model

from PyARCL import Robot

from ...config.AGV_service_config import AGVServiceConfig
from ...core.base_operation_service import BaseOperationService, GuardResult
from ...core.utils.submodel_repository import SubmodelRepository

logger = logging.getLogger(__name__)


class AGVService(BaseOperationService):
    """Service for Reading AGV Battery Percentage, current supply in Production Storage and sending job to AGV if necessary.

    Operations are explicitly registered in __init__ via self.register().
    Each operation is bound to a topic (idShort) and triggered by the EventHandler
    when a matching MQTT message is received.
    """

    def __init__(self, config: AGVServiceConfig) -> None:
        """Initialize the AGVService with the given configuration.

        Args:
            config: Configuration for this AGV service instance,
                    including AAS URLs, submodel IDs, sensor path, and aggregation settings.
        """
        self._config = config
        self.amr = Robot('192.168.10.12')

        """Read Battery Percentage"""
        battery_level = AMR.get_battery_level()

        """Read current supply in Production Storage"""
        current_supply = self._aas_client.get_value(self._config.current_supply_path)





     
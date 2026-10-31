"""AGV_service-py - Reads AGV Battery Percentage, current supply in Production Storage and sends job to AGV if necessary."""

import logging
import threading

from basyx.aas import model

#from PyARCL import Robot

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

  #  def __init__(self, config: AGVServiceConfig) -> None:
    def __init__(self) -> None:
        """Initialize the AGVService with the given configuration.

        Args:
            config: Configuration for this AGV service instance,
                    including AAS URLs, submodel IDs, sensor path, and aggregation settings.
        """
        #self._config = config
        #self.amr = Robot('192.168.10.12')

        # ── Configuration ───────────────────────────────────────────────────────
        self._base_url = "http://localhost:8082"
        self._value_idshort = "Red_parts"
        self._value_submodelid  = "https://www.example.com/subodel/partstorage/1"

        # ── Clients ───────────────────────────────────────────────────────
        self._part_storage_client = SubmodelRepository(self._base_url, self._value_submodelid)

        # ── BaseOperationService init (empty registry) ────────────────────
        super().__init__()

        # ── Register operations ───────────────────────────────────────────
        self.register(self.update_current_supply, topic=self._value_idshort)

        # ── Load initial values ────────────────────────────────────────────
        self._current_supply = self.update_current_supply()

    def update_current_supply(self, payload: str = "") -> None:
        """Fetch the current supply from the AAS."""
        try:
            response = self._part_storage_client.get_value_list(self._value_idshort)
            logger.info(f"Current supply fetched: {response}")

            self._current_supply = int(response)
            #response = requests.get(AAS_URL)
            #response.raise_for_status()
            #data = response.json()
            
            # NOTE: Adjust the parsing below based on your actual AAS JSON structure
            # This assumes a simple structure where 'supply' is a key
            # supply_value = data.get("supply", 0)
            return
        except Exception as e:
            logger.error(f"Failed to fetch supply from AAS: {e}")
            return 0




    # def check_and_dispatch(self) -> None:
    #     """Check battery and supply levels, then dispatch AGV if conditions are met."""
    #     battery_level = self.amr.get_battery_level()
    #     current_supply = self.get_current_supply()

    #     logger.info(f"Battery Level: {battery_level}%, Current Supply: {current_supply}")

    #     if current_supply < 5 and battery_level > 20:
    #         logger.info("Conditions met. Sending AGV to replenish supply.")
    #         self.send_robot()
    #     else:
    #         logger.info("Conditions not met. AGV remains idle.")

    # def send_robot(self) -> None:
    #     """Send the robot to the destination."""
    #     try:
    #         # Replace with the actual PyARCL command to send the robot
    #         # e.g., self.amr.send_job("ReplenishSupply")
    #         logger.info("Robot dispatched successfully.")
    #     except Exception as e:
    #         logger.error(f"Failed to dispatch robot: {e}")





     
"""AGV_service-py - Reads AGV Battery Percentage, current supply in Production Storage and sends job to AGV if necessary."""

import logging
import threading

from basyx.aas import model

from ...PyARCL.PyARCL import Robot

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
    def __init__(self, config: AGVServiceConfig) -> None:
        """Initialize the AGVService with the given configuration.

        Args:
            config: Configuration for this AGV service instance,
                    including AAS URLs, submodel IDs, sensor path, and aggregation settings.
        """
        self._config = config
        self.amr: Robot | None = None
        if self._config.robot_enabled:
            self.amr = Robot(
                self._config.robot_host,
                password=self._config.robot_password,
                port=self._config.robot_port,
            )

        # ── Locks ─────────────────────────────────────────────────────────
        self._battery_level_lock = threading.Lock()
        # self._aggregation_lock     = threading.Lock()
        # self._CFSubmodel_lock      = threading.Lock()        

        # ── Clients ───────────────────────────────────────────────────────
        self._part_storage_client = SubmodelRepository(
            self._config.base_url,
            self._config.submodel_id,
        )
        self._agv_client = SubmodelRepository(
            self._config.base_url,
            self._config.agv_submodel_id,
        )
        self._value_idshort = self._config.value_idshort
        self._min_number_red_parts = self._config.min_number_red_parts
        self._min_battery_allowed_idshort = self._config.min_battery_allowed_idshort

        # ── BaseOperationService init (empty registry) ────────────────────
        super().__init__()

        # ── Register operations ───────────────────────────────────────────
        self.register(self.update_current_supply, topic=self._value_idshort)
        self.register(self.update_min_supply, topic=self._min_number_red_parts)
        self.register(
            self.update_min_battery_allowed,
            topic=self._min_battery_allowed_idshort,
        )

        # ── Load initial values ────────────────────────────────────────────
        self._current_supply = self.update_current_supply()
        self._min_supply = self.update_min_supply()
        self._min_battery_allowed = self.update_min_battery_allowed()
        self._battery_level = None
        if self._config.robot_enabled:
            self._battery_level = self.check_battery_level()

        # ── Start Background Monitor ───────────────────────────────────────
        self._stop_monitor = threading.Event()
        self._monitor_thread: threading.Thread | None = None
        if self._config.robot_enabled:
            self._monitor_thread = threading.Thread(
                target=self._battery_monitor_loop,
                daemon=True,
            )
            self._monitor_thread.start()

    def _battery_monitor_loop(self) -> None:
        """Background loop to update battery level every 5 minutes."""
        # wait() returns False if the time elapsed, or True if the event was set (meaning we should stop)
        while not self._stop_monitor.wait(self._config.AGV.Battery_interval_seconds):  
            self._battery_level = self.check_battery_level()
            logger.info(f"Scheduled Update: Battery level is {self._battery_level}%")

    def stop(self) -> None:
        """Stop the background thread gracefully."""
        self._stop_monitor.set()
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            self._monitor_thread.join()
        super().stop()

    def update_current_supply(self, payload: str = "") -> None:
        """Fetch the current supply from the AAS."""
        try:
            response = self._part_storage_client.get_value_list(self._value_idshort)
            logger.info(f"Current supply fetched: {response}")

            self._current_supply = int(response)
            return
        except Exception as e:
            logger.error(f"Failed to fetch supply from AAS: {e}")
            return 0
        
    def update_min_supply(self, payload: str = "") -> None:
        """Fetch the current supply from the AAS."""
        try:
            response = self._part_storage_client.get_value_list(self._min_number_red_parts)
            logger.info(f"Minimum supply fetched: {response}")

            self._current_supply = int(response)
            return
        except Exception as e:
            logger.error(f"Failed to fetch minimumsupply from AAS: {e}")
            return 0

    def update_min_battery_allowed(self, payload: str = "") -> int | None:
        """Fetch the minimum battery level allowed for AGV operation."""
        try:
            response = self._agv_client.get_value(self._min_battery_allowed_idshort)
            if response is None:
                raise ValueError("AAS returned no value")

            self._min_battery_allowed = int(response)
            logger.info(
                f"Minimum allowed battery fetched: {self._min_battery_allowed}%"
            )
            return self._min_battery_allowed
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to parse minimum allowed battery: {e}")
            return None

    def check_battery_level(self) -> None:
        """Fetch the current battery level from the AGV."""
        if not self._config.robot_enabled or self.amr is None:
            logger.info("Robot communication is disabled; skipping battery update.")
            return

        try:
            battery_level = self.amr.status.stateOfCharge
            logger.info(f"Battery level fetched: {battery_level}%")
            with self._battery_level_lock:
                self._battery_level = battery_level
            return 
        except Exception as e:
            logger.error(f"Failed to fetch battery level: {e}")
            return



    # def check_and_dispatch(self) -> None:
    #     """Check battery and supply levels, then dispatch AGV if conditions are met."""
    #     battery_level = self.amr.status.stateOfCharge
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





     
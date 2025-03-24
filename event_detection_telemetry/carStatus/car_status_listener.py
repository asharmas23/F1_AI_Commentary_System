import json
import structlog
from f1_22_telemetry.packets import PacketCarStatusData

# Initialize structured logging
log = structlog.get_logger()

class CarStatusParser:
    """Handles parsing and storing F1 22 Car Status Data."""

    def __init__(self, file_handle):
        """
        Initializes the CarStatusParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketCarStatusData, player_indexes=None) -> dict:
        """
        Parses the Car Status Data packet and extracts status data for specified player indexes.

        Args:
            packet (PacketCarStatusData): The raw car status telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """
        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]  # Default to human player only

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "CarStatusData",
            "players": {}
        }

        for idx in player_indexes:
            if 0 <= idx < len(packet.car_status_data):
                car_status = packet.car_status_data[idx]
                parsed_data["players"][idx] = {
                    "actual_tyre_compound": car_status.actual_tyre_compound,
                    "anti_lock_brakes": car_status.anti_lock_brakes,
                    "drs_activation_distance": car_status.drs_activation_distance,
                    "drs_allowed": car_status.drs_allowed,
                    "ers_deploy_mode": car_status.ers_deploy_mode,
                    "ers_deployed_this_lap": car_status.ers_deployed_this_lap,
                    "ers_harvested_this_lap_mguh": car_status.ers_harvested_this_lap_mguh,
                    "ers_harvested_this_lap_mguk": car_status.ers_harvested_this_lap_mguk,
                    "ers_store_energy": car_status.ers_store_energy,
                    "front_brake_bias": car_status.front_brake_bias,
                    "fuel_capacity": car_status.fuel_capacity,
                    "fuel_in_tank": car_status.fuel_in_tank,
                    "fuel_mix": car_status.fuel_mix,
                    "fuel_remaining_laps": car_status.fuel_remaining_laps,
                    "idle_rpm": car_status.idle_rpm,
                    "max_gears": car_status.max_gears,
                    "max_rpm": car_status.max_rpm,
                    "network_paused": car_status.network_paused,
                    "pit_limiter_status": car_status.pit_limiter_status,
                    "traction_control": car_status.traction_control,
                    "tyres_age_laps": car_status.tyres_age_laps,
                    "vehicle_fia_flags": car_status.vehicle_fia_flags,
                    "visual_tyre_compound": car_status.visual_tyre_compound
                }

        return parsed_data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Car Status Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Car Status data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Car Status file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Car Status file: {e}")

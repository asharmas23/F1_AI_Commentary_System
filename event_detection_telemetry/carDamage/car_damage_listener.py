import json
import structlog
from f1_22_telemetry.packets import PacketCarDamageData

# Initialize structured logging
log = structlog.get_logger()

class CarDamageParser:
    """Handles parsing and storing F1 22 Car Damage Data."""

    def __init__(self, file_handle):
        """
        Initializes the CarDamageParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketCarDamageData, player_indexes=None) -> dict:
        """
        Parses the Car Damage Data packet and extracts data for specified player indexes.

        Args:
            packet (PacketCarDamageData): The raw car damage telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """
        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]  # Default to human player only

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "CarDamageData",
            "players": {}
        }

        for idx in player_indexes:
            if 0 <= idx < len(packet.car_damage_data):
                car_damage = packet.car_damage_data[idx]
                parsed_data["players"][idx] = {
                    "brakes_damage": list(car_damage.brakes_damage),
                    "diffuser_damage": car_damage.diffuser_damage,
                    "drs_fault": car_damage.drs_fault,
                    "engine_blown": car_damage.engine_blown,
                    "engine_control_electronics_wear": car_damage.engine_control_electronics_wear,
                    "engine_energy_store_wear": car_damage.engine_energy_store_qear,  # Fixed typo
                    "engine_internal_combustion_engine_wear": car_damage.engine_internal_combustion_engine_wear,
                    "engine_mguh_wear": car_damage.engine_mguh_wear,
                    "engine_mguk_wear": car_damage.engine_mguk_wear,
                    "engine_seized": car_damage.engine_seized,
                    "engine_traction_control_wear": car_damage.engine_traction_control_wear,
                    "engine_damage": car_damage.engined_damage,  # Fixed typo
                    "ers_fault": car_damage.ers_fault,
                    "floor_damage": car_damage.floor_damage,
                    "front_left_wing_damage": car_damage.front_left_wing_damage,
                    "front_right_wing_damage": car_damage.front_right_wing_damage,
                    "gearbox_damage": car_damage.gearbox_damage,
                    "rear_wing_damage": car_damage.rear_wing_damage,
                    "sidepod_damage": car_damage.sidepod_damage,
                    "tyres_damage": list(car_damage.tyres_damage),
                    "tyres_wear": list(car_damage.tyres_wear)
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
                json.dump(data, self.file_handle, indent=4)  # Use json.dump() for proper formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("File handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing file: {e}")

import json
import structlog
from f1_22_telemetry.packets import PacketCarSetupData

# Initialize structured logging
log = structlog.get_logger()

class CarSetupParser:
    """Handles parsing and storing F1 22 Car Setup Data."""

    def __init__(self, file_handle):
        """
        Initializes the CarSetupParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketCarSetupData, player_indexes=None) -> dict:
        """
        Parses the Car Setup Data packet and extracts setup data for specified player indexes.

        Args:
            packet (PacketCarSetupData): The raw car setup telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """
        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]  # Default to human player only

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "CarSetup",
            "players": {}
        }

        for idx in player_indexes:
            if 0 <= idx < len(packet.car_setups):
                setup = packet.car_setups[idx]
                parsed_data["players"][idx] = {
                    "front_wing": setup.front_wing,
                    "rear_wing": setup.rear_wing,
                    "on_throttle": setup.on_throttle,
                    "off_throttle": setup.off_throttle,
                    "front_camber": setup.front_camber,
                    "rear_camber": setup.rear_camber,
                    "front_toe": setup.front_toe,
                    "rear_toe": setup.rear_toe,
                    "front_suspension": setup.front_suspension,
                    "rear_suspension": setup.rear_suspension,
                    "front_anti_roll_bar": setup.front_anti_roll_bar,
                    "rear_anti_roll_bar": setup.rear_anti_roll_bar,
                    "front_suspension_height": setup.front_suspension_height,
                    "rear_suspension_height": setup.rear_suspension_height,
                    "brake_pressure": setup.brake_pressure,
                    "brake_bias": setup.brake_bias,
                    "rear_left_tyre_pressure": setup.rear_left_tyre_pressure,
                    "rear_right_tyre_pressure": setup.rear_right_tyre_pressure,
                    "front_left_tyre_pressure": setup.front_left_tyre_pressure,
                    "front_right_tyre_pressure": setup.front_right_tyre_pressure,
                    "ballast": setup.ballast,
                    "fuel_load": setup.fuel_load
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
                self.file_handle.write("\n")  # Each entry on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Car Setup Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Car Setup data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Car Setup file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Car Setup file: {e}")

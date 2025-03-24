import json
import structlog
from f1_22_telemetry.packets import PacketCarTelemetryData

# Initialize structured logging
log = structlog.get_logger()

class CarTelemetryParser:
    """Handles parsing and storing F1 22 Car Telemetry Data."""

    def __init__(self, file_handle):
        """
        Initializes the CarTelemetryParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    # def parse(self, packet):
    #     """Standardized parse method to be used in Listener."""
    #     return self.parse_telemetry_packet(packet)

    def parse(self, packet: PacketCarTelemetryData, player_indexes=None) -> dict:
        """
        Parses the Car Telemetry Data packet and extracts telemetry data for specified player indexes.

        Args:
            packet (PacketCarTelemetryData): The raw car telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """

        if not isinstance(packet, PacketCarTelemetryData):
            return None

        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "CarTelemetryData",
            "players": {}
        }

        for idx in player_indexes:
            if 0 <= idx < len(packet.car_telemetry_data):
                telemetry = packet.car_telemetry_data[idx]
                parsed_data["players"][idx] = {
                    "brake": telemetry.brake,
                    "brakes_temperature": list(telemetry.brakes_temperature),
                    "clutch": telemetry.clutch,
                    "drs_active": telemetry.drs,
                    "engine_rpm": telemetry.engine_rpm,
                    "engine_temperature": telemetry.engine_temperature,
                    "gear": telemetry.gear,
                    "rev_lights_bit_value": telemetry.rev_lights_bit_value,
                    "rev_lights_percent": telemetry.rev_lights_percent,
                    "speed_kph": telemetry.speed,
                    "steering_angle": telemetry.steer,
                    "surface_type": list(telemetry.surface_type),
                    "throttle": telemetry.throttle,
                    "tyres_inner_temperature": list(telemetry.tyres_inner_temperature),
                    "tyres_pressure": list(telemetry.tyres_pressure),
                    "tyres_surface_temperature": list(telemetry.tyres_surface_temperature),
                }

        return parsed_data if parsed_data["players"] else None

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
                log.info("Car Telemetry Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Car Telemetry data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Car Telemetry file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Car Telemetry file: {e}")

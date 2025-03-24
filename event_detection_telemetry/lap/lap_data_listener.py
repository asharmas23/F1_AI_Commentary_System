import json
import structlog
from f1_22_telemetry.packets import PacketLapData

# Initialize structured logging
log = structlog.get_logger()

class LapDataParser:
    """Handles parsing and storing F1 22 Lap Data."""

    def __init__(self, file_handle):
        """
        Initializes the LapDataParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketLapData, player_indexes=None) -> dict:
        """
        Parses the Lap Data packet and extracts lap data for specified player indexes.

        Args:
            packet (PacketLapData): The raw lap data telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """
        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]  # Default to human player only

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "LapData",
            "players": {}
        }

        for idx in player_indexes:
            if 0 <= idx < len(packet.lap_data):
                lap_data = packet.lap_data[idx]
                parsed_data["players"][idx] = {
                    "car_position": lap_data.car_position,
                    "current_lap_invalid": lap_data.current_lap_invalid,
                    "current_lap_num": lap_data.current_lap_num,
                    "current_lap_time_in_ms": lap_data.current_lap_time_in_ms,
                    "driver_status": lap_data.driver_status,
                    "grid_position": lap_data.grid_position,
                    "lap_distance": lap_data.lap_distance,
                    "last_lap_time_in_ms": lap_data.last_lap_time_in_ms,
                    "num_pit_stops": lap_data.num_pit_stops,
                    "num_unserved_drive_through_pens": lap_data.num_unserved_drive_through_pens,
                    "num_unserved_stop_go_pens": lap_data.num_unserved_stop_go_pens,
                    "penalties": lap_data.penalties,
                    "pit_lane_time_in_lane_in_ms": lap_data.pit_lane_time_in_lane_in_ms,
                    "pit_lane_timer_active": lap_data.pit_lane_timer_active,
                    "pit_status": lap_data.pit_status,
                    "pit_stop_should_serve_pen": lap_data.pit_stop_should_serve_pen,
                    "pit_stop_timer_in_ms": lap_data.pit_stop_timer_in_ms,
                    "result_status": lap_data.result_status,
                    "safety_car_delta": lap_data.safety_car_delta,
                    "sector": lap_data.sector,
                    "sector1_time_in_ms": lap_data.sector1_time_in_ms,
                    "sector2_time_in_ms": lap_data.sector2_time_in_ms,
                    "total_distance": lap_data.total_distance,
                    "warnings": lap_data.warnings,
                }

        return parsed_data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed lap telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Lap Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Lap Data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Lap Data file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Lap Data file: {e}")

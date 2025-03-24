import json
import structlog
from f1_22_telemetry.packets import PacketSessionHistoryData

# Initialize structured logging
log = structlog.get_logger()

class SessionHistoryParser:
    """Handles parsing and storing F1 22 Session History Data."""

    def __init__(self, file_handle):
        """
        Initializes the SessionHistoryParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketSessionHistoryData, player_indexes=None) -> dict:
        """
        Parses the Session History packet and extracts data for specified player indexes.

        Args:
            packet (PacketSessionHistoryData): The raw session history telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """
        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]  # Default to human player only

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "SessionHistory",
            "players": {}
        }

        for idx in player_indexes:
            if idx == packet.car_idx:  # Only process the current packet if it belongs to a requested player
                parsed_data["players"][idx] = {
                    "best_lap_time_lap_num": packet.best_lap_time_lap_num,
                    "best_sector1_lap_num": packet.best_sector1_lap_num,
                    "best_sector2_lap_num": packet.best_sector2_lap_num,
                    "best_sector3_lap_num": packet.best_sector3_lap_num,
                    "num_laps": packet.num_laps,
                    "num_tyre_stints": packet.num_tyre_stints,
                    "lap_history": [
                        {
                            "lap_time_in_ms": lap.lap_time_in_ms,
                            "sector1_time_in_ms": lap.sector1_time_in_ms,
                            "sector2_time_in_ms": lap.sector2_time_in_ms,
                            "sector3_time_in_ms": lap.sector3_time_in_ms,
                            "lap_valid_bit_flags": lap.lap_valid_bit_flags
                        }
                        for lap in packet.lap_history_data if lap.lap_time_in_ms > 0  # Remove empty lap data
                    ],
                    "tyre_stints": [
                        {
                            "end_lap": stint.end_lap,
                            "tyre_actual_compound": stint.tyre_actual_compound,
                            "tyre_visual_compound": stint.tyre_visual_compound
                        }
                        for stint in packet.tyre_stints_history_data if stint.end_lap > 0  # Remove empty stints
                    ]
                }

        return parsed_data if parsed_data["players"] else None  # Return None if no valid player data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed session history telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Session History Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Session History Data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Session History Data file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Session History Data file: {e}")

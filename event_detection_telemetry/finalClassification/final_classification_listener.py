import json
import structlog
from f1_22_telemetry.packets import PacketFinalClassificationData

# Initialize structured logging
log = structlog.get_logger()

class FinalClassificationParser:
    """Handles parsing and storing F1 22 Final Classification Data."""

    def __init__(self, file_handle):
        """
        Initializes the FinalClassificationParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketFinalClassificationData, player_indexes=None) -> dict:
        """
        Parses the Final Classification Data packet and extracts classification for all players.

        Args:
            packet (PacketFinalClassificationData): The raw final classification telemetry packet.

        Returns:
            dict: Parsed JSON data containing session-wide final classification.
        """
        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "FinalClassificationData",
            "final_classification": []
        }

        for classification in packet.classification_data:
            parsed_data["final_classification"].append({
                "best_lap_time_in_ms": classification.best_lap_time_in_ms,
                "grid_position": classification.grid_position,
                "num_laps": classification.num_laps,
                "num_penalties": classification.num_penalties,
                "num_pit_stops": classification.num_pit_stops,
                "num_tyre_stints": classification.num_tyre_stints,
                "penalties_time": classification.penalties_time,
                "points": classification.points,
                "position": classification.position,
                "result_status": classification.result_status,
                "total_race_time": classification.total_race_time,
                "tyre_stints_actual": list(classification.tyre_stints_actual),
                "tyre_stints_end_laps": list(classification.tyre_stints_end_laps),
                "tyre_stints_visual": list(classification.tyre_stints_visual)
            })

        return parsed_data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed final classification telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Final Classification Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Final Classification Data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Final Classification Data file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Final Classification Data file: {e}")

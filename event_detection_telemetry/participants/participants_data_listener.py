import json
import structlog
from f1_22_telemetry.packets import PacketParticipantsData

# Initialize structured logging
log = structlog.get_logger()

class ParticipantsDataParser:
    """Handles parsing and storing F1 22 Participants Data."""

    def __init__(self, file_handle):
        """
        Initializes the ParticipantsDataParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketParticipantsData, player_indexes=None) -> dict:
        """
        Parses the Participants Data packet and extracts participant data for specified player indexes.

        Args:
            packet (PacketParticipantsData): The raw participants telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """
        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]  # Default to human player only

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "ParticipantsData",
            "players": {}
        }

        for idx in player_indexes:
            if 0 <= idx < len(packet.participants):
                player_data = packet.participants[idx]
                parsed_data["players"][idx] = {
                    "ai_controlled": player_data.ai_controlled,
                    "driver_id": player_data.driver_id,
                    "my_team": player_data.my_team,
                    "name": player_data.name.decode("utf-8").strip().replace("\x00", ""),
                    "nationality": player_data.nationality,
                    "network_id": player_data.network_id,
                    "race_number": player_data.race_number,
                    "team_id": player_data.team_id,
                    "your_telemetry": player_data.your_telemetry
                }

        return parsed_data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed participants telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Participants Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Participants Data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Participants Data file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Participants Data file: {e}")

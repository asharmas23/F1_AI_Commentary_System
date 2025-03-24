import json
import structlog
from f1_22_telemetry.packets import PacketEventData

# Initialize structured logging
log = structlog.get_logger()

class EventDataParser:
    """Handles parsing and storing F1 22 Event Data."""

    def __init__(self, file_handle):
        """
        Initializes the EventDataParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketEventData, player_indexes=None) -> dict:
        """
        Parses the Event Data packet and extracts all relevant fields in a flattened format.

        Args:
            packet (PacketEventData): The raw event telemetry packet.

        Returns:
            dict: Parsed JSON data containing session-wide event details.
        """
        # Extract header information
        try:
            parsed_data = {
                "header": {
                                "frame_identifier": packet.header.frame_identifier,
                                "game_major_version": packet.header.game_major_version,
                                "game_minor_version": packet.header.game_minor_version,
                                "packet_format": packet.header.packet_format,
                                "packet_id": packet.header.packet_id,
                                "packet_version": packet.header.packet_version,
                                "player_car_index": packet.header.player_car_index,
                                "secondary_player_car_index": packet.header.secondary_player_car_index,
                                "session_time": packet.header.session_time,
                                "session_uid": packet.header.session_uid,
                            },
                "packet_type": "EventData",
                "event_string_code": "".join(map(chr, packet.event_string_code)),  # Convert byte array to string
                # "event_details": packet.event_details.buttons.button_status
                "event_details": {
                            "event_details": {
                                "buttons": {"button_status": packet.event_details.buttons.button_status},
                                "drive_through_penalty_served": {"vehicle_idx": packet.event_details.drive_through_penalty_served.vehicle_idx},
                                "fastest_lap": {"lap_time": packet.event_details.fastest_lap.lap_time, "vehicle_idx": packet.event_details.fastest_lap.vehicle_idx},
                                "flashback": {
                                    "flashback_frame_identifier":  packet.event_details.flashback.flashback_frame_identifier,
                                    "flashback_session_time": packet.event_details.flashback.flashback_session_time,
                                },
                                "penalty": {
                                    "infringement_type": packet.event_details.penalty.infringement_type,
                                    "lap_num": packet.event_details.penalty.lap_num,
                                    "other_vehicle_idx": packet.event_details.penalty.other_vehicle_idx,
                                    "penalty_type": packet.event_details.penalty.penalty_type,
                                    "places_gained": packet.event_details.penalty.places_gained,
                                    "time": packet.event_details.penalty.time,
                                    "vehicle_idx": packet.event_details.penalty.vehicle_idx,
                                },
                                "race_winner": {"vehicle_idx": packet.event_details.race_winner.vehicle_idx},
                                "retirement": {"vehicle_idx": packet.event_details.retirement.vehicle_idx},
                                "speed_trap": {
                                    "fastest_speed_in_session": packet.event_details.speed_trap.fastest_speed_in_session,
                                    "fastest_vehicle_idx_in_sSession": packet.event_details.speed_trap.fastest_vehicle_idx_in_sSession,
                                    "is_driver_fastest_in_session": packet.event_details.speed_trap.is_driver_fastest_in_session,
                                    "overall_fastest_in_session": packet.event_details.speed_trap.overall_fastest_in_session,
                                    "speed": packet.event_details.speed_trap.speed,
                                    "vehicle_idx": packet.event_details.speed_trap.vehicle_idx,
                                },
                                "start_lights": {"num_lights": packet.event_details.start_lights.num_lights},
                                "stop_go_penalty_served": {"vehicle_idx": packet.event_details.stop_go_penalty_served.vehicle_idx},
                                "team_mate_in_pits": {"vehicle_idx": packet.event_details.team_mate_in_pits.vehicle_idx},
                            }
                        }
            }       

        except AttributeError as e:
            log.error(f"Error extracting event details: {e}")

        return parsed_data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed event telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Event Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Event Data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Event Data file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Event Data file: {e}")

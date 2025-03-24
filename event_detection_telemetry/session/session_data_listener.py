import json
import structlog
from f1_22_telemetry.packets import PacketSessionData

# Initialize structured logging
log = structlog.get_logger()

class SessionDataParser:
    """Handles parsing and storing F1 22 Session Data."""

    def __init__(self, file_handle):
        """
        Initializes the SessionDataParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketSessionData, player_indexes=None) -> dict:
        """
        Parses the Session Data packet and extracts all relevant fields in alphabetical order.

        Args:
            packet (PacketSessionData): The raw session telemetry packet.

        Returns:
            dict: Parsed JSON data containing session-wide details.
        """
        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "SessionData",
            "session_data": {
                "ai_difficulty": packet.ai_difficulty,
                "air_temperature": packet.air_temperature,
                "braking_assist": packet.braking_assist,
                "drs_assist": packet.drs_assist,
                "dynamic_racing_line": packet.dynamic_racing_line,
                "dynamic_racing_line_type": packet.dynamic_racing_line_type,
                "ers_assist": packet.ers_assist,
                "forecast_accuracy": packet.forecast_accuracy,
                "formula": packet.formula,
                "game_mode": packet.game_mode,
                "game_paused": packet.game_paused,
                "gearbox_assist": packet.gearbox_assist,
                "is_spectating": packet.is_spectating,
                "marshal_zones": [
                    {"zone_start": mz.zone_start, "zone_flag": mz.zone_flag}
                    for mz in packet.marshal_zones[:packet.num_marshal_zones]
                ],
                "network_game": packet.network_game,
                "num_marshal_zones": packet.num_marshal_zones,
                "num_weather_forecast_samples": packet.num_weather_forecast_samples,
                "pit_assist": packet.pit_assist,
                "pit_release_assist": packet.pit_release_assist,
                "pit_speed_limit": packet.pit_speed_limit,
                "pit_stop_rejoin_position": packet.pit_stop_rejoin_position,
                "pit_stop_window_ideal_lap": packet.pit_stop_window_ideal_lap,
                "pit_stop_window_latest_lap": packet.pit_stop_window_latest_lap,
                "rule_set": packet.rule_set,
                "safety_car_status": packet.safety_car_status,
                "season_link_identifier": packet.season_link_identifier,
                "session_duration": packet.session_duration,
                "session_length": packet.session_length,
                "session_link_identifier": packet.session_link_identifier,
                "session_time_left": packet.session_time_left,
                "session_type": packet.session_type,
                "sli_pro_native_support": packet.sli_pro_native_support,
                "spectator_car_index": packet.spectator_car_index,
                "steering_assist": packet.steering_assist,
                "time_of_day": packet.time_of_day,
                "total_laps": packet.total_laps,
                "track_id": packet.track_id,
                "track_length": packet.track_length,
                "track_temperature": packet.track_temperature,
                "weather": packet.weather,
                "weather_forecast_samples": [
                    {
                        "time_offset": wf.time_offset,
                        "weather": wf.weather,
                        "track_temperature": wf.track_temperature,
                        "track_temperature_change": wf.track_temperature_change,
                        "air_temperature": wf.air_temperature,
                        "air_temperature_change": wf.air_temperature_change,
                        "rain_percentage": wf.rain_percentage
                    }
                    for wf in packet.weather_forecast_samples[:packet.num_weather_forecast_samples]
                ],
                "weekend_link_identifier": packet.weekend_link_identifier
            }
        }

        return parsed_data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed session telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Session Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Session Data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Session Data file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Session Data file: {e}")

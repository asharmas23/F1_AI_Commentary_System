import json
import structlog
from f1_22_telemetry.packets import PacketMotionData

# Initialize structured logging
log = structlog.get_logger()

class MotionDataParser:
    """Handles parsing and storing F1 22 Motion Data."""

    def __init__(self, file_handle):
        """
        Initializes the MotionDataParser.

        Args:
            file_handle (file object): Open file handle to write parsed data.
        """
        self.file_handle = file_handle

    def parse(self, packet: PacketMotionData, player_indexes=None) -> dict:
        """
        Parses the Motion Data packet and extracts motion data for specified player indexes.

        Args:
            packet (PacketMotionData): The raw motion telemetry packet.
            player_indexes (list, optional): List of player indexes to extract data for. Defaults to None (human player only).

        Returns:
            dict: Parsed JSON data containing only the specified player indexes.
        """
        if player_indexes is None:
            player_indexes = [packet.header.player_car_index]  # Default to human player only

        parsed_data = {
            "timestamp": packet.header.session_time,
            "packet_type": "MotionData",
            "players": {}
        }

        for idx in player_indexes:
            if 0 <= idx < len(packet.car_motion_data):
                motion_data = packet.car_motion_data[idx]
                parsed_data["players"][idx] = {
                    "g_force_lateral": motion_data.g_force_lateral,
                    "g_force_longitudinal": motion_data.g_force_longitudinal,
                    "g_force_vertical": motion_data.g_force_vertical,
                    "pitch": motion_data.pitch,
                    "roll": motion_data.roll,
                    "yaw": motion_data.yaw,
                    "world_forward_dir": [motion_data.world_forward_dir_x, motion_data.world_forward_dir_y, motion_data.world_forward_dir_z],
                    "world_position": [motion_data.world_position_x, motion_data.world_position_y, motion_data.world_position_z],
                    "world_right_dir": [motion_data.world_right_dir_x, motion_data.world_right_dir_y, motion_data.world_right_dir_z],
                    "world_velocity": [motion_data.world_velocity_x, motion_data.world_velocity_y, motion_data.world_velocity_z]
                }

        parsed_data.update({
            "local_velocity": [packet.local_velocity_x, packet.local_velocity_y, packet.local_velocity_z],
            "angular_velocity": [packet.angular_velocity_x, packet.angular_velocity_y, packet.angular_velocity_z],
            "angular_acceleration": [packet.angular_acceleration_x, packet.angular_acceleration_y, packet.angular_acceleration_z],
            "suspension_position": list(packet.suspension_position),
            "suspension_velocity": list(packet.suspension_velocity),
            "suspension_acceleration": list(packet.suspension_acceleration),
            "wheel_speed": list(packet.wheel_speed),
            "wheel_slip": list(packet.wheel_slip),
            "front_wheels_angle": packet.front_wheels_angle
        })

        return parsed_data

    def save_to_file(self, data: dict):
        """
        Writes parsed data to an **open** file handle.

        Args:
            data (dict): The parsed motion telemetry data to be saved.
        """
        try:
            if data:
                json.dump(data, self.file_handle, indent=4)  # Proper JSON formatting
                self.file_handle.write("\n")  # Ensure each entry is on a new line
                self.file_handle.flush()  # Flush immediately for real-time updates
                log.info("Motion Data successfully written to file.")
        except Exception as e:
            log.error(f"Failed to write Motion Data: {e}")

    def close_file(self):
        """
        Closes the file handle to ensure proper saving.
        """
        try:
            self.file_handle.close()
            log.info("Motion Data file handle successfully closed.")
        except Exception as e:
            log.error(f"Error closing Motion Data file: {e}")

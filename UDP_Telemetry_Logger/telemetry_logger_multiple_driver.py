import logging
import csv
import threading
import signal
import sys
import os
import time
import datetime
import re
import shutil
from f1_22_telemetry.listener import TelemetryListener
from f1_22_telemetry.packets import *

class TelemetryLogger:
    """Handles directory creation and file writing operations for telemetry data."""

    def __init__(self, base_dir="Data"):
        self.base_dir = os.path.join(os.getcwd(), base_dir)
        self.log_dir = None
        self.driver_folders = {}

    def create_main_directory(self, track_name):
        """Creates the main directory for the telemetry session."""
        session_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_dir = os.path.join(self.base_dir, f"{track_name}_{session_date}")
        os.makedirs(self.log_dir, exist_ok=True)
        self.create_main_csv_files()  # Ensure session-wide CSV files are created

    def create_main_csv_files(self):
        """Ensure session-wide CSV files (session & event) exist in the main directory."""
        if self.log_dir:
            main_files = {
                "session": os.path.join(self.log_dir, "session_data.csv"),
                "event": os.path.join(self.log_dir, "event_data.csv"),
            }

            headers = {
                "session": ["timestamp", "weather", "track_temperature", "air_temperature",
                            "safety_car_status", "total_laps", "track_length"],
                "event": ["timestamp", "event_code"],
            }

            for category, path in main_files.items():
                if not os.path.exists(path):
                    with open(path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(headers[category])  # Write column headers

    def write_to_main_csv(self, category, row):
        """Writes a row to the session-wide CSV file."""
        if self.log_dir:
            file_path = os.path.join(self.log_dir, f"{category}_data.csv")
            with open(file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

    def create_driver_directory(self, driver_index, driver_name, track_name, is_player):
        """Creates a folder for each driver inside the main track directory."""
        if self.log_dir:
            player_type = "Player" if is_player else "AI"
            driver_folder = os.path.join(self.log_dir, f"{player_type}_{track_name}_{driver_name}")
            os.makedirs(driver_folder, exist_ok=True)

            self.driver_folders[driver_index] = {
                "path": driver_folder,
                "motion": os.path.join(driver_folder, "motion_data.csv"),
                "lap": os.path.join(driver_folder, "lap_data.csv"),
                "car_telemetry": os.path.join(driver_folder, "car_telemetry.csv"),
                "car_status": os.path.join(driver_folder, "car_status.csv"),
                "car_damage": os.path.join(driver_folder, "car_damage.csv"),
            }

            headers = {
                "motion": ["timestamp", "position_x", "position_y", "position_z", "velocity_x", "velocity_y",
                           "velocity_z", "g_force_lateral", "g_force_longitudinal", "g_force_vertical"],
                "lap": ["timestamp", "lap_time_ms", "sector1_time_ms", "sector2_time_ms", "lap_invalid"],
                "car_telemetry": ["timestamp", "speed_kmh", "throttle", "brake", "gear", "engine_rpm", "drs",
                                  "tire_temp_FL", "tire_temp_FR", "tire_temp_RL", "tire_temp_RR"],
                "car_status": ["timestamp", "fuel_remaining_laps", "ers_energy", "drs_allowed", "tyre_age_laps"],
                "car_damage": ["timestamp", "tyre_wear_FL", "tyre_wear_FR", "tyre_wear_RL", "tyre_wear_RR",
                               "brakes_damage_FL", "brakes_damage_FR", "brakes_damage_RL", "brakes_damage_RR",
                               "gearbox_damage", "engine_damage"]
            }

            for category, path in self.driver_folders[driver_index].items():
                if category != "path" and not os.path.exists(path):
                    with open(path, 'w', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow(headers[category])

    def write_to_csv(self, driver_index, category, row):
        """Writes a row to the respective driver’s category CSV file."""
        if driver_index in self.driver_folders:
            with open(self.driver_folders[driver_index][category], 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(row)

class TelemetryProcessor:
    """Processes telemetry data packets and writes them to corresponding files."""

    def __init__(self, logger):
        self.logger = logger
        self.track_name = None

    def process_packet(self, packet):
        """Processes packets and directs them to the appropriate logging function."""
        timestamp = packet.header.session_time

        # ✅ 1. SESSION DATA (Global Logging)
        if isinstance(packet, PacketSessionData):
            self.track_name = f"Track_{packet.track_id}"
            if not self.logger.log_dir:
                self.logger.create_main_directory(self.track_name)

            self.logger.write_to_main_csv("session", [
                timestamp, packet.weather, packet.track_temperature, packet.air_temperature,
                packet.safety_car_status, packet.total_laps, packet.track_length
            ])

        # ✅ 2. EVENT DATA (Global Logging)
        elif isinstance(packet, PacketEventData):
            event_code = bytes(packet.event_string_code).decode("utf-8").strip()
            self.logger.write_to_main_csv("event", [timestamp, event_code])

        # ✅ 3. PARTICIPANTS DATA (Creates Driver Directories)
        elif isinstance(packet, PacketParticipantsData):
            for i, participant in enumerate(packet.participants):
                driver_name = participant.name.decode("utf-8").strip()
                is_player = i == packet.header.player_car_index
                self.logger.create_driver_directory(i, driver_name, self.track_name, is_player)

        # ✅ 4. MOTION DATA (Per Driver)
        elif isinstance(packet, PacketMotionData):
            for i, player in enumerate(packet.car_motion_data):
                self.logger.write_to_csv(i, "motion", [
                    timestamp, player.world_position_x, player.world_position_y, player.world_position_z,
                    player.world_velocity_x, player.world_velocity_y, player.world_velocity_z,
                    player.g_force_lateral, player.g_force_longitudinal, player.g_force_vertical
                ])

        # ✅ 5. LAP DATA (Per Driver)
        elif isinstance(packet, PacketLapData):
            for i, player in enumerate(packet.lap_data):
                self.logger.write_to_csv(i, "lap", [
                    timestamp, player.current_lap_time_in_ms, player.sector1_time_in_ms,
                    player.sector2_time_in_ms, player.current_lap_invalid
                ])

        # ✅ 6. CAR TELEMETRY DATA (Per Driver)
        elif isinstance(packet, PacketCarTelemetryData):
            for i, player in enumerate(packet.car_telemetry_data):
                self.logger.write_to_csv(i, "car_telemetry", [
                    timestamp, player.speed, player.throttle, player.brake, player.gear,
                    player.engine_rpm, "Active" if player.drs else "Inactive",
                    *player.tyres_surface_temperature
                ])

        # ✅ 7. CAR STATUS DATA (Per Driver)
        elif isinstance(packet, PacketCarStatusData):
            for i, player in enumerate(packet.car_status_data):
                self.logger.write_to_csv(i, "car_status", [
                    timestamp, player.fuel_remaining_laps, player.ers_store_energy,
                    player.drs_allowed, player.tyres_age_laps
                ])

        # ✅ 8. CAR DAMAGE DATA (Per Driver)
        elif isinstance(packet, PacketCarDamageData):
            for i, player in enumerate(packet.car_damage_data):
                self.logger.write_to_csv(i, "car_damage", [
                    timestamp, player.tyres_wear[0], player.tyres_wear[1], player.tyres_wear[2], player.tyres_wear[3],
                    player.brakes_damage[0], player.brakes_damage[1], player.brakes_damage[2], player.brakes_damage[3],
                    player.gearbox_damage, player.engined_damage  
                ])

class TelemetryListenerManager:
    """Handles the telemetry listener and manages packet processing and cleanup."""

    def __init__(self, host='127.0.0.1', port=20777):
        self.host = host
        self.port = port
        self.listener = TelemetryListener(host, port)
        self.logger = TelemetryLogger()
        self.processor = TelemetryProcessor(self.logger)
        self.run_event = threading.Event()
        self.run_event.set()
        self.listener_thread_instance = None

    def listener_thread(self):
        """Thread that listens for incoming telemetry data."""
        print(f"📡 Listening for F1 22 telemetry data on {self.host}:{self.port}...")
        logging.info("Telemetry listener started.")

        while self.run_event.is_set():
            try:
                packet = self.listener.get()
                if packet:
                    self.processor.process_packet(packet)
            except TimeoutError:
                continue
            except Exception as e:
                logging.error(f"Error in listener: {e}")
                break

        print("🛑 Stopping telemetry listener...")

    def start(self):
        """Starts the telemetry listener in a separate thread."""
        self.listener_thread_instance = threading.Thread(target=self.listener_thread)
        self.listener_thread_instance.start()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def handle_exit(self, signum, frame):
        """Handles graceful shutdown and cleans up incorrectly named driver folders."""
        print("\n🚀 Attempting to close listener. Please wait...")
        logging.info("Shutting down telemetry listener...")

        self.run_event.clear()  # Stop the listener thread
        if self.listener_thread_instance:
            self.listener_thread_instance.join(timeout=3)  # Wait for thread to finish

        # Cleanup: Remove incorrectly named driver folders
        if self.logger.log_dir:
            for folder_name in os.listdir(self.logger.log_dir):
                folder_path = os.path.join(self.logger.log_dir, folder_name)

                # Skip if not a directory
                if not os.path.isdir(folder_path):
                    continue

                # Check if folder name matches "AI_Track_<number>_" or "AI_Track_<number>_YYYY-MM-DD_HH-MM-SS"
                if re.match(r"^AI_Track_\d_+(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})?$", folder_name):
                    try:
                        shutil.rmtree(folder_path)
                        print(f"🗑️ Removed incorrect folder: {folder_name}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete {folder_name}: {e}")

        print("✅ Listener stopped successfully. Exiting now.")
        sys.exit(0)  # Ensure proper exit
        
def main():
    """Main function to start telemetry listener and handle shutdown."""
    telemetry_manager = TelemetryListenerManager()

    telemetry_manager.start()  # Start the telemetry listener

    try:
        while telemetry_manager.run_event.is_set():
            time.sleep(0.1)  # Prevent high CPU usage
    except KeyboardInterrupt:
        telemetry_manager.handle_exit(None, None)  # Call handle_exit on CTRL+C


if __name__ == "__main__":
    main()

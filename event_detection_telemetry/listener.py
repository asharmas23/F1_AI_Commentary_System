import json
import threading
import structlog
import sys
from carDamage.car_damage_listener import CarDamageParser
from carTelemetry.car_telemetry_listener import CarTelemetryParser
from carSetup.car_setup_listener import CarSetupParser
from carStatus.car_status_listener import CarStatusParser
from event.event_data_listener import EventDataParser
from finalClassification.final_classification_listener import FinalClassificationParser
from lap.lap_data_listener import LapDataParser
from motion.motion_data_listener import MotionDataParser
from participants.participants_data_listener import ParticipantsDataParser
from session.session_data_listener import SessionDataParser
from sessionHistory.session_history_listener import SessionHistoryParser
from packetQueue.packet_queue import PacketQueue

# Initialize structured logging
log = structlog.get_logger()

class Listener:
    """Listener class that runs a separate thread for processing packets and writing JSON data."""

    def __init__(self, packet_type, player_indexes, datetime):
        """
        Initializes a listener for a specific packet type.

        Args:
            packet_type (str): The type of telemetry packet to process.
            player_indexes (list): The list of player indexes to extract data for.
            datetime (str): Unique timestamp for file naming.
        """
        self.packet_type = packet_type
        self.player_indexes = player_indexes  # Store player indexes
        self.file_name = f"{packet_type}_{datetime}.json"
        self.file_handle = open(self.file_name, "a")  # Keep file open for appending
        self.shutdown_event = threading.Event()
        self.lock = threading.Lock()  # Ensures safe multi-threaded file writing

        # Initialize the appropriate parser dynamically
        self.parser = self._initialize_parser()

        # Start processing thread
        self.thread = threading.Thread(target=self.process_packets, daemon=True)
        self.thread.start()

    def _initialize_parser(self):
        """Dynamically initializes the correct parser based on `packet_type`."""
        parser_mapping = {
            "carDamage": CarDamageParser,
            "carTelemetry": CarTelemetryParser,
            "carSetup": CarSetupParser,
            "carStatus": CarStatusParser,
            "event": EventDataParser,
            "finalClassification": FinalClassificationParser,
            "lap": LapDataParser,
            "motion": MotionDataParser,
            "participants": ParticipantsDataParser,
            "session": SessionDataParser,
            "sessionHistory": SessionHistoryParser,
        }

        return parser_mapping.get(self.packet_type, None)(self.file_handle) if self.packet_type in parser_mapping else None



    def process_packets(self):
        """Continuously processes packets received from main_handler."""
        log.info(f"Started listener for {self.packet_type}. Writing to {self.file_name}.")

        while not self.shutdown_event.is_set():
            try:
                packet_data = PacketQueue.get(self.packet_type)  
                if packet_data:
                    packet, player_indexes = packet_data 

                    if self.parser:
                        json_packet = self.parser.parse(packet, player_indexes)

                        with self.lock:  # Thread-safe file writing
                            self.parser.save_to_file(json_packet)

            except Exception as e:
                log.error(f"Error processing {self.packet_type}: {e}")

        log.info(f"Stopping {self.packet_type} listener.")

    def handle_exit(self, signum=None, frame=None):
        """Handles graceful shutdown and closes file properly."""
        log.info(f"\n[INFO] Stopping {self.packet_type} listener...")

        self.shutdown_event.set()

        # Ensure thread stops safely
        if self.thread.is_alive():
            self.thread.join(timeout=1)

        # Ensure file closure
        try:
            with self.lock:
                self.file_handle.close()
                log.info(f"[INFO] Closed {self.packet_type}.json")
        except Exception as e:
            log.error(f"Error closing file {self.file_name}: {e}")
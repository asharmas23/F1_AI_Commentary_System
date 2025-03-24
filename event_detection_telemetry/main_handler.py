import structlog
import threading
import signal
import sys
import datetime
from f1_22_telemetry.listener import TelemetryListener
from f1_22_telemetry.packets import (
    PacketCarDamageData, PacketCarTelemetryData, PacketCarSetupData, PacketCarStatusData, 
    PacketEventData, PacketFinalClassificationData, PacketLapData, PacketMotionData, 
    PacketParticipantsData, PacketSessionData, PacketSessionHistoryData
)
from packetQueue.packet_queue import PacketQueue
from listener import Listener

# Initialize structured logging
log = structlog.get_logger()

class MainTelemetryListener:
    """A class to listen to and forward F1 22 telemetry packets."""

    _instance = None

    def __init__(self, packet_types=None, player_indexes=None, ip='127.0.0.1', port=20777):
        """Initializes the listener and starts dedicated packet processors."""
        if MainTelemetryListener._instance is not None:
            raise RuntimeError("An instance of MainTelemetryListener already exists.")

        MainTelemetryListener._instance = self
        self.ip = ip
        self.port = port
        self.packet_types = packet_types or ["carDamage","carTelemetry","session"]  # Default packet type
        self.player_indexes = player_indexes  # Store player indexes

        self.session_date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Initialize queues & listeners
        self.listeners = {}
        for packet_type in self.packet_types:
            PacketQueue.add_queue(packet_type)
            self.listeners[packet_type] = Listener(packet_type, self.player_indexes, self.session_date)

        self.listener = TelemetryListener(host=self.ip, port=self.port)
        self.shutdown_event = threading.Event()

        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def listen(self):
        """Listens to F1 22 telemetry packets and adds them to processing queues."""
        log.info(f"Listening on {self.ip}:{self.port} for packets: {self.packet_types}")

        packet_mapping = {
            "carDamage": PacketCarDamageData,
            "carTelemetry": PacketCarTelemetryData,
            "carSetup": PacketCarSetupData,
            "carStatus": PacketCarStatusData,
            "event": PacketEventData,
            "finalClassification": PacketFinalClassificationData,
            "lap": PacketLapData,
            "motion": PacketMotionData,
            "participants": PacketParticipantsData,
            "session": PacketSessionData,
            "sessionHistory": PacketSessionHistoryData,
        }

        while not self.shutdown_event.is_set():
            try:
                packet = self.listener.get()

                for packet_type, packet_class in packet_mapping.items():
                    if isinstance(packet, packet_class) and packet_type in self.packet_types:
                        PacketQueue.put(packet_type, (packet, self.player_indexes))  # Pass tuple

            except Exception as e:
                log.error(f"Error: {e}")
                break

        log.info("Listener stopped.")

    def start(self):
        """Starts the telemetry listener in a separate thread."""
        listener_thread = threading.Thread(target=self.listen, daemon=True)
        listener_thread.start()

        try:
            while listener_thread.is_alive():
                listener_thread.join(timeout=1)
        except KeyboardInterrupt:
            self.handle_exit(None, None)

    def handle_exit(self, signum, frame):
        """Handles graceful shutdown and stops all threads."""
        log.info("\n[INFO] Stopping MainTelemetryListener...")

        self.shutdown_event.set()

        for packet_type, listener in self.listeners.items():
            listener.handle_exit(signum, frame)

        log.info("[INFO] Listener successfully stopped.")
        sys.exit(0)


if __name__ == "__main__":
    # listener = MainTelemetryListener(
    #     packet_types=["carTelemetry", "carSetup", "session"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["carDamage"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["carTelemetry"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["carSetup"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["carStatus"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["event"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["finalClassification"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["lap"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["motion"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["participants"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["session"],
    #     player_indexes=[3, 19, 15]
    # )
    # listener = MainTelemetryListener(
    #     packet_types=["sessionHistory"],
    #     player_indexes=[3, 19, 15]
    # )
    listener = MainTelemetryListener()
    listener.start()

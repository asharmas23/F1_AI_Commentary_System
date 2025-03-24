import json
import structlog
from f1_22_telemetry.listener import TelemetryListener
from f1_22_telemetry.packets import PacketLobbyInfoData

# File to store raw lobby info data packets
OUTPUT_FILE = "raw_lobby_info_data.json"

def save_to_file(data):
    """Appends the complete raw packet to a file for review."""
    with open(OUTPUT_FILE, "a") as file:
        file.write(json.dumps(data, indent=4) + ",\n")  # Append JSON object


def start_telemetry_listener():
    """Listens to F1 22 telemetry data and saves raw Lobby Info Data packets."""
    listener = TelemetryListener(port=20777)  # Default F1 22 telemetry port

    print(f"[INFO] Listening to F1 22 Lobby Info Data Packets. Data is being saved to {OUTPUT_FILE}")

    while True:
        packet = listener.get()  # Get the latest telemetry packet

        if packet is None:
            print("[WARNING] Received an empty packet. Check UDP settings.")
            continue  # Skip empty packets

        if isinstance(packet, PacketLobbyInfoData):
            print(packet)  # Print raw packet data
            # save_to_file(vars(packet))  # Save packet data
            break  # Stop after receiving one packet


if __name__ == "__main__":
    start_telemetry_listener()

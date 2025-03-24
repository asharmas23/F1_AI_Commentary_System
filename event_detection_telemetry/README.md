# Event Detection Telemetry Pipeline

The **Event Detection Telemetry** module is a performance-oriented telemetry parser designed to extract structured race events from raw F1 22 telemetry data. This forms the foundation for AI-driven analysis, commentary generation, and performance coaching.

---

## 🌍 Overview

### 🔧 Purpose
To transform raw telemetry data into structured, driver-specific JSON packets that represent key race events (e.g., overtakes, pit stops, tire wear, mechanical issues), optimized for real-time Large Language Model (LLM) consumption.

---



### ✅ **Background & Motivation**
Telemetry from the F1 22 game is rich and continuous but not inherently structured for storytelling, coaching, or commentary. There's a need to extract significant moments from the raw feed and format them in a way suitable for downstream AI models.

### ✅ **Design Goals**
Design and implement a multi-threaded pipeline that:
- Parses specific telemetry message types.
- Filters for the human player's data.
- Structures JSON outputs for LLM input.
- Operates in near real-time with minimal overhead.

### ✅ **How It Works**
- Built a threaded telemetry parser that subscribes to the same UDP data stream used by the logger.
- Implemented custom logic to handle:
  - Session-wide messages (like event and session metadata).
  - Player-specific messages (e.g., car status, damage, telemetry).
- Flattened the data structure into clean, one-layer JSON packets.
- Output categorized into folders by message type and saved incrementally to disk for efficiency.
- Alphabetized fields for consistency with LLM expectations.

### ✅ **Impact & Outcomess**
- Achieved fast, low-latency transformation of telemetry data into rich JSON packets.
- Created a foundation for real-time AI commentary systems.
- Enabled post-race analysis pipelines to process meaningful, contextual race data.

---

## ⚙️ Implementation Details

### 🧩 Components
- `parser_event_detection.py`: Main script for threaded telemetry parsing and JSON generation.
- `utils.py`: Shared helper functions (packet extraction, folder management, etc.).
- `json_output/`: Destination folder for generated JSON event logs.

### 🧠 Parsing Logic
- Telemetry packet types supported:
  - `PacketSessionData`
  - `PacketEventData`
  - `PacketParticipantsData`
  - `PacketCarStatusData`
  - `PacketCarDamageData`
  - `PacketFinalClassificationData`
- Session-wide packets are stored once per race.
- Player-specific packets are filtered using `header.playerCarIndex`.

### 📁 Output Format

```json
{
  "driver_name": "ALBON",
  "speed": 198,
  "engine_temperature": 103,
  "brakes_temp": [456, 470, 445, 462],
  "ers_deployed": 0.3,
  "tyre_wear": [0.12, 0.15, 0.13, 0.14],
  ...
}
```

Each file contains telemetry for a single message type and driver, optimized for rapid LLM inference.

---

## 🚀 How to Use

1. Ensure the F1 22 game is running and UDP telemetry is enabled.
2. Run the parser:

```bash
python parser_event_detection.py
```

3. JSON files will be saved into the `json_output/` folder, organized by packet type.

---

## 📦 Dependencies

```txt
pandas
numpy
f1-22-telemetry
```

---

## 💡 Future Extensions

- Real-time race event classification (e.g., overtakes, off-track incidents).
- Integration with LLM-based race commentators.
- Anomaly detection (mechanical failures, performance drops).
- Event timestamp synchronization with race footage.

---

## 🧠 Author Notes

This module is designed for performance and reliability. It prepares telemetry data for the future of AI in racing — enabling commentary, feedback, and coaching with structured, story-ready data.

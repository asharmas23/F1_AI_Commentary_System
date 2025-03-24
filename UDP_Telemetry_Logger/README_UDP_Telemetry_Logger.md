# UDP Telemetry Logger

The **UDP Telemetry Logger** is a core module of the F1 AI Commentary System that captures and stores real-time telemetry data from the F1 22 game using its UDP data stream.

---

## 🌍 Overview

### 🔧 Purpose
To collect structured, multi-driver telemetry data emitted by the F1 22 game over UDP, and log it efficiently into categorized CSV files for future analysis, dashboard visualization, or AI processing.

---


### ✅ **Background & Motivation**
Modern racing simulators like F1 22 emit a rich stream of real-time telemetry via UDP. Capturing this data accurately and efficiently is crucial for post-race analysis, driver performance reviews, and powering AI commentary systems.

### ✅ **Design Goals**
Build a robust and extensible logging system that:
- Listens to real-time UDP data packets.
- Differentiates and processes multiple telemetry packet types (car status, lap data, motion, etc.).
- Saves data in a structured, per-driver, per-session format.
- Ensures low latency and minimal resource usage during gameplay.

### ✅ **How It Works**
- Implemented a multi-driver logging system in `telemetry_logger_multiple_driver.py`.
- Automatically detects session details (track, timestamp, driver name).
- Categorizes telemetry data by packet type.
- Stores each type in separate CSV files inside a race session folder (`Data/TrackName_Date_Timestamp/`).
- Organizes driver-specific data inside named folders like `AI_TrackName_DriverName_Timestamp`.
- Performs real-time file flushing to reduce memory load and avoid crashes during long races.
- Deletes temporary or incorrectly named folders on exit using intelligent cleanup logic.

### ✅ **Impact & Outcomes**
- Achieved reliable, efficient, and extensible telemetry logging.
- Enabled seamless integration with dashboards and AI analysis pipelines.
- Reduced delivery time for insights, enhanced traceability, and eliminated redundant data processing.

---

## ⚙️ Implementation Details

### 🔁 Main Script
- `telemetry_logger_multiple_driver.py`: Entry-point script for real-time data logging.
  - Listens to UDP telemetry on a specified port.
  - Processes all known F1 22 packet types.
  - Supports:
    - Driver name & track detection.
    - Real-time data categorization.
    - Per-driver folder management.
    - Session-level metadata handling.

### 📁 Directory Structure

```bash
Data/
├── TrackName_Date_Timestamp/
│   ├── session_data.csv
│   ├── event_data.csv
│   ├── AI_TrackName_DRIVERNAME_Timestamp/
│   │   ├── car_status.csv
│   │   ├── car_telemetry.csv
│   │   ├── motion_data.csv
│   │   ├── lap_data.csv
│   │   ├── car_damage.csv
│   │   └── session_history.csv
```

### 🧠 Special Features

- **Real-Time Logging** with Flush:
  - Avoids memory buildup during long races.
- **Smart Folder Naming**:
  - Auto-names using detected driver and track metadata.
- **Error Handling & Cleanup**:
  - Deletes incomplete folders like `UnknownDriver` or invalid double underscores on exit.
- **One-Time Writes**:
  - Avoids writing session-wide CSVs multiple times to improve performance.

---

## 🚀 How to Use

1. Start F1 22 and ensure telemetry is enabled in-game.
2. Run the logger:

```bash
python telemetry_logger_multiple_driver.py
```

3. Telemetry will be logged automatically while the game runs.

4. Use `Ctrl+C` to safely exit after the session. Cleanup will be handled automatically.

---

## 📦 Dependencies

Install required packages:

```bash
pip install -r requirements.txt
```

---

## 📈 Output Usage

- Visualize the logged data using the F1 AI Dashboard.
- Feed into the Event Detection pipeline for generating structured race events.
- Export to other analytics or ML pipelines for insights or coaching.

---

## 📁 Coming Next

- Support for F1 23 telemetry.
- Optional JSON output format.
- Integration with real-time commentary generation.

---

## 🧠 Author Notes

This module is foundational to building a multi-modal racing analytics toolchain. It focuses heavily on structured data pipelines, extensibility, and performance during real-time gameplay.

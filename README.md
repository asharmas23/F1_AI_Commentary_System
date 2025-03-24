# F1 AI Commentary System

The **F1 AI Commentary System** is an integrated pipeline that provides real-time and post-race analysis for the **F1 22** racing game, leveraging telemetry data captured via UDP, interactive dashboards, and advanced event detection methods to facilitate AI-generated commentary and insights.

---

## Modules

### 1. UDP Telemetry Logger
- **Purpose:**
  - Captures real-time telemetry data emitted by the **F1 22** game via UDP.
  - Organizes and stores telemetry data into structured CSV files.

- **Key Features:**
  - Real-time UDP data collection for multiple telemetry message types (`carDamage`, `carStatus`, `carTelemetry`, `lapData`, `motionData`, `eventData`, `sessionData`, etc.).
  - Data organized per driver and session.
  - Efficient logging to minimize resource usage during gameplay.

- **Usage:**
  - Refer to [UDP Telemetry Logger README](UDP_Telemetry_Logger/README.md) for setup and execution details.

---

### 2. F1 AI Dashboard
- **Purpose:**
  - Provides an interactive visualization dashboard built using **Dash, Plotly, and Flask**.
  - Visualizes telemetry data from live UDP streams or pre-recorded CSV data.

- **Key Features:**
  - Two visualization modes:
    - **Real-Time Mode**: Direct visualization of live telemetry streams.
    - **Log Mode**: Visualization of historical data recorded via UDP Logger.
  - Dynamic driver selection for viewing individual telemetry data.
  - Real-time graphical analysis (speed, tire temperatures, throttle/brake usage, G-forces, etc.) with rolling data windows.

- **Usage:**
  - Detailed instructions available in [F1 AI Dashboard README](F1_AI_Dashboard_OOP/README.md).

---

### 3. Event Detection Telemetry Pipeline
- **Purpose:**
  - Parses and processes telemetry data to identify key racing events and generates structured JSON output.
  - Designed for efficient real-time performance using multi-threading.
  - Data prepared by this pipeline is optimized for consumption by Large Language Models (LLMs) for commentary generation.

- **Key Features:**
  - Real-time telemetry parsing and filtering by message type and individual drivers.
  - Structured JSON output optimized for AI model consumption.
  - Multi-threaded implementation ensures high-performance and low latency.

- **Usage:**
  - For detailed usage instructions, refer to [Event Detection Telemetry Pipeline README](event_detection_telemetry/README.md).

---

## Coming Soon

### LLM Commentary Module
- An advanced commentary generation module utilizing Large Language Models (LLMs).
- Will provide dynamic, real-time race commentary and performance analysis based on parsed telemetry and event detection data.

Stay tuned for updates!

---

## Setup & Installation

### Prerequisites
- Python 3.8 or later
- Dependencies listed in each module's `requirements.txt`

### Installation

```bash
git clone https://github.com/yourusername/F1_AI_Commentary_System.git
cd F1_AI_Commentary_System

# Install dependencies for each module
pip install -r UDP_Telemetry_Logger/requirements.txt
pip install -r F1_AI_Dashboard_OOP/requirements.txt
pip install -r event_detection_telemetry/requirements.txt
```

### Running the Project
 - Detailed execution instructions are provided within each module's individual README files.

### Contribution
 - Contributions and improvements are welcome! Please fork the repository and create pull requests with detailed explanations of your changes.

### License
 - This project is licensed under the MIT License - see the LICENSE file for details.
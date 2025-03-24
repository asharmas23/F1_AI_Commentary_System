# F1 AI Dashboard (OOP)

The **F1 AI Dashboard** module is a fully interactive telemetry visualization system built with **Dash**, **Plotly**, and **Flask**, designed to display live or recorded telemetry data from the F1 22 game.

---

## 🌍 Overview

### 🔧 Purpose
To provide an intuitive, responsive dashboard interface for analyzing and comparing telemetry data from multiple drivers in real-time or using recorded race data.

---


### ✅ **Background & Motivation**
With real-time telemetry captured from F1 22, there is a need for an accessible way to visualize data such as speed, tire temps, G-forces, and throttle/brake usage for both live races and past sessions.

### ✅ **Design Goals**
Design and implement a responsive dashboard that:
- Supports two data modes (Live via UDP, or from CSV logs).
- Handles multi-driver telemetry data.
- Offers real-time updates at race pace (30Hz).
- Visualizes key performance metrics with dynamic controls.

### ✅ **How It Works**
- Created a multi-page Dash web app using an OOP structure.
- Added real-time telemetry streaming via UDP as well as log file playback.
- Designed a dynamic driver list so users can choose whose telemetry to view.
- Implemented rolling 5-second plots to mirror live data feel.
- Structured views for:
  - Speed and RPM
  - Throttle and Brake Overlay
  - Tire Temperatures
  - G-Forces
  - Gear and Engine Stats
- Maintained a consistent UI using Bootstrap components for readability and responsiveness.

### ✅ **Impact & Outcomes**
- Delivered a responsive, user-friendly telemetry dashboard.
- Enabled both real-time and post-race data analysis.
- Created a base for extending toward AI-powered coaching and performance insights.

---

## ⚙️ Implementation Details

### 🧩 Key Components
- `app.py`: Core Dash app setup and layout manager.
- `pages/`: Contains modular Dash pages for different telemetry views.
- `callbacks/`: Houses callback functions for updating graphs based on data source and driver selection.
- `assets/`: CSS and static files for styling.

### 📈 Visualization Features

- **Throttle & Brake Graph** – Overlay showing driver input.
- **Tire Temperature** – Per tire temps over time.
- **Speed & Gear Display** – RPM, gear shift patterns, and acceleration.
- **G-Force Analysis** – Real-time G-force plotting.
- **Live UDP vs Log Mode** – Toggle between real-time stream and historical playback.

---

## 🚀 How to Use

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python app.py
```

### 3. Open your browser and navigate to:

```
http://127.0.0.1:8050/
```

- Switch between **Live** and **Log** mode in the UI.
- Select a driver from the sidebar to visualize their telemetry data.

---

## 📂 Directory Structure

```bash
F1_AI_Dashboard_OOP/
├── app.py
├── assets/
├── pages/
├── callbacks/
├── utils/
├── requirements.txt
└── README.md
```

---

## 💡 Highlights

- **Rolling Graphs**: Real-time updates at 30 FPS with fixed time windows.
- **Driver Selection**: Dynamic dropdown generated from active participants.
- **Modular Design**: OOP-based code structure allows easy extensibility.
- **Lightweight Backend**: Minimal CPU/GPU load, suitable for live gameplay analysis.

---

## 🧠 Coming Soon

- Integrated AI Coaching Insights.
- Sector comparison mode.
- Auto-highlight anomalies (e.g., brake lockups, tire overheating).

---

## 🛠 Dependencies

```txt
dash
plotly
flask
pandas
numpy
dash-bootstrap-components
```

---

## 🧠 Author Notes

This module bridges data and visuals, providing a racing engineer-style view of the telemetry. It's modular and efficient for building further into AI coaching and feedback loops.


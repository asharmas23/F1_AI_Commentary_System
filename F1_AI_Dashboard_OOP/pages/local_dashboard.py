import dash
from dash import dcc, html, callback, Input, Output, State, ctx
import plotly.graph_objs as go
import pandas as pd
import os
import dash_bootstrap_components as dbc

from pages.top_bar import top_bar  # Import top navigation bar

dash.register_page(__name__, path="/local_dashboard")

# Global dictionaries to manage session playback positions & fixed y-axis ranges
playback_position = {}
fixed_ranges = {}

# UI Layout
layout = html.Div([
    top_bar(),  # Navigation Bar

    # Race Session Selection
    html.Div([
        html.Label("Select a Race Session:", style={"font-weight": "bold"}),
        dcc.Dropdown(id="session-dropdown", placeholder="Select a race session", style={"width": "60%"}),
    ], style={"display": "flex", "justify-content": "center", "margin-bottom": "20px"}),

    html.Div([
        # Left Pane: Driver List
        html.Div(id="driver-list", style={
            "width": "10%",  
            "height": "85vh",
            "overflowY": "auto",
            "borderRight": "2px solid #ccc",
            "padding": "10px"
        }),

        # Main Content: Title & Graphs
        html.Div([
            html.H1(id="driver-title", children="Driver Telemetry", 
                    style={"textAlign": "center", "fontSize": "32px", "fontWeight": "bold", "marginBottom": "20px"}),

            dcc.Graph(id="speed-graph"),
            dcc.Graph(id="throttle-brake-graph"),
            dcc.Graph(id="gear-graph"),
            dcc.Graph(id="rpm-graph"),
            dcc.Graph(id="gforce-graph"),
            dcc.Graph(id="tire-temp-graph"),
        ], style={"width": "90%", "padding": "10px"})
    ], style={"display": "flex"}),

    dcc.Interval(id="interval-component", interval=200, n_intervals=0),  # 10 FPS (100ms interval)

    # Store Selected Driver & Timestamp
    dcc.Store(id="selected-driver"),
    dcc.Store(id="selected-folder-path"),
    dcc.Store(id="last-timestamp", data=0)
])

# ✅ Load Available Race Sessions with Debugging
@callback(
    Output("session-dropdown", "options"),
    Input("selected-folder-path", "data"),  
    prevent_initial_call=True
)
def load_sessions(data_folder):
    if not data_folder or not os.path.exists(data_folder):
        print("🚨 Error: Invalid or missing data folder:", data_folder)  # Debugging
        return []

    print("✅ Loading sessions from:", data_folder)  # Debugging

    sessions = sorted([f for f in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, f))])
    
    if not sessions:
        print("🚨 No race sessions found in:", data_folder)  # Debugging
        return []
    
    return [{"label": session, "value": session} for session in sessions]

# ✅ Load Available Drivers with Centered Text
@callback(
    Output("driver-list", "children"),
    Input("session-dropdown", "value"),
    State("selected-folder-path", "data"),
    prevent_initial_call=True
)
def load_drivers(selected_session, data_folder):
    if not selected_session or not data_folder:
        return "No drivers found."

    session_path = os.path.join(data_folder, selected_session)
    drivers = sorted([f for f in os.listdir(session_path) if os.path.isdir(os.path.join(session_path, f))])

    num_drivers = len(drivers)
    top_bar_height = 100  # Approximate height of the top bar (adjust if needed)
    total_available_height = "calc(85vh - {}px)".format(top_bar_height)  # Dynamically calculate remaining height

    button_height = f"calc({total_available_height} / {max(num_drivers, 1)})"  # Divide available height equally

    driver_buttons = [
        dbc.Button(
            driver.split("_")[3][:3], 
            id={"type": "driver-button", "index": driver}, 
            color="dark", 
            outline=True, 
            className="w-100 mb-1",
            style={
                "height": button_height, 
                "min-height": "5px",
                "display": "flex",  # Enables flexbox for alignment
                "align-items": "center",  # Centers vertically
                "justify-content": "center",  # Centers horizontally
                "text-align": "center",  # Ensures text is centered
                "font-weight": "bold",  # Makes text bold for better visibility
                "padding": "5px"  # Adds padding for better readability
            }
        )
        for driver in drivers
    ]
    
    return driver_buttons



# ✅ Select Driver (Triggers Data Loading)
@callback(
    [Output("selected-driver", "data"),
     Output("last-timestamp", "data"),  
     Output("driver-title", "children")],  
    Input({"type": "driver-button", "index": dash.ALL}, "n_clicks"),
    State({"type": "driver-button", "index": dash.ALL}, "id"),
    State("last-timestamp", "data"),
    prevent_initial_call=True
)
def update_selected_driver(n_clicks, driver_ids, last_timestamp):
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "driver-button":
        selected_driver = triggered_id["index"]
        full_name = selected_driver.split("_")[3]  
        return selected_driver, last_timestamp, f"Driver Telemetry - {full_name}"
    
    return dash.no_update, dash.no_update, dash.no_update

# ✅ Update All Graphs with x FPS Rolling Window
@callback(
    [Output("speed-graph", "figure"),
     Output("throttle-brake-graph", "figure"),
     Output("gear-graph", "figure"),
     Output("rpm-graph", "figure"),
     Output("gforce-graph", "figure"),
     Output("tire-temp-graph", "figure")],
    [Input("selected-driver", "data"),
     Input("interval-component", "n_intervals")],
    [State("selected-folder-path", "data"), State("session-dropdown", "value")],
    prevent_initial_call=True
)
def update_graphs(selected_driver, n, data_folder, selected_session):
    if not selected_driver or not selected_session or not data_folder:
        return [go.Figure() for _ in range(6)]

    motion_data, telemetry_data = load_driver_data(data_folder, selected_session, selected_driver)

    if motion_data.empty or telemetry_data.empty:
        return [go.Figure() for _ in range(6)]

    telemetry_data["timestamp"] = pd.to_numeric(telemetry_data["timestamp"], errors="coerce")
    motion_data["timestamp"] = pd.to_numeric(motion_data["timestamp"], errors="coerce")

    min_time, max_time = telemetry_data["timestamp"].min(), telemetry_data["timestamp"].max()

    # Rolling playback position
    playback_position[selected_session] = playback_position.get(selected_session, min_time) + 0.1
    if playback_position[selected_session] >= max_time:
        playback_position[selected_session] = min_time

    window_start, window_end = playback_position[selected_session], playback_position[selected_session] + 5

    # Filter rolling window
    telemetry_data = telemetry_data[(telemetry_data["timestamp"] >= window_start) & (telemetry_data["timestamp"] <= window_end)]
    motion_data = motion_data[(motion_data["timestamp"] >= window_start) & (motion_data["timestamp"] <= window_end)]

    return create_graphs(telemetry_data, motion_data, window_start, window_end)

# ✅ Function to Load Driver Data
def load_driver_data(data_folder, session, driver):
    driver_path = os.path.join(data_folder, session, driver)
    
    motion_file = os.path.join(driver_path, "motion_data.csv")
    telemetry_file = os.path.join(driver_path, "car_telemetry.csv")

    if not os.path.exists(motion_file) or not os.path.exists(telemetry_file):
        return pd.DataFrame(), pd.DataFrame()

    motion_data = pd.read_csv(motion_file)
    telemetry_data = pd.read_csv(telemetry_file)

    return motion_data, telemetry_data

# ✅ Function to Generate Multi-Line Graphs with Fixed Y-Axis Ranges
def create_graphs(telemetry_data, motion_data, window_start, window_end):
    if telemetry_data.empty or motion_data.empty:
        return [go.Figure() for _ in range(6)]  # Return empty figures to prevent callback errors

    # ✅ Define Fixed Y-Axis Ranges
    y_ranges = {
        "speed": [0, 375],  # Speed (0 to 350 km/h)
        "throttle": [-0.1, 1.1],  # Throttle (0 to 1)
        "brake": [-0.1, 1.1],  # Brake (0 to 1)
        "gear": [-1.1, 8.1],  # Gear (-1 for reverse, 0-8 for normal gears)
        "rpm": [0, 15000],  # RPM (0 to 15,000)
        "gforce": [-5, 5],  # G-Force (-5 to 5)
        "tire_temp": [50, 140]  # Tire Temperature (50°C to 150°C)
    }

    # Speed Graph
    speed_fig = go.Figure()
    speed_fig.add_trace(go.Scatter(x=telemetry_data['timestamp'], y=telemetry_data['speed_kmh'], mode='lines+markers', name='Speed'))
    speed_fig.update_layout(title='Speed (km/h)', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["speed"]))

    # Throttle & Brake Graph (Two Lines)
    tb_fig = go.Figure()
    tb_fig.add_trace(go.Scatter(x=telemetry_data['timestamp'], y=telemetry_data['throttle'], mode='lines+markers', name='Throttle', line=dict(color='green')))
    tb_fig.add_trace(go.Scatter(x=telemetry_data['timestamp'], y=telemetry_data['brake'], mode='lines', name='Brake', line=dict(color='red')))
    tb_fig.update_layout(title='Throttle & Brake', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["throttle"]))

    # Gear Graph
    gear_fig = go.Figure()
    gear_fig.add_trace(go.Scatter(x=telemetry_data['timestamp'], y=telemetry_data['gear'], mode='lines+markers', name='Gear'))
    gear_fig.update_layout(title='Gear Changes', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["gear"]))

    # Engine RPM Graph
    rpm_fig = go.Figure()
    rpm_fig.add_trace(go.Scatter(x=telemetry_data['timestamp'], y=telemetry_data['engine_rpm'], mode='lines+markers', name='RPM'))
    rpm_fig.update_layout(title='Engine RPM', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["rpm"]))

    # G-Force Graph (Three Lines for Lateral, Longitudinal, Vertical)
    gforce_fig = go.Figure()
    for force in ['g_force_lateral', 'g_force_longitudinal', 'g_force_vertical']:
        gforce_fig.add_trace(go.Scatter(x=motion_data['timestamp'], y=motion_data[force], mode='lines+markers', name=force))
    gforce_fig.update_layout(title='G-Forces', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["gforce"]))

    # Tire Temperature Graph (Four Lines for Each Tire)
    tire_temp_fig = go.Figure()
    tire_colors = ['blue', 'orange', 'green', 'red']  # Assign unique colors to each tire
    tires = ['tire_temp_FL', 'tire_temp_FR', 'tire_temp_RL', 'tire_temp_RR']
    
    for i, tire in enumerate(tires):
        if tire in telemetry_data.columns:
            tire_temp_fig.add_trace(go.Scatter(
                x=telemetry_data['timestamp'], 
                y=telemetry_data[tire], 
                mode='lines+markers', 
                name=tire, 
                line=dict(color=tire_colors[i])
            ))
    
    tire_temp_fig.update_layout(title='Tire Temperatures', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["tire_temp"]))

    return speed_fig, tb_fig, gear_fig, rpm_fig, gforce_fig, tire_temp_fig

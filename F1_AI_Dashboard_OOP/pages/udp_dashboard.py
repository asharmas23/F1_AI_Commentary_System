import dash
from dash import dcc, html, callback, Input, Output, State, ctx
import plotly.graph_objs as go
import threading
import dash_bootstrap_components as dbc
from f1_22_telemetry.listener import TelemetryListener
from f1_22_telemetry.packets import *
from pages.top_bar import top_bar
from collections import deque
import socket
import time
import numpy as np
import pandas as pd

dash.register_page(__name__, path="/udp-dashboard")

# Global variables
listener = None
udp_thread = None
running = False
driver_names = {}  # Stores {driver_index: driver_name}

# Global variables
rate = 10
buffer_size = 5 * rate  # Rolling window of 5 seconds
motion_columns=[
        "timestamp", "pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z", 
        "g_force_lateral", "g_force_longitudinal", "g_force_vertical"
    ]
motion_data = np.empty((buffer_size,len(motion_columns)), dtype=object)  # Stores latest motion data
motion_index = 0  # Tracks current insertion index
telem_columns=[
        "timestamp", "speed_kmh", "throttle", "brake", "gear", "engine_rpm",  #"drs",
        "tire_temp_FL", "tire_temp_FR", "tire_temp_RL", "tire_temp_RR"
    ]
telem_data = np.empty((buffer_size,len(telem_columns)), dtype=object)  # Stores latest telemetry data
telem_index = 0 
selected_driver_index = 0  # Set to correct driver index

def reset_data():
    global buffer_size, motion_columns, motion_data, motion_index, telem_columns, telem_data, telem_index
    del motion_data, telem_data
    motion_data = np.empty((buffer_size,len(motion_columns)), dtype=object)
    telem_data = np.empty((buffer_size,len(telem_columns)), dtype=object)
    motion_index = 0
    telem_index = 0


layout = html.Div([
    top_bar(),

    html.Div([
        dbc.Button("Start Streaming", id="udp-control", color="success"),
    ], style={"textAlign": "center", "margin-bottom": "20px"}),

    html.Div([
        # Left Pane: Driver List
        html.Div(id="udp-driver-list", style={
            "width": "10%",
            "height": "85vh",
            "overflowY": "auto",
            "borderRight": "2px solid #ccc",
            "padding": "10px"
        }),

        # Main Content: Title & Graphs
        html.Div([
            html.H1(id="udp-driver-title", children="Driver Telemetry",
                    style={"textAlign": "center", "fontSize": "32px"}),

            dcc.Graph(id="udp-speed-graph"),
            dcc.Graph(id="udp-throttle-brake-graph"),
            dcc.Graph(id="udp-gear-graph"),
            dcc.Graph(id="udp-rpm-graph"),
            dcc.Graph(id="udp-gforce-graph"),  # ✅ Added missing graph
            dcc.Graph(id="udp-tire-temp-graph"),  # ✅ Added missing graph
        ], style={"width": "90%", "padding": "10px"})
    ], style={"display": "flex"}),

    dcc.Interval(id="udp-interval-component", interval=200, n_intervals=0),
    dcc.Store(id="udp-selected-driver"),
])

def udp_listener(ip, port):
    """Listens for F1 22 telemetry and updates driver data."""
    global running, listener, rate, selected_driver_index

    try:
        port = int(port)  # ✅ Ensure port is an integer
        listener = TelemetryListener(host=ip, port=port)
        print(f"✅ Started UDP Listener on {ip}:{port}")

        while running:
            try:
                packet = listener.get()

                # ✅ Extract driver names (filter out empty entries)
                if isinstance(packet, PacketParticipantsData):
                    for i, participant in enumerate(packet.participants):
                        driver_name = participant.name.decode("utf-8").strip()
                        if driver_name:
                            driver_names[i] = driver_name  # ✅ Only store non-empty names

                global motion_data, motion_index, buffer_size, telem_data, telem_index
                timestamp = packet.header.session_time  # Common timestamp for all packets

                if isinstance(packet, PacketMotionData): 
                    for i, player in enumerate(packet.car_motion_data):
                        if i == selected_driver_index:
                            data_row = [timestamp, player.world_position_x, player.world_position_y, player.world_position_z,
                                        player.world_velocity_x, player.world_velocity_y, player.world_velocity_z,
                                        player.g_force_lateral, player.g_force_longitudinal, player.g_force_vertical]
                            
                            # Store data in the circular buffer
                            motion_data[motion_index % buffer_size] = data_row
                            
                            # Update index (ensures rolling behavior)
                            motion_index += 1
                    # print("Motion!")

                if isinstance(packet, PacketCarTelemetryData):
                    for i, player in enumerate(packet.car_telemetry_data):
                        if i == selected_driver_index:
                            data_row = [timestamp, player.speed, player.throttle, player.brake, player.gear,
                                        player.engine_rpm, #"Active" if player.drs else "Inactive",
                                        player.tyres_surface_temperature[0], player.tyres_surface_temperature[1],
                                        player.tyres_surface_temperature[2], player.tyres_surface_temperature[3]]
                            
                            # Store data in the circular buffer
                            telem_data[telem_index % buffer_size] = data_row
                            
                            # Update index (ensures rolling behavior)
                            telem_index += 1
                    # print("Telemetry!")

                # time.sleep(0.2)  # ✅ Force continuous updates based on FPS

            except Exception as e:
                print(f"⚠️ UDP Error: {e}")

        print("✅ UDP Listener stopped successfully.")

    except OSError as e:
        print(f"🚨 Socket Error: {e}")

    finally:
        running = False
        try:
            if listener and hasattr(listener, "socket"):
                listener.socket.close()
                print("✅ UDP Socket Closed")
        except Exception as e:
            print(f"⚠️ Error closing socket: {e}")

        time.sleep(1)



@callback(
    Output("udp-control", "children"),
    Input("udp-control", "n_clicks"),
    State("udp-config", "data"),
    prevent_initial_call=True
)
def toggle_udp(n_clicks, udp_config):
    global udp_thread, running, rate

    if not udp_config:
        print("🚨 Error: udp_config is None. Ensure settings are configured.")
        return "Start Streaming"

    ip = udp_config.get("ip", "127.0.0.1")
    port = udp_config.get("port", 20777)
    rate = int(udp_config.get("rate", 30))

    if running:
        print("⚠️ Stopping existing UDP listener...")
        running = False  # ✅ Stop listener

        if udp_thread and udp_thread.is_alive():
            udp_thread.join(timeout=3)  # ✅ Wait max 3 sec to stop
            if udp_thread.is_alive():
                print("🚨 Forcefully terminating UDP thread...")
                udp_thread = None  # ✅ Reset thread reference

        time.sleep(1)  # ✅ Ensure the socket is released before restarting

        return "Start Streaming"

    # ✅ Ensure `running` is reset before restarting
    running = True

    print(f"✅ Starting new UDP listener on {ip}:{port}...")
    udp_thread = threading.Thread(target=udp_listener, args=(ip, port), daemon=True)
    udp_thread.start()

    return "Stop Streaming"


@callback(
    Output("udp-driver-list", "children"),
    Input("udp-interval-component", "n_intervals"),
    prevent_initial_call=True
)
def update_driver_list(n):
    """Dynamically updates the driver list, removing empty drivers."""
    if not driver_names:
        return "No drivers available."

    # ✅ Create dynamic driver buttons (only for valid drivers)
    driver_buttons = [
        dbc.Button(driver_name[:3], id={"type": "udp-driver-button", "index": i},  
                   color="dark", outline=True, className="w-100 mb-1")
        for i, driver_name in driver_names.items() if driver_name  # ✅ Ignore empty drivers
    ]
    return driver_buttons


@callback(
    Output("udp-selected-driver", "data"),
    Output("udp-driver-title", "children"),
    [Input("udp-driver-list", "children"),  # ✅ Auto-select first valid driver
     Input({"type": "udp-driver-button", "index": dash.ALL}, "n_clicks")],  # ✅ Allow manual selection
    State("udp-selected-driver", "data"),
    prevent_initial_call=True
)
def select_driver(driver_list, n_clicks, current_driver):
    global selected_driver_index
    """Auto-selects the first driver initially, but allows manual selection."""
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update, dash.no_update

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # ✅ Manual Selection: Prioritize button clicks
    if "udp-driver-button" in triggered_id:
        driver_index = eval(triggered_id)["index"]

        if driver_index not in driver_names:
            return dash.no_update, "No Driver Selected"

        selected_driver_index = driver_index
        reset_data()
        driver_name = driver_names[driver_index]
        print(f"✅ User Selected Driver: {driver_name}")

        return driver_index, f"Driver Telemetry - {driver_name}"

    # ✅ Auto-Selection: Only run if no driver is selected yet
    elif triggered_id == "udp-driver-list" and current_driver is None:
        valid_drivers = {i: name for i, name in driver_names.items() if name}  # ✅ Ignore empty drivers
        if not valid_drivers:
            return dash.no_update, "No Driver Selected"

        first_driver_index = next(iter(valid_drivers.keys()))
        first_driver_name = valid_drivers[first_driver_index]

        print(f"✅ Auto-Selected Driver: {first_driver_name}")
        return first_driver_index, f"Driver Telemetry - {first_driver_name}"

    return dash.no_update, dash.no_update

@callback(
    [Output("udp-speed-graph", "figure"),
     Output("udp-throttle-brake-graph", "figure"),
     Output("udp-gear-graph", "figure"),
     Output("udp-rpm-graph", "figure"),
     Output("udp-gforce-graph", "figure"),
     Output("udp-tire-temp-graph", "figure")],
    [Input("udp-selected-driver", "data"),
     Input("udp-interval-component", "n_intervals")],
    prevent_initial_call=True
)
def update_graphs(selected_driver, n):
    # """Fetch latest telemetry data & update graphs in real-time."""
    # print(f"📊 Dash Callback Triggered: update_graphs() - Interval: {n}")  # Debug print
    
    global motion_data, telem_data, motion_index, telem_index, buffer_size
    # print(motion_data.shape, telem_data.shape)
    
    # print(motion_data)
    if len(motion_data) == 0 or len(telem_data) == 0:
        print("⚠️ No telemetry data available yet!")
        return [go.Figure() for _ in range(6)]  # Empty figures
    
    # ✅ Reconstruct ordered data
    valid_motion_size = min(motion_index, buffer_size)
    ordered_motion_data = np.roll(motion_data, -motion_index % buffer_size, axis=0)[:valid_motion_size]

   # ✅ Reconstruct Telemetry ordered data
    valid_telem_size = min(telem_index, buffer_size)
    ordered_telem_data = np.roll(telem_data, -telem_index % buffer_size, axis=0)[:valid_telem_size]

    df_motion = pd.DataFrame(list(ordered_motion_data), columns=[
        "timestamp", "pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z", 
        "g_force_lateral", "g_force_longitudinal", "g_force_vertical"
    ], dtype=float)
    
    df_telem = pd.DataFrame(list(ordered_telem_data), columns=[
        "timestamp", "speed_kmh", "throttle", "brake", "gear", "engine_rpm", #"drs", 
        "tire_temp_FL", "tire_temp_FR", "tire_temp_RL", "tire_temp_RR"
    ], dtype=float)

    return create_graphs(df_motion, df_telem)


# ✅ Function to Generate Multi-Line Graphs with Fixed Y-Axis Ranges
def create_graphs(motion_data, telem_data):
    global buffer_size
    
    if telem_data.empty or motion_data.empty:
        return [go.Figure() for _ in range(6)]  # Return empty figures to prevent callback errors
    
    
    # ✅ Handle window_start and window_end properly
    if not telem_data.empty and "timestamp" in telem_data.columns:
        window_start = int(telem_data['timestamp'].iloc[0]) if pd.notna(telem_data['timestamp'].iloc[0]) else 0
        window_end = int(telem_data['timestamp'].iloc[-1]) if pd.notna(telem_data['timestamp'].iloc[-1]) else window_start + 5
    else:
        window_start, window_end = 0, 5  # Default values if DataFrame is empty

    # print(f"Window Start: {window_start}, Window End: {window_end}")   
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
    speed_fig.add_trace(go.Scatter(x=telem_data['timestamp'], y=telem_data['speed_kmh'], mode='lines+markers', name='Speed'))
    speed_fig.update_layout(title='Speed (km/h)', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["speed"]))


    # Throttle & Brake Graph (Two Lines)
    tb_fig = go.Figure()
    tb_fig.add_trace(go.Scatter(x=telem_data['timestamp'], y=telem_data['throttle'], mode='lines+markers', name='Throttle', line=dict(color='green')))
    tb_fig.add_trace(go.Scatter(x=telem_data['timestamp'], y=telem_data['brake'], mode='lines', name='Brake', line=dict(color='red')))
    tb_fig.update_layout(title='Throttle & Brake', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["throttle"]))
    # Gear Graph
    gear_fig = go.Figure()
    gear_fig.add_trace(go.Scatter(x=telem_data['timestamp'], y=telem_data['gear'], mode='lines+markers', name='Gear'))
    gear_fig.update_layout(title='Gear Changes', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["gear"]))

    # Engine RPM Graph
    rpm_fig = go.Figure()
    rpm_fig.add_trace(go.Scatter(x=telem_data['timestamp'], y=telem_data['engine_rpm'], mode='lines+markers', name='RPM'))
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
        if tire in telem_data.columns:
            tire_temp_fig.add_trace(go.Scatter(
                x=telem_data['timestamp'], 
                y=telem_data[tire], 
                mode='lines+markers', 
                name=tire, 
                line=dict(color=tire_colors[i])
            ))
    
    tire_temp_fig.update_layout(title='Tire Temperatures', xaxis=dict(range=[window_start, window_end]), yaxis=dict(range=y_ranges["tire_temp"]))

    return speed_fig, tb_fig, gear_fig, rpm_fig, gforce_fig, tire_temp_fig





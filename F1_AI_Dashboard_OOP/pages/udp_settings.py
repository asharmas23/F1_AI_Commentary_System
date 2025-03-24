import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from pages.top_bar import top_bar  # Import top bar

class UDPSettingsPage:
    def __init__(self):
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div([
            top_bar(),  # Add top navigation pane
            html.H2("🔧 Configure UDP Telemetry", style={"textAlign": "center", "margin-bottom": "20px"}),

            dcc.Store(id="udp-config", storage_type="session"),  # ✅ Store UDP Configuration persistently

            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Label("UDP IP Address", style={"font-weight": "bold"}), width=4, className="text-end"),
                    dbc.Col(dcc.Input(id="udp-ip", type="text", value="127.0.0.1", className="form-control"), width=8),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(html.Label("UDP Port", style={"font-weight": "bold"}), width=4, className="text-end"),
                    dbc.Col(dcc.Input(id="udp-port", type="number", value="20777", className="form-control"), width=8),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(html.Label("UDP Rate (Hz)", style={"font-weight": "bold"}), width=4, className="text-end"),
                    dbc.Col(dcc.Input(id="udp-rate", type="number", value="30", className="form-control"), width=8),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(html.Label("Format", style={"font-weight": "bold"}), width=4, className="text-end"),
                    dbc.Col(
                        dcc.Dropdown(
                            id="udp-format",
                            options=[
                                {"label": "F1 22 Format", "value": "2022"},
                                {"label": "F1 23 Format", "value": "2023"},
                            ],
                            value="2022",
                            clearable=False,
                            style={"cursor": "pointer"}
                        ),
                        width=8
                    ),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(dbc.Button("Set Credentials", id="start-udp", color="success", className="w-100"), width=8),
                ], className="mt-4"),
            ], fluid=True, style={"maxWidth": "600px", "margin": "auto"}),

            dcc.Location(id="redirect-udp", refresh=True)
        ])

    def register_callbacks(self):
        @callback(
            [Output("udp-config", "data", allow_duplicate=True), Output("redirect-udp", "pathname")],
            Input("start-udp", "n_clicks"),
            [State("udp-ip", "value"),
             State("udp-port", "value"),
             State("udp-rate", "value"),
             State("udp-format", "value")],
            prevent_initial_call=True
        )
        def save_udp_settings(n_clicks, ip, port, rate, format_value):
            if not ip or not port or not rate:
                print("🚨 Error: Missing UDP settings.")
                return dash.no_update, dash.no_update

            try:
                port = int(port)  # ✅ Convert port to integer before saving
            except ValueError:
                print(f"🚨 Error: Invalid port '{port}'. Must be a number.")
                return dash.no_update, dash.no_update

            udp_config = {"ip": ip, "port": port, "rate": rate, "format": format_value}
            print(f"✅ UDP Settings Saved: {udp_config}")
            return udp_config, "/udp-dashboard"

# Register page with Dash
dash.register_page(__name__, path="/udp-settings")

# Create an instance of UDPSettingsPage
udp_settings_page = UDPSettingsPage()
layout = udp_settings_page.layout

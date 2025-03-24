import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import os

from pages.top_bar import top_bar  # Import top bar

class LocalSystemPage:
    def __init__(self):
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div([
            top_bar(),  # Add top navigation pane

            html.H2("📂 Enter F1 22 Data Folder Path", style={"textAlign": "center", "margin-bottom": "20px"}),

            dcc.Store(id="selected-folder-path"),  # ✅ Store Folder Path Globally

            dbc.Container([
                dbc.Row([
                    dbc.Col(html.Label("Folder Path", style={"font-weight": "bold"}), width=4, className="text-end"),
                    dbc.Col(
                        dcc.Input(id="folder-path", type="text", placeholder="Enter folder path...", className="form-control"),
                        width=8
                    ),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(html.Label("Folder Status"), width=4, className="text-end"),
                    dbc.Col(html.Div(id="folder-status", style={"font-style": "italic"}), width=8),
                ], className="mb-3"),

                dbc.Row([
                    dbc.Col(html.Div(), width=4),  # Empty column for alignment
                    dbc.Col(
                        dbc.Button("Start Streaming", id="start-streaming", color="success", className="w-100", disabled=True, href="/local_dashboard"),
                        width=8,
                    ),
                ], className="mt-3"),
            ], fluid=True, style={"maxWidth": "700px", "margin": "auto"})  # Centers form & makes it responsive
        ])

    def register_callbacks(self):
        @callback(
            Output("folder-status", "children"),
            Output("start-streaming", "disabled"),
            Output("selected-folder-path", "data"),  # Store folder path globally
            Input("folder-path", "value"),
            prevent_initial_call=True
        )
        def check_folder(folder_path):
            if not folder_path or not os.path.exists(folder_path):
                return "❌ Invalid folder path", True, None  # Disable button

            num_files = len(os.listdir(folder_path))
            return f"✅ Folder contains {num_files} race sessions. Ready to visualize!", False, folder_path  # Enable button

# Register page with Dash
dash.register_page(__name__, path="/local-system")

# Create an instance of LocalSystemPage
local_system_page = LocalSystemPage()
layout = local_system_page.layout

import dash
import dash_bootstrap_components as dbc
from flask import Flask
from dash import dcc, html

class DashboardApp:
    def __init__(self):
        self.server = Flask(__name__)
        self.app = self._initialize_dash()
        self._set_layout()
    
    def _initialize_dash(self):
        return dash.Dash(
            __name__,
            use_pages=True,
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            suppress_callback_exceptions=True,
            server=self.server
        )
    
    def _set_layout(self):
        self.app.layout = html.Div([
            dcc.Store(id="selected-folder-path"),  # Store folder path globally
            dcc.Store(id="udp-config", storage_type="session"),  # Store UDP Settings globally
            dash.page_container  # Loads pages dynamically
        ])
    
    def run(self, debug=True):
        self.app.run_server(debug=debug)

if __name__ == "__main__":
    dashboard = DashboardApp()
    dashboard.run()

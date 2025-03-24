import dash
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

class HomePage:
    def __init__(self):
        self.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div([
            html.H1("🏎️ F1 22 Telemetry Dashboard", style={"textAlign": "center"}),

            html.Div([
                html.Img(src="https://cdn.pixabay.com/photo/2024/01/18/16/38/ai-generated-8517210_1280.png", style={
        "width": "100%",       # Ensures the image scales to fit the container
        "height": "auto",      # Maintains aspect ratio
        "max-width": "800px",  # Limits the max width to avoid overflow
        "display": "block",    # Centers the image properly
        "margin": "0 auto"     # Centers the image horizontally
    }),
            ], style={"textAlign": "center"}),

            html.Div([
                dbc.Button("UDP", id="udp-btn", color="primary", className="me-2"),
                dbc.Button("Local System", id="local-btn", color="secondary", className="me-2"),
                dbc.Button("F1 Original Historical", id="historical-btn", color="info"),
            ], style={"display": "flex", "justifyContent": "center", "gap": "10px", "margin-top": "20px"}),

            dcc.Location(id="redirect", refresh=True)
        ])

    def register_callbacks(self):
        @callback(
            Output("redirect", "pathname"),
            [Input("udp-btn", "n_clicks"),
             Input("local-btn", "n_clicks"),
             Input("historical-btn", "n_clicks")],
            prevent_initial_call=True
        )
        def navigate(udp_click, local_click, historical_click):
            ctx = dash.callback_context
            if not ctx.triggered:
                return dash.no_update

            button_id = ctx.triggered[0]["prop_id"].split(".")[0]

            if button_id == "udp-btn":
                return "/udp-settings"
            elif button_id == "local-btn":
                return "/local-system"
            elif button_id == "historical-btn":
                return "/historical"

# Register page with Dash
dash.register_page(__name__, path="/")

# Create an instance of HomePage
home_page = HomePage()
layout = home_page.layout

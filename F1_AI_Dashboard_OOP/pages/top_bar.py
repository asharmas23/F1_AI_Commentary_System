from dash import html
import dash_bootstrap_components as dbc

def top_bar():
    return dbc.Navbar(
        dbc.Container([
            # Title with F1 Car Emoji/Icon
            dbc.NavbarBrand([
                html.Img(src="https://cdn-icons-png.flaticon.com/512/2925/2925731.png", 
                         style={"height": "30px", "margin-right": "10px"}),  # Small F1 Car Icon
                html.Span("F1 22 Telemetry Dashboard", 
                          style={"font-size": "32px", "font-weight": "bold", "color": "white"})
            ], className="d-flex align-items-center", style={"margin-right": "20px"}),

            # Navigation Buttons
            dbc.ButtonGroup([
                dbc.Button("🏁 UDP", href="/udp-settings", color="primary", className="me-2"),
                dbc.Button("📂 Local System", href="/local-system", color="secondary", className="me-2"),
                dbc.Button("📊 F1 Historical", href="/historical", color="info"),
            ]),
        ], fluid=True, className="d-flex justify-content-between"),
        color="dark",  # Dark background
        dark=True,  # White text
        className="mb-4"
    )

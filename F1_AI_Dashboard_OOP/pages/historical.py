import dash
from dash import html
from pages.top_bar import top_bar  # Import top bar

class HistoricalPage:
    def __init__(self):
        self.layout = self.create_layout()

    def create_layout(self):
        return html.Div([
            top_bar(),  # Add top navigation pane
            html.H2("📊 Historical Data Coming Soon!", style={"textAlign": "center", "color": "gray"})
        ])

# Register page with Dash
dash.register_page(__name__, path="/historical")

# Create an instance of HistoricalPage
historical_page = HistoricalPage()
layout = historical_page.layout

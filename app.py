import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import chart_1
import os
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "plotly_dark"

# Initialize the Dash app using the DARKLY theme.
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Strength Comparison Calculator", 
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
)

server = app.server

app.layout = html.Div(
    style={'padding': '20px'},
    children=[
        html.H1("Strength Comparison Calculator", style={'textAlign': 'center'}),
        # Lifter 1 Controls (first row)
        html.Div([
            html.Label("Lifter 1:"),
            dbc.RadioItems(
                id='lifter1-gender',
                options=[
                    {"label": "Male", "value": "Male"},
                    {"label": "Female", "value": "Female"}
                ],
                value="Female",
                inline=True
            ),
            html.Br(),
            html.Label("Weight (lbs):"),
            dcc.Slider(
                id='lifter1-weight-slider',
                min=100,
                max=400,
                step=1,
                value=170,
                marks={i: str(i) for i in range(100, 401, 50)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'margin-bottom': '20px'}),
        # Lifter 2 Controls (second row)
        html.Div([
            html.Label("Lifter 2:"),
            dbc.RadioItems(
                id='lifter2-gender',
                options=[
                    {"label": "Male", "value": "Male"},
                    {"label": "Female", "value": "Female"}
                ],
                value="Male",
                inline=True
            ),
            html.Br(),
            html.Label("Weight (lbs):"),
            dcc.Slider(
                id='lifter2-weight-slider',
                min=100,
                max=400,
                step=1,
                value=225,
                marks={i: str(i) for i in range(100, 401, 50)},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'margin-bottom': '20px'}),
        dcc.Graph(
            id='dots-chart',
            config={
                'displayModeBar': False,
                'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d'],
                'doubleClick': False,
                'scrollZoom': False
            }
        ),
        # Hidden store to hold the screen width.
        dcc.Store(id='screen-width', data=1024),
        # Interval component to trigger the clientside callback (runs once on load).
        dcc.Interval(id='interval-component', interval=1000, n_intervals=0, max_intervals=1)
    ]
)

# Clientside callback to capture the window's innerWidth.
app.clientside_callback(
    """
    function(n_intervals) {
        return window.innerWidth;
    }
    """,
    Output('screen-width', 'data'),
    Input('interval-component', 'n_intervals')
)

@app.callback(
    Output('dots-chart', 'figure'),
    [
        Input('dots-chart', 'hoverData'),
        Input('dots-chart', 'clickData'),
        Input('lifter1-weight-slider', 'value'),
        Input('lifter2-weight-slider', 'value'),
        Input('lifter1-gender', 'value'),
        Input('lifter2-gender', 'value'),
        Input('screen-width', 'data')
    ]
)
def update_chart(hoverData, clickData, lifter1_weight, lifter2_weight, lifter1_gender, lifter2_gender, screen_width):
    # Generate the base figure.
    fig = chart_1.create_chart(
        lifter1_bodyweight=lifter1_weight,
        lifter1_gender=lifter1_gender,
        lifter2_bodyweight=lifter2_weight,
        lifter2_gender=lifter2_gender
    )

    # Use clickData if hoverData is None (common on mobile).
    eventData = hoverData if hoverData is not None else clickData
    annotation_text = "Tap a point to see details."  # default text
    if eventData is not None and 'points' in eventData:
        try:
            annotation_text = eventData['points'][0].get('customdata', annotation_text)
        except Exception as e:
            print("Error extracting annotation text:", e)

    # Dynamically scale annotation font size and box width based on screen width
    max_font_size = 18
    min_font_size = 8
    annotation_font_size = max(min_font_size, min(max_font_size, screen_width * 0.02))  # Scale with screen width

    max_box_width_px = 400  # Max 400 pixels wide
    min_box_width_px = 150  # Min 150 pixels wide
    annotation_box_width_px = max(min_box_width_px, min(max_box_width_px, screen_width * 0.4))  # Scale width

    # Update layout with a fixed annotation at 90% of the plot height, centered horizontally.
    fig.update_layout(
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=0.5,  # Centered horizontally
            y=0.9,  # Near the top
            text=annotation_text,
            showarrow=False,
            font=dict(size=annotation_font_size, color='white'),
            bgcolor='rgba(0, 0, 0, 0.5)',
            bordercolor='white',
            borderwidth=1,
            borderpad=2,
            align='center',
            xanchor='center',
            width=int(annotation_box_width_px)  # Convert to integer pixels
        )]
    )
    
    return fig



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)

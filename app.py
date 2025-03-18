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
        )


    ]
)



@app.callback(
    Output('dots-chart', 'figure'),
    [
        Input('dots-chart', 'hoverData'),
        Input('lifter1-weight-slider', 'value'),
        Input('lifter2-weight-slider', 'value'),
        Input('lifter1-gender', 'value'),
        Input('lifter2-gender', 'value')
    ]
)
def update_chart(hoverData, lifter1_weight, lifter2_weight, lifter1_gender, lifter2_gender):
    # Generate the base figure.
    fig = chart_1.create_chart(
        lifter1_bodyweight=lifter1_weight,
        lifter1_gender=lifter1_gender,
        lifter2_bodyweight=lifter2_weight,
        lifter2_gender=lifter2_gender
    )
    
    # Default annotation text.
    annotation_text = "Hover over a point to see details."
    
    # Debug: Print hoverData to verify data is arriving.
    #print("hoverData:", hoverData['points'])
    

    if hoverData is not None and 'points' in hoverData:
        try:
            # Use 'customdata' to get the stored hover text.
            annotation_text = hoverData['points'][0].get('customdata', annotation_text)
            print(annotation_text)
        except Exception as e:
            print("Error extracting hover text:", e)
    else:
        print("never in points")
    
    # Update layout with a fixed annotation at 90% of the plot height, centered horizontally.
    fig.update_layout(
        annotations=[dict(
            xref='paper',
            yref='paper',
            x=0.5,      # Center horizontally.
            y=0.9,      # 90% of the plot height.
            text=annotation_text,
            showarrow=False,
            font=dict(size=18, color='white'),
            bgcolor='rgba(0, 0, 0, 0.5)',
            bordercolor='white',
            borderwidth=1,
            borderpad=4
        )]
    )
    
    return fig


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)

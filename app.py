import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import chart_1

# Initialize the Dash app using the DARKLY theme.
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="DOTS Calculator", 
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1.0"}]
)

# Define the layout with two sliders for female and male bodyweights.
app.layout = html.Div(
    style={'padding': '20px'},
    children=[
        html.H1("DOTS Score Comparison", style={'textAlign': 'center'}),
        html.Div([
            html.Label("Female Weight (lbs):"),
            dcc.Slider(
                id='female-weight-slider',
                min=100,
                max=400,
                step=1,
                value=170,
                marks={i: str(i) for i in range(100, 401, 50)}
            )
        ], style={'margin-bottom': '20px'}),
        html.Div([
            html.Label("Male Weight (lbs):"),
            dcc.Slider(
                id='male-weight-slider',
                min=100,
                max=400,
                step=1,
                value=225,
                marks={i: str(i) for i in range(100, 401, 50)}
            )
        ], style={'margin-bottom': '20px'}),
        dcc.Graph(
            id='dots-chart',
            config={'displayModeBar': True}
        )
    ]
)

# Callback to update the chart when either slider value changes.
@app.callback(
    Output('dots-chart', 'figure'),
    [Input('female-weight-slider', 'value'),
     Input('male-weight-slider', 'value')]
)
def update_chart(female_weight, male_weight):
    return chart_1.create_chart(female_bodyweight=female_weight,
                                  male_bodyweight=male_weight)

if __name__ == '__main__':
    app.run_server(debug=True)

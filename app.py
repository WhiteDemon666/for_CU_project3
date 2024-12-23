from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc

from api import get_weather_data
from secret import api_key

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

MAP_STYLE = "open-street-map"

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Прогноз погоды"), className="text-center mb-4")
    ]),
    dbc.Row([
        dbc.Col(dcc.Input(id='city-input-1', type='text', placeholder='Введите первый город', className='form-control'),
                width=6),
        dbc.Col(dcc.Input(id='city-input-2', type='text', placeholder='Введите второй город', className='form-control'),
                width=6)
    ], className="mb-3"),
    dbc.Row([
        dbc.Col(dbc.Button('Добавить город', id='add-city-button', n_clicks=0, color='primary'), width='auto'),
        dbc.Col(dbc.Button('Удалить последний город', id='remove-city-button', n_clicks=0, color='danger'),
                width='auto')
    ], className="mb-3"),
    html.Div(id='additional-city-inputs'),
    dbc.Row([
        dbc.Col(dbc.Button('Получить погоду', id='submit-button', n_clicks=0, color='success'), className="text-center")
    ], className="mb-3"),

    dcc.Dropdown(
        id='days-dropdown',
        options=[
            {'label': str(i) + ' день' if i == 1 else str(i) + ' дня' if 2 <= i <= 4 else str(i) + ' дней', 'value': i}
            for i in range(2, 6)
        ],
        value=5,
        clearable=False,
        style={'width': '50%'},
        className="mb-3"
    ),

    dcc.Dropdown(
        id='parameter-dropdown',
        options=[
            {'label': 'Температура', 'value': 'temperature'},
            {'label': 'Вероятность осадков', 'value': 'precipitation'},
            {'label': 'Влажность', 'value': 'humidity'},
            {'label': 'Скорость ветра', 'value': 'wind_speed'}
        ],
        value='temperature',
        style={'display': 'none'}
    ),

    dcc.Graph(id='weather-graph', style={'display': 'none'}),
    dcc.Graph(id='weather-map')
], fluid=True)

@app.callback(
    [Output('additional-city-inputs', 'children'),
     Output('weather-graph', 'figure', allow_duplicate=True),
     Output('weather-graph', 'style', allow_duplicate=True),
     Output('parameter-dropdown', 'style'),
     Output('weather-map', 'figure', allow_duplicate=True)],
    [Input('add-city-button', 'n_clicks'),
     Input('remove-city-button', 'n_clicks'),
     Input('submit-button', 'n_clicks')],
    [State('city-input-1', 'value'),
     State('city-input-2', 'value'),
     State('additional-city-inputs', 'children'),
     State('days-dropdown', 'value')],
    prevent_initial_call=True
)
def manage_city_inputs(add_clicks, remove_clicks, submit_clicks, city1, city2, additional_cities, days):
    ctx = dash.callback_context

    if additional_cities is None:
        additional_cities = []

    city1 = city1.strip() if city1 else ''
    city2 = city2.strip() if city2 else ''

    if ctx.triggered:
        if ctx.triggered[0]['prop_id'].startswith('add-city-button'):
            new_input_index = len(additional_cities) + 3
            new_input = dcc.Input(type='text', placeholder=f'Город {new_input_index}', className='form-control mb-2')
            return additional_cities + [new_input], {}, {'display': 'none'}, {'display': 'none'}, {}

        elif ctx.triggered[0]['prop_id'].startswith('remove-city-button'):
            return additional_cities[:-1], {}, {'display': 'none'}, {'display': 'none'}, {}

        elif ctx.triggered[0]['prop_id'].startswith('submit-button'):
            cities_list = [city for city in
                           [city1, city2] +
                           [input_field.value.strip() for input_field in additional_cities if isinstance(input_field, dcc.Input)]
                           if city]

            df_weather = get_weather_data(cities_list, api_key)

            required_columns = ['date'] + ['temperature'] + ['loc']
            if not all(col in df_weather.columns for col in required_columns):
                return {}, {}, {'display': 'none'}, {'display': 'none'}, {}

            df_weather['date'] = pd.to_datetime(df_weather['date'], errors='coerce')

            filtered_df = df_weather.copy()

            if filtered_df.empty:
                return {}, {}, {'display': 'none'}, {'display': 'none'}, {}


            result_df = filtered_df.groupby('loc').tail(days)


            result_df.loc[:, 'date'] = result_df['date'].dt.strftime('%Y-%m-%d')

            fig_weather = px.line(result_df,
                                  x='date',
                                  y='temperature',
                                  color='loc',
                                  title=f'Данные о погоде: Температура за последние {days} {("дней" if days > 1 else "день")}',
                                  labels={'date': "Дата", 'temperature': "Температура"})


            map_fig = go.Figure()


            for _, row in result_df.iterrows():
                map_fig.add_trace(go.Scattermapbox(
                    lat=[row['lat']],
                    lon=[row['lon']],
                    mode='markers+lines',
                    marker=dict(size=10),
                    hoverinfo='text',
                    text=f"{row['loc']}: {row['temperature']}°C\nВлажность: {row.get('humidity')}%\nСкорость ветра: {row.get('wind_speed')} м/с\nВероятность осадков: {row.get('precipitation')}%"
                ))

                map_fig.add_trace(go.Scattermapbox(
                    lat=result_df['lat'],
                    lon=result_df['lon'],
                    mode='lines',
                    line=dict(width=2, color='blue'),
                    hoverinfo='none'
                ))


            map_fig.update_layout(
                mapbox=dict(
                    style=MAP_STYLE,
                    center=dict(lat=filtered_df['lat'].mean(), lon=filtered_df['lon'].mean()),
                    zoom=5
                ),
                title="Маршрут и прогнозы погоды",
                height=600,
                width=600
            )

            return additional_cities, fig_weather, {'display': 'block'}, {'display': 'block'}, map_fig

    return additional_cities or [], {}, {'display': 'none'}, {'display': 'none'}, {}

@app.callback(
    [Output('weather-graph', 'figure', allow_duplicate=True),
     Output('weather-graph', 'style'),
     Output('weather-map', 'figure')],
    [Input('days-dropdown', 'value'),
     Input('parameter-dropdown', 'value')],
    [State('additional-city-inputs', 'children'),
     State('city-input-1', 'value'),
     State('city-input-2', 'value')],
    prevent_initial_call=True
)
def update_graph(days, parameter, additional_cities, city1, city2):
    cities_list = [city.strip() for city in
                   [city1, city2] +
                   [input_field.value.strip() for input_field in additional_cities if isinstance(input_field, dcc.Input)]
                   if city]

    df_weather = get_weather_data(cities_list, api_key)

    required_columns = ['date'] + [parameter] + ['loc']

    if not all(col in df_weather.columns for col in required_columns):
        return {}, {'display': 'none'}, {}

    df_weather['date'] = pd.to_datetime(df_weather['date'], errors='coerce')

    filtered_df = df_weather.copy()

    if filtered_df.empty:
        return {}, {'display': 'none'}, {}

    result_df = filtered_df.groupby('loc').tail(days)

    result_df.loc[:, 'date'] = result_df['date'].dt.strftime('%Y-%m-%d')

    fig_weather = px.line(result_df,
                          x='date',
                          y=parameter,
                          color='loc',
                          title=f'Данные о погоде: {parameter.capitalize()} за последние {days} {("дня" if days == 1 else "дней")}',
                          labels={'date': "Дата", parameter: parameter.capitalize()})

    map_fig = go.Figure()

    for _, row in result_df.iterrows():
        map_fig.add_trace(go.Scattermapbox(
            lat=[row['lat']],
            lon=[row['lon']],
            mode='markers+lines',
            marker=dict(size=10),
            hoverinfo='text',
            text=f"{row['loc']}: {row[parameter]}°C\nВлажность: {row.get('humidity')}%\nСкорость ветра: {row.get('wind_speed')} м/с\nВероятность осадков: {row.get('precipitation')}%"
        ))

    map_fig.update_layout(
        mapbox=dict(
            style=MAP_STYLE,
            center=dict(lat=filtered_df['lat'].mean(), lon=filtered_df['lon'].mean()),
            zoom=5
        ),
        title="Маршрут и прогнозы погоды",
        height=600,
        width=600
    )

    return fig_weather, {'display': 'block'}, map_fig

if __name__ == '__main__':
    app.run_server(debug=True)

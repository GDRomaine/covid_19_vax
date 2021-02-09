# import kaggle
import pandas as pd

# kaggle.api.authenticate()
# dataset = 'gpreda/covid-world-vaccination-progress'
# path = '/Users/GDRomaine/data_science/covid-19_vax'
# kaggle.api.dataset_download_files(dataset, path=path, unzip=True)

vax = pd.read_csv('country_vaccinations.csv')
vax.date = pd.to_datetime(vax.date)

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

app.layout = html.Div([
    
    html.H3('COVID-19 World Vaccination Progress'),
    
    html.H6('Country selection:'),
    
    dcc.Dropdown(
        id = 'country_input',
        options = [{'label': c, 'value': c} for c in vax.country.unique()],
        multi = True,
        value = ['United States']),
    
    html.Div([
        
        html.H6('Statistic selection:'),
        
        dcc.RadioItems(
            id = 'stat_type_input',
            options = [{'label': 'absolute numbers', 'value': 'abs'},
                       {'label': 'population-adjusted', 'value': 'pop'}],
            value = 'abs'),
    
        dcc.RadioItems(id='stat_input')
        
    ], style={'columnCount': 2}),
    
    dcc.Graph(id='plot_output'),
    
    html.Div([
        
        html.H6('Vaccines used:'),

        html.Div(id='vaccines_used_output'),
        
        html.H6('Data sources:'),
        
        html.Div(id='data_sources_output')
        
    ], style={'columnCount': 2}),
    
    html.Div([
        
        dcc.Markdown('''*Data is collected daily by [Gabriel Preda](https://www.kaggle.com/gpreda) from
                    [Our World in Data's](https://ourworldindata.org/) [GitHub repository for COVID-19]
                    (https://github.com/owid/covid-19-data), merged, and uploaded to [Kaggle.]
                    (https://www.kaggle.com/gpreda/covid-world-vaccination-progress)*''',
                     style = {'textAlign': 'right', 'fontSize': 12})
    ])
])

@app.callback(Output('stat_input', 'options'),
              Input('stat_type_input', 'value'))
def set_stat_options(stat_type):
    if stat_type == 'abs':
        options = [{'label': 'total vaccinations', 'value': 'total_vaccinations'},
                   {'label': 'people vaccinated', 'value': 'people_vaccinated'},
                   {'label': 'people fully vaccinated', 'value': 'people_fully_vaccinated'},
                   {'label': 'daily vaccinations', 'value': 'daily_vaccinations'}]
        return options
    elif stat_type == 'pop':
        options = [{'label': 'total vaccinations per hundred', 'value': 'total_vaccinations_per_hundred'},
                   {'label': 'people vaccinated per hundred', 'value': 'people_vaccinated_per_hundred'},
                   {'label': 'people fully vaccinated per hundred', 'value': 'people_fully_vaccinated_per_hundred'},
                   {'label': 'daily vaccinations per million', 'value': 'daily_vaccinations_per_million'}]
        return options
    
@app.callback(Output('stat_input', 'value'),
              Input('stat_input', 'options'))
def set_stat_value(available_options):
    return available_options[0]['value']

@app.callback(Output('plot_output', 'figure'),
              Input('country_input', 'value'),
              Input('stat_input', 'value'))
def update_plot(countries, stat):
    if len(countries) != 0:
        df = vax[vax.country.isin(countries)].copy()
        # in order to preserve order of countries and corresponding colors in plot
        mapping = {country: i for i, country in enumerate(countries)}
        df['country_sort'] = df.country.map(mapping)
        df = df.sort_values(['country_sort', 'date'])
        fig = px.scatter(df, x='date', y=stat, color='country')
        fig.update_layout(xaxis_title='date', yaxis_title=stat)
        fig.update_traces(mode='lines+markers', connectgaps=True)
        return fig
    else:
        fig = px.scatter()
        return fig

@app.callback(Output('vaccines_used_output', 'children'),
              Input('country_input', 'value'))
def update_vaccines_used(countries):
    if len(countries) != 0:
        vax_used_list = []
        for country in countries:
            df = vax[vax.country == country]
            vax_used = df.vaccines.iloc[0]
            vax_used_list.append(dcc.Markdown(country + ': ' + vax_used))
        return vax_used_list
    else:
        return None
    
@app.callback(Output('data_sources_output', 'children'),
              Input('country_input', 'value'))
def update_data_sources(countries):
    if len(countries) != 0:
        data_sources_list = []
        for country in countries:
            df = vax[vax.country == country]
            source_name = df.source_name.iloc[0]
            source_website = df.source_website.iloc[0]
            markdown = '[{}: {}]({})'.format(country, source_name, source_website)
            data_sources_list.append(dcc.Markdown(markdown))
        return data_sources_list
    else:
        return None

if __name__ == '__main__':
    app.run_server(debug=True)
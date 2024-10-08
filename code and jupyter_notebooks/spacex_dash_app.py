# python3.11 spacex_dash_app.py
# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# dropdown options
dropdown_options = [
    {'label': 'All Sites', 'value': 'ALL'},
    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=dropdown_options,
                                            value='ALL', #Default Vale
                                            placeholder="Select a Launch Site", #lo que aparece en la app
                                            searchable=True, #Funcionalidad de busqueda en lista desplegable
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={i: f'{i} kg' for i in range(0, 10001, 1000)},
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
# Pie suma los valores numericos en cada celda de la columna, por eso me dara el mismo resultado en este caso
# si uso un df filtrado con los lanzamientos exitosos, o si uso todo el dataframe, ya que los ceros
# no van a sumar al tamano de cada seccion del pie. Si class tuviera otros valores, o fuera categorica o booleana, 
# ahi si seria necesario hacer un filtro y luego usar count() por ejemplo asi
#site_counts = filtered_df['Launch Site'].value_counts().reset_index()
#site_counts.columns = ['Launch Site', 'count']
def get_pie_chart(entered_site): 
    if entered_site == 'ALL':
        fig = px.pie(spacex_df, values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site')
        return fig
    else:
        condition = spacex_df['Launch Site']==entered_site
        filtered_df = spacex_df[condition]
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        fig = px.pie(site_counts, values='count', 
            names='class', 
            title=f'Success vs. Failure Launches for {entered_site}')
        return fig


# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
            Output(component_id='success-payload-scatter-chart', component_property='figure'),
            [Input(component_id='site-dropdown', component_property='value'), 
            Input(component_id="payload-slider", component_property="value")]
            )

def get_scatterplot(selected_site,payload_range): 
    low, high = payload_range
    # Filtrar el DataFrame según el rango de carga útil seleccionado
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]
    
    # Si se selecciona "ALL", mostramos todos los sitios
    if selected_site == 'ALL':
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites')
    else:
        # Filtrar el DataFrame por el sitio de lanzamiento seleccionado
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for {selected_site}')
    
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(port=8090)

#esto es lo que se ejecuta en terminal
# python3.11 spacex_dash_app.py
# Author: Faiber Alonso Leal

# %% [markdown]
# ### Assignment #5: Basic UI
# 
# DS4003 | Spring 2024
# 
# Objective: Practice adding callbacks to Dash apps.
# 
# Task:
# (1) Build an app that contains the following components user the gapminder dataset: `gdp_pcap.csv`. 
# TASK 1 is the same as ASSIGNMENT 4. You are welcome to update your code. 
# 
# UI Components:
# A dropdown menu that allows the user to select `country`
# - The dropdown should allow the user to select multiple countries
# - The options should populate from the dataset (not be hard-coded)
# A slider that allows the user to select `year`
# - The slider should allow the user to select a range of years
# - The range should be from the minimum year in the dataset to the maximum year in the dataset
# A graph that displays the `gdpPercap` for the selected countries over the selected years
# - The graph should display the gdpPercap for each country as a line
# - Each country should have a unique color
# - The graph should have a title and axis labels in reader friendly format
#  
# 
# (2) Write Callback functions for the slider and dropdown to interact with the graph
# 
# This means that when a user updates a widget the graph should update accordingly.
# The widgets should be independent of each other. 
# Layout:
# - Use a stylesheet
# - There should be a title at the top of the page
# - There should be a description of the data and app below the title (3-5 sentences)
# - The dropdown and slider should be side by side above the graph and take up the full width of the page
# - The graph should be below the dropdown and slider and take up the full width of the page
# Submission:
# - Deploy your app on Render. 
# - In Canvas, submit the URL to your public Github Repo (made specifically for this assignment)
# - The readme in your GitHub repo should contain the URL to your Render page. 
# **For help you may use the web resources and pandas documentation. No co-pilot or ChatGPT.**

# %%
# import needed dependencies
from dash import Dash, html, dcc, Input, Output
import pandas as pd
import plotly.express as px

# %%
# read in data
data = pd.read_csv('gdp_pcap.csv')
print(data.head())

# melt data to reshape the wide data to long data, so that it is easier to work with
columns_to_select = data.columns.drop('country').tolist()
data = pd.melt(data, id_vars='country', value_vars=columns_to_select)
data = data.rename(columns={'variable': 'year', 'value': 'gdp_pcap'})

# observe flipped data
data.head()


# %%
# look at datatypes for potential issues
print(data.info())

# convert year to numeric
data['year'] = data['year'].astype(int)

# convert gdp to numeric, some values are written as 10.1 k , so use function to fix this
def convert_to_numeric(value):
    if isinstance(value, str) and 'k' in value:
        return int(float(value.replace('k', '')) * 1000)
    elif isinstance(value, (int, float)):
        return int(value)
    else:
        return value
data['gdp_pcap'] = data['gdp_pcap'].apply(convert_to_numeric)
data['gdp_pcap'] = data['gdp_pcap'].astype(int)

# look at converted data
print(data.info())
data.head()


# %%

# import stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# set up app and use stylesheet
app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

# set up app layout
app.layout = html.Div([

    # write a title
    html.H1("Gapminder: GDP per capita by country"),
    # write a description
    html.P("This app uses gapminder data that contains yearly GDP per capita of each country."),
    html.P("The app visualizes the GDP data using a dropdown, a slider, and a line graph."),
    html.P("The dropdown allows users to select any of the countries included in the dataset."),
    html.P("The slider features the range of years included in the dataset and allows users to select ranges of years."),
    html.P("Users are able to select countries and years to be displayed in a graph of GDP per capita over time below."),

    # write code for the dropdown
    html.Div([
        # label of the dropdown
        html.Label("Select Country"),
        dcc.Dropdown(
            id="country dropdown", 
            # write in country options from dataset
            options=[{'label': country, 'value': country} for country in data['country'].unique()],
            # make a placeholder
            placeholder =  'Select countries',
            # allow multiple countries to be selected
            multi=True
        ),
    # make the dropdown half width
    ], style={'width': '50%', 'display': 'inline-block'}),

    # write code for the slider
    html.Div([
        # write a label for the slider
        html.Label("Years"),
        dcc.RangeSlider(
            id='Year-slider',
            # make min and max the min and max years of the dataset
            min=data['year'].min(),
            max=data['year'].max(),
            # set the values to the min and max
            value = [data['year'].min(), data['year'].max()],
            # create marks every 30 years to keep app looking clean
            marks={int(year): str(year) for year in data['year'].unique() if year % 30 == 0},
            step=1
        ),
    # make the slider half width
    ], style={'width': '50%', 'display': 'inline-block'}),

    # write code for the graph below the dropdown and slider, will use callback to define figure
    dcc.Graph(id='GDP-graph')
])

# define callback
@app.callback(
    Output('GDP-graph', 'figure'),
    [Input('country dropdown', 'value'),
     Input('Year-slider', 'value')]
)

# define callback function to allow graph to use selected countries and years
def update_figure(selected_countries, selected_years):
    # return an empty graph if no countries are selected
    if selected_countries is None or len(selected_countries) == 0:
        return px.line(title="No countries selected for GDP per Capita Graph")
    # use only user selected data
    filtered_data = data[(data['country'].isin(selected_countries)) & (data['year'].between(selected_years[0], selected_years[1]))]
    fig = px.line(filtered_data, x='year', y='gdp_pcap', color='country',
                  title='GDP per Capita Over Time',
                  labels={'country': 'Country', 'gdp_pcap': 'GDP per Capita'})
    fig.update_layout(xaxis_title='Year', yaxis_title='GDP per Capita')
    # return figure
    return fig

# run app
if __name__ == "__main__":
    app.run_server(debug=True)


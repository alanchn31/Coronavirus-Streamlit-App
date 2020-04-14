import streamlit as st
import numpy as np 
import pandas as pd
import datetime
import altair as alt
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects

st.title('Coronavirus Data Global')

DATE_COLUMN = 'daterep'
DATA_URL = ('https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')

@st.cache
def load_data():
    data = pd.read_csv(DATA_URL)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN], format='%d/%m/%Y')
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text('')


COUNTRIES_DICT = {
    'United States of America': "USA",
    "United Kingdom": 'UK'
}


yesterday = datetime.date.today() - datetime.timedelta(days=1)
date = st.date_input('Date', yesterday)
dt64 = np.datetime64(date)
filtered_data = data.loc[data[DATE_COLUMN] == dt64]

st.markdown('**Total new cases:** {}  \n'.format(filtered_data['cases'].sum()) + 
            '**Total new deaths:** {}'.format(filtered_data['deaths'].sum()))

st.subheader('Top 10 Countries (by new cases)')
top_10_data = filtered_data.sort_values(by='cases', ascending=False).iloc[:10]
top_10_data['countriesandterritories'] = top_10_data['countriesandterritories'].apply(lambda x: x.replace("_", " "))
top_10_data['countriesandterritories'] = top_10_data['countriesandterritories'].apply(lambda x: \
                                                                                     COUNTRIES_DICT.get(x, x))
st.write(alt.Chart(top_10_data, width=600, height=500).mark_bar().encode(
    x=alt.X('countriesandterritories', sort=None,  title='Countries and Territories'),
    y=alt.Y('cases', title='Number of New Cases'),
).configure_axisX(
    titleAngle=0,
    labelAngle=0
))


st.subheader('Global Map of Coronavirus Cases')
fig = go.Figure(data=go.Choropleth(
    locations = filtered_data['countryterritorycode'],
    z = np.log10(filtered_data['cases']),
    text = ['Country: {}<br>Number of new cases: {} <br> Number of deaths: {} <br>'.format(filtered_data['countriesandterritories'].iloc[i],
                                                                                           filtered_data['cases'].iloc[i],
                                                                                           filtered_data['deaths'].iloc[i],) \
            for i in range(len(filtered_data['cases']))
            ],
    colorscale = 'Bluered_r',
    autocolorscale=False,
    reversescale=True,
    marker_line_color='darkgray',
    marker_line_width=0.5,
    colorbar = dict(len=0.75,
                    title='New Cases of Coronavirus',
                    tickprefix='1.e',
                    ticktext=[str(x) for x in np.linspace(np.min(filtered_data['cases']), 
                                            np.max(filtered_data['cases']),
                                         num=10)])
    # colorbar_title = 'New Cases of Coronavirus'
))

fig.update_layout(
    title_text='Cases of Coronavirus Globally',
    autosize=False,
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='equirectangular'
    ),
    annotations = [dict(
        x=0.55,
        y=0.1,
        xref='paper',
        yref='paper',
        text='Source: <a href="https://opendata.ecdc.europa.eu/covid19/casedistribution/csv">\
            European Centre for Disease Prevention and Control</a>',
        showarrow = False
    )],
    margin = dict(l=10,r=50, b=40, t=40, pad=4),
    width=800,
    height=600,
)

fig
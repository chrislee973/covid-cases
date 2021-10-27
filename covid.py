import pandas as pd
import numpy as np
import json
from datetime import date, datetime, timedelta
import pytz

import streamlit.components.v1 as components
import streamlit as st
import plotly.graph_objects as go
st.set_page_config(layout="wide")


from utils import *


# READ MOST RECENT DATA
# Yesterday's date is used to read in new data and send it to cache, since the most recent date with data available is the day before the present day
# yesterday = date.today() - timedelta(1)
tz = pytz.timezone('US/Pacific')
yesterday = datetime.now(tz).date() - timedelta(1)

@st.cache
def read_data(yesterday):
    df = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv', 
                        parse_dates=['date'], 
                        )
    df['date'] = df['date'].dt.date
    drop_idx = df[df['location'].isin(df['continent'].unique()) 
                | (df['location'] =='World') | (df['location'] =='European Union')].index
    df= df.drop(drop_idx)
    return df
df = read_data(yesterday)


# HEADING
st.title("Covid-19 Global Cases")
st.write("By Christopher Lee")
st.subheader("""A global dashboard of daily new cases and other related metrics using data sourced from Our World in Data.""")
st.write("Use the side-panel on the left to select the metric you'd like to see as well as the date you'd like to view data for (the date with the latest available data is selected by default).")
"""***"""


# SIDEBAR 
# selected_feature = st.sidebar.selectbox('What metric would you like to view data for?', 
#                                     ['New cases','New cases per capita', 'New cases (7 day rolling average)', 'New cases per capita (7 day rolling average)'])

feature_map = {'New cases': 'new_cases', 
                'New cases per capita': 'new_cases_per_million', 
                'New cases (7 day rolling average)': 'new_cases_smoothed', 
                'New cases per capita (7 day rolling average)': 'new_cases_smoothed_per_million', 
                'Total cases': 'total_cases', 
                'Total cases per capita': 'total_cases_per_million'}

# most_recent = sorted(set(df.date), reverse=True)[0]#.strftime("%B %d, %Y")
most_recent=yesterday
day_before_most_recent = yesterday - timedelta(1)
first_date = sorted(set(df.date))[0]

selected_feature_COLUMN, date_input_COLUMN = st.columns(2)
with selected_feature_COLUMN:
    selected_feature = st.selectbox('Metric', 
                                    ['New cases','New cases per capita', 'New cases (7 day rolling average)', 'New cases per capita (7 day rolling average)'])
# date_input = st.sidebar.date_input('Choose date to display data', most_recent, min_value=first_date, max_value=most_recent)
with date_input_COLUMN:
    date_input = st.date_input(f'Choose date to display data(most recent date is {most_recent.strftime("%m/%d/%Y")})', most_recent, min_value=first_date, max_value=most_recent)

col1, col2 = st.columns([8,1])

# CHOROPLETH
fig = plotly_choropleth(df, date_input, selected_feature=feature_map.get(selected_feature, ''), 
                        )
with col1:
    st.plotly_chart(fig, use_container_width=True)    

st.write("""***""")

# DAILY INCREASES CHART
st.header(f"Countries with highest daily increase in {selected_feature.lower()}")
df_pivot = pivot(df, selected_feature, feature_map)
percent_increase, absolute_increase = daily_increase(df_pivot, most_recent, day_before_most_recent)
# with col2:
#     col2.subheader('Top 20 countries with highest daily increase in '+ selected_feature.lower())
#     option = st.selectbox("select option", ["% increase", "absolute increase"])
#     if option == "% increase":
#         # st.table(percent_increase)
#         st.bar_chart(percent_increase, use_container_width=False)
#     elif option == "absolute increase":
#         st.table(absolute_increase)
#     st.bar_chart(absolute_increase, use_container_width=False)
chart1, chart2 = st.columns(2)
with chart1:
    percent_chart = plotly_bargraph(percent_increase, most_recent, day_before_most_recent, selected_feature = selected_feature, option = "% increase")
    st.plotly_chart(percent_chart)
with chart2:
    abs_chart = plotly_bargraph(absolute_increase, most_recent, day_before_most_recent, selected_feature = selected_feature, option = "abs. increase")
    st.plotly_chart(abs_chart)

# st.write("""***""")

# st.header('Top 20 countries with highest daily increase in '+ selected_feature.lower())
# st.write(f'From {day_before_most_recent.strftime("%B %d, %Y")} - {most_recent.strftime("%B %d, %Y")}')
# st.write('Ranked in decreasing order.')

# st.write("""***""")

# percent_increase_COLUMN, abs_increase_COLUMN = st.columns(2)

# percent_increase_COLUMN.write('% increase')
# percent_increase_COLUMN.table(percent_increase)

# abs_increase_COLUMN.write('Absolute increase')
# abs_increase_COLUMN.table(absolute_increase)

st.write("""***""")
# HIGHEST TOTAL CASES TABLE
st.header("Countries with the highest total cases")
st.write('As of ' + most_recent.strftime("%B %d, %Y"))
per_capita = st.checkbox('View per-capita')
if per_capita:
    feature_name = 'Total cases per capita'
else:
    feature_name = 'Total cases'

total_cases = pivot(df, feature_name, feature_map)
most_cases = pd.DataFrame(total_cases[most_recent].sort_values(ascending=False)).head(20)
most_cases.rename(columns = {most_cases.columns[0]: feature_name}, inplace=True)
st.table(most_cases.style.format("{:,}"))

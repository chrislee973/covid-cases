import pandas as pd
import numpy as np
import json
from datetime import date, datetime, timedelta

import streamlit.components.v1 as components
import streamlit as st
import plotly.graph_objects as go
st.set_page_config(layout="wide")


from utils import *


# READ MOST RECENT DATA
# Yesterday's date is used to read in new data and send it to cache, since the most recent date with data available is the day before the present day
yesterday = date.today() - timedelta(1)

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
st.subheader("""A daily-updated interactive dashboard of new cases on a country by country basis. Data sourced from Our World in Data.""")
st.write("Use the panel on the left to select the metric you'd like to see, as well as a date you'd like to see data for (the most recent date the data contains is selected by default).")
"""***"""


# SIDEBAR 
selected_feature = st.sidebar.selectbox('What metric would you like to view data for?', 
                                    ['New cases','New cases per capita', 'New cases (7 day rolling average)', 'New cases per capita (7 day rolling average)'])

feature_map = {'New cases': 'new_cases', 
                'New cases per capita': 'new_cases_per_million', 
                'New cases (7 day rolling average)': 'new_cases_smoothed', 
                'New cases per capita (7 day rolling average)': 'new_cases_smoothed_per_million', 
                'Total Cases': 'total_cases'}

# most_recent = sorted(set(df.date), reverse=True)[0]#.strftime("%B %d, %Y")
most_recent=yesterday
day_before_most_recent = yesterday - timedelta(1)
first_date = sorted(set(df.date))[0]

st.sidebar.write("""***""")

selected_date = st.sidebar.slider(label="Choose date to display data", 
                        value=most_recent, 
                        min_value = first_date, 
                        max_value = most_recent,  
                        format="MM/DD/YY")


# CHOROPLETH
fig = plotly_choropleth(df, selected_date, selected_feature=feature_map.get(selected_feature, ''), 
                        )
st.plotly_chart(fig, use_container_width=True)

st.write("""***""")

# DAILY INCREASES TABLES
@st.cache
def pivot(df, feature):
    df = df.pivot(index=['location'], 
                columns='date', 
                values= feature_map.get(feature, ''))
    return df

df_pivot = pivot(df, selected_feature)

@st.cache
def daily_increase(df_pivot, most_recent, day_before_most_recent):
    """Calculates the increase of the selected feature between the most recent day and the day before that."""
    percent_increase = round(((df_pivot[most_recent] - df_pivot[day_before_most_recent]) / df_pivot[most_recent])*100).sort_values(ascending=False)
    absolute_increase = round(df_pivot[most_recent] - df_pivot[day_before_most_recent]).sort_values(ascending=False)

    percent_increase = pd.DataFrame(percent_increase[percent_increase != 100], columns=['% increase']).head(20)
    absolute_increase= pd.DataFrame(absolute_increase, columns=['abs. increase']).head(20)
    return percent_increase, absolute_increase

percent_increase, absolute_increase = daily_increase(df_pivot, most_recent, day_before_most_recent)


st.header('Top 20 countries with highest daily increase in '+ selected_feature.lower())
st.write(most_recent.strftime("%B %d, %Y"))
st.write('Ranked in decreasing order.')

st.write("""***""")

left_column, right_column = st.beta_columns(2)

left_column.write('% increase from prior day')
left_column.table(percent_increase)

right_column.write('Absolute increase from prior day')
right_column.table(absolute_increase)

st.write("""***""")

# HIGHEST TOTAL CASES TABLE
st.header("Countries with the highest total cases")
st.write('As of ' + most_recent.strftime("%B %d, %Y"))
total_cases = pivot(df, 'Total Cases')
most_cases = pd.DataFrame(total_cases[most_recent].sort_values(ascending=False)).head(20)
most_cases.rename(columns = {most_cases.columns[0]: 'Total Cases'}, inplace=True)
st.table(most_cases.style.format("{:,}"))
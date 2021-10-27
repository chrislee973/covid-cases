from datetime import datetime
import pandas as pd
import numpy as np
import json
from plotly.graph_objs.layout import xaxis

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px



def start_pipeline(df):
    '''Creates a copy of original dataframe to use in pipeline'''
    return df.copy()

def convert_datetime(df):
    '''Converts date column to datetime'''
    df['date'] = df['date'].apply(lambda x: x.to_pydatetime().date())
    return df

def dropContinents(df):
  '''Drop those rows whose location are the continents'''
  drop_idx = df[df['location'].isin(df['continent'].unique()) 
                | (df['location'] =='World') | (df['location'] =='European Union')].index
  df= df.drop(drop_idx)
  return df

def convertCountryLabels(df):
  '''Correct for differences between geojson country labels and OWID country labels. 
     Convert all dataframe country labels to what geojson expects.'''
  
  df= df.replace({
            'United States': 'United States of America', 
            'Serbia': 'Republic of Serbia', 
            'North Macedonia':'Macedonia', 
            'Czechia': 'Czech Republic', 
            "Cote d'Ivoire": 'Ivory Coast', 
            'Democratic Republic of Congo': 'Democratic Republic of the Congo', 
            'Congo': 'Republic of the Congo', 
            'Tanzania': 'United Republic of Tanzania', 
            'Guinea-Bissau': 'Guinea Bissau', 
              })
  return df

@st.cache
def pivot(df, feature, feature_map):
    df = df.pivot(index=['location'], 
                columns='date', 
                values= feature_map.get(feature, ''))
    return df

@st.cache
def daily_increase(df_pivot, most_recent, day_before_most_recent):
    """Calculates the increase of the selected feature between the most recent day and the day before that."""
    percent_increase = round(((df_pivot[most_recent] - df_pivot[day_before_most_recent]) / df_pivot[most_recent])*100).sort_values(ascending=False)
    absolute_increase = round(df_pivot[most_recent] - df_pivot[day_before_most_recent]).sort_values(ascending=False)

    percent_increase = pd.DataFrame(percent_increase[percent_increase != 100], columns=['% increase']).head(20)
    absolute_increase= pd.DataFrame(absolute_increase, columns=['abs. increase']).head(20)
    return percent_increase, absolute_increase

    
#--------- MAPPING
map_title = { 'new_cases': 'New cases',
              'new_cases_per_million': 'New cases per million people',
              'new_cases_smoothed': 'New cases (7 day rolling average)', 
             'new_cases_smoothed_per_million': 'New cases per million people (7 day rolling average)' 
              }
map_colorbar_title = {'new_cases_smoothed': 'New cases', 
                      'new_cases_smoothed_per_million': 'New cases'}

@st.cache
def plotly_choropleth(df, date , selected_feature = 'new_cases'):
  #Get the subset of the dataset matching the user-provided date
  df = df[df.date == date]

  #Convert date to string format
  date = date.strftime("%B %d, %Y")
  fig = go.Figure(data=go.Choropleth(
    locations = df['iso_code'],
    z = (df[selected_feature]),
    text = df['location'], #+ '<br>' + 'New cases ' + str(df_pipeline['new_cases_smoothed']) ,
    colorscale = [[0, '#ffffff'], [.0005, '#e8cfce'], [.005, '#d09f9c'], [0.1, '#a13e39'],  [0.2, '#8a0e08'], [.25, '#6e0b06'], [1.0, '#450704']],
    marker_line_color='darkgray',
    marker_line_width=0.5, 
    colorbar_title = map_colorbar_title.get(selected_feature, '')
  ))
  fig.update_layout(
      title_text = '<b>' + map_title.get(selected_feature, '') + '</b>' + 
                   '<br>' +
                   '<i>' + date + '</i>'  + '<br>' + '(hover over country for the exact number of the selected metric)',
      width = 120,
      height=800, 
      )
  return fig


@st.cache
def plotly_bargraph(df, date, date_before_most_recent, selected_feature, option = "% increase"):
  # fig = go.Figure([go.Bar(x=df.index, y=df[option], hovertext='{:.2%}'.format(list(df[option])))])
  df = df.reset_index().rename(columns={"index": "Country"})
  fig = px.bar(df, x="location", y=option, labels={'location': 'Country'})
  # fig = go.Figure([go.Bar(x=df.index, y=df[option], hovertext=["{:.0%}".format(x/100) for x in df[option]])])
  fig.update_layout(
    # font=dict(
    #     family="Roboto, monospace",
    #     size=12,
    # ),
yaxis_title = f"{option} in {selected_feature.lower()}", title_text = f"<b>Countries with highest daily increase in {selected_feature.lower()}</b> ({option})" + "<br>" + f'<i>From {date_before_most_recent.strftime("%B %d, %Y")} - {date.strftime("%B %d, %Y")}</i>', xaxis_tickangle=-45)
  return fig
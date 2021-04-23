from datetime import datetime
import pandas as pd
import numpy as np
import json

import streamlit as st
import plotly.graph_objects as go



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

#--------- MAPPING
map_title = { 'new_cases': 'New cases',
              'new_cases_per_million': 'New cases per million people',
              'new_cases_smoothed': 'New cases (7 day rolling average)', 
             'new_cases_smoothed_per_million': 'New cases per million people (7 day rolling average)' 
              }
map_colorbar_title = {'new_cases_smoothed': 'New cases', 
                      'new_cases_smoothed_per_million': 'New cases'}

@st.cache
def plotly_choropleth(df, date, selected_feature = 'new_cases'):
  #Get the subset of the dataset matching the user-provided date
  df = df[df.date == date]

  #Convert date to string format
  date = date.strftime("%B %d, %Y")
  fig = go.Figure(data=go.Choropleth(
    locations = df['iso_code'],
    z = (df[selected_feature]),
    text = df['location'], #+ '<br>' + 'New cases ' + str(df_pipeline['new_cases_smoothed']) ,
    # colorscale = 'Reds',
    # colorscale = [[0, 'green'], [.005, 'yellow'], [.05, 'orange'], [0.5, 'red'], [.8, 'purple'], [1.0, 'rgb(0, 0, 255)']],
    # colorscale = [[0, '#ffffff'], [.005, 'yellow'], [.05, 'orange'], [0.5, 'red'], [.8, 'purple'], [1.0, 'rgb(0, 0, 255)']],
    # colorscale = [[0, '#ffffff'], [.005, '#f5b9b9'], [.05, '#ec7474'], [0.5, '#e54545'], [.8, '#e22e2e'], [1.0, '#df1717']],
    colorscale = [[0, '#ffffff'], [.0005, '#e8cfce'], [.005, '#d09f9c'], [0.1, '#a13e39'],  [0.2, '#8a0e08'], [.25, '#6e0b06'], [1.0, '#450704']],
    marker_line_color='darkgray',
    marker_line_width=0.5, 
    colorbar_title = map_colorbar_title.get(selected_feature, '')
  ))
  fig.update_layout(
      title_text = '<b>' + map_title.get(selected_feature, '') + '</b>' + 
                   '<br>' +
                   '<i>' + 'As of ' + date + '</i>'  + '<br>' + '(hover over country for the exact number of the selected metric)',
      width = 900,
      height=700, 
      )
  return fig


from datetime import datetime
import pandas as pd
import numpy as np
import json
from plotly.graph_objs.layout import xaxis

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


@st.cache
def pivot(df, feature, feature_map):
    df = df.pivot(
        index=["location"],
        columns="date",
        values=feature_map.get(feature, ""),
    )
    return df


@st.cache
def daily_increase(df_pivot, most_recent, day_before_most_recent):
    """Calculates the increase of the selected feature between the most recent day and the day before that."""
    percent_increase = round(
        (
            (df_pivot[most_recent] - df_pivot[day_before_most_recent])
            / df_pivot[most_recent]
        )
        * 100
    ).sort_values(ascending=False)
    absolute_increase = round(
        df_pivot[most_recent] - df_pivot[day_before_most_recent]
    ).sort_values(ascending=False)

    percent_increase = pd.DataFrame(
        percent_increase[percent_increase != 100], columns=["Percent increase"]
    ).head(20)
    absolute_increase = pd.DataFrame(
        absolute_increase, columns=["Absolute increase"]
    ).head(20)
    return percent_increase, absolute_increase


# --------- MAPPING
MAP_TITLE = {
    "new_cases": "New cases",
    "new_cases_per_million": "New cases per million people",
    "new_cases_smoothed": "New cases (7 day rolling avg)",
    "new_cases_smoothed_per_million": "New cases per million people (7 day rolling avg)",
    "total_cases": "Total cases",
    "total_cases_per_million": "Total cases per million people",
}
map_colorbar_title = {
    "new_cases": "New cases",
    "new_cases_per_million": "New cases per million people",
    "new_cases_smoothed": "New cases (7 day rolling avg)",
    "new_cases_smoothed_per_million": "New cases per million people (7 day rolling avg)",
    "total_cases": "Total cases",
    "total_cases_per_million": "Total cases per million people"
    # "color": "log10(New cases)",
}


@st.cache
def plotly_choropleth(df, date, selected_feature="new_cases"):
    # Get the subset of the dataset matching the user-provided date
    df = df[df.date == date]

    # Convert date to string format
    date = date.strftime("%B %d, %Y")
    fig = px.choropleth(
        df,
        locations="iso_code",
        color=np.log10(df[selected_feature] + 0.01),
        # color=df[selected_feature],
        color_continuous_scale="Blues",
        hover_name="location",
        hover_data={"iso_code": False, selected_feature: ":,.0f"},
        labels=map_colorbar_title,
        # range_color=[df[selected_feature].min(), df[selected_feature].max()],
    )
    fig.update_layout(
        title_text="<b>"
        + MAP_TITLE.get(selected_feature, "")
        + "</b>"
        + "<br>"
        + "<i>"
        + date
        + "</i>"
        + "<br>",
        # + "(hover over country for the exact number of the selected metric)",
        width=120,
        height=800,
        coloraxis_colorbar=dict(
            title=map_colorbar_title.get(selected_feature, ""),
            tickvals=[-2, 1, 2, 3, 3.699, 4, 5, 6, 7, 7.60],
            ticktext=[
                "0",
                "10",
                "100",
                "1,000",
                "5,000",
                "10,000",
                "100,000",
                "1,000,000",
                "10,000,000",
                "40,000,000",
            ],
        ),
    )
    return fig


@st.cache
def plotly_bargraph(df, most_recent, option):
    df = df.reset_index().rename(columns={"index": "Country"})
    fig = px.bar(
        df,
        x="location",
        y=option,
        hover_name="location",
        hover_data={"location": False, option: ":,.0f"},
    )
    fig.update_layout(
        yaxis_title=f"{option}",
        title_text=f"<b>{option} from previous day</b>",
        xaxis_tickangle=-45,
    )
    return fig

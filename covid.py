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
tz = pytz.timezone("US/Pacific")
yesterday = datetime.now(tz).date() - timedelta(1)


@st.cache
def read_data(yesterday):
    df = pd.read_csv(
        "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv",
        parse_dates=["date"],
    )
    df["date"] = df["date"].dt.date
    drop_idx = df[
        df["location"].isin(df["continent"].unique())
        | (df["location"] == "World")
        | (df["location"] == "European Union")
    ].index
    df = df.drop(drop_idx)
    df = df.dropna(subset=["continent"])
    return df


df = read_data(yesterday)

# HEADING
st.title("Covid-19 Global Cases")
st.subheader(
    """A global dashboard of daily new cases and other related metrics using data sourced from Our World in Data."""
)
st.write("By Christopher Lee")
"""***"""

feature_map = {
    "New cases": "new_cases",
    "New cases per million people": "new_cases_per_million",
    "New cases (7 day rolling average)": "new_cases_smoothed",
    "New cases per million people (7 day rolling average)": "new_cases_smoothed_per_million",
    "Total cases": "total_cases",
    "Total cases per million people": "total_cases_per_million",
}

most_recent = yesterday
day_before_most_recent = yesterday - timedelta(1)
first_date = sorted(set(df.date))[0]

selected_feature_COLUMN, date_input_COLUMN = st.columns(2)
with selected_feature_COLUMN:
    selected_feature = st.selectbox(
        "Metric",
        [
            "New cases",
            "New cases per million people",
            "New cases (7 day rolling average)",
            "New cases per million people (7 day rolling average)",
        ],
    )
with date_input_COLUMN:
    date_input = st.date_input(
        f"Choose date to display data",
        most_recent,
        min_value=first_date,
        max_value=most_recent,
    )


# CHOROPLETH
fig = plotly_choropleth(
    df,
    date_input,
    selected_feature=feature_map.get(selected_feature, ""),
)
st.plotly_chart(fig, use_container_width=True)

st.write("""***""")

# DAILY INCREASES CHART
st.subheader(
    f"Countries with highest daily increase in {MAP_TITLE.get(feature_map.get(selected_feature, ''), '').lower()}"
)
st.write(
    f"""From {day_before_most_recent.strftime("%B %d, %Y")} - {most_recent.strftime("%B %d, %Y")}"""
)
df_pivot = pivot(df, selected_feature, feature_map)
percent_increase, absolute_increase = daily_increase(
    df_pivot, most_recent, day_before_most_recent
)

bar1, bar2 = st.columns(2)
with bar1:
    percent_chart = plotly_bargraph(
        percent_increase, most_recent, option="Percent increase"
    )
    st.plotly_chart(percent_chart)
with bar2:
    abs_chart = plotly_bargraph(
        absolute_increase, most_recent, option="Absolute increase"
    )
    st.plotly_chart(abs_chart)

st.write("""***""")

# HIGHEST TOTAL CASES TABLE
st.subheader("Total cases")
st.write("As of " + most_recent.strftime("%B %d, %Y"))
per_capita = st.checkbox("View per-capita")
if per_capita:
    feature_name = "Total cases per million people"
else:
    feature_name = "Total cases"


# st.table(most_cases.style.format("{:,}"))

# total_cases_bar, total_cases_choropleth = st.columns(2)
# with total_cases_choropleth:
total_cases_fig = plotly_choropleth(df, most_recent, feature_map.get(feature_name, ""))
st.plotly_chart(total_cases_fig, use_container_width=True)


# with total_cases_bar:
total_cases = pivot(df, feature_name, feature_map)
most_cases = pd.DataFrame(total_cases[most_recent].sort_values(ascending=False)).head(
    20
)
most_cases.rename(columns={most_cases.columns[0]: feature_name}, inplace=True)
fig = px.bar(
    most_cases,
    y=most_cases.index,
    x=most_cases[feature_name],
    text=feature_name,
    orientation="h",
    height=700,
    width=800,
    # height=800,
    # width=1000,
    labels={"location": "Country"},
    hover_data={feature_name: ":,.0f"},
)
fig.update_traces(texttemplate="%{text:.3s}", textposition="outside")
fig.update_layout(
    yaxis={"categoryorder": "total ascending"},
    title_text=f"<b>Countries with the highest {feature_name.lower()}</b><br><i>As of {most_recent.strftime('%B %d, %Y')}</i>",
)
st.plotly_chart(fig)

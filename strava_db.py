import pandas as pd
from get_data import *
from pathlib import Path
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
pd.options.mode.chained_assignment = None
import plotly.express as px

import streamlit as st

st.set_page_config(page_title='Strava Dashboard', 
                    page_icon = './images/strava_vector.png',
                    layout="wide")

# GET AND PREPARE THE DATA
activities_raw = pd.read_csv('strava_activities.csv')
activities = prepare_data(activities_raw)

types_of_activities = activities.sport_type.unique()


runs = activities[activities['sport_type'] == 'Run']
runs_2022 = runs[runs.index.year == 2022]

t1, t2, t3, t4 = st.columns([2.4, 3.5, 0.12, 0.5])
with t2:
    # set dashboard title:
    st.title('Running Dashboard')

st.markdown('---')

kpi0, kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns([0.2, 1, 1, 1, 1, 1, 1])

with kpi1:
    total_runs = runs_2022.shape[0]
    kpi1.metric(label='Total Runs', value=total_runs)

with kpi2:
    miles_run = round(runs_2022.distance.sum())
    kpi2.metric(label="Miles Ran (YTD)", value=f"{miles_run:,}")

with kpi3:
    elev_gain = round(runs_2022.total_elevation_gain.sum())
    kpi3.metric(label="Elevation Gain (YTD)", value=f"{elev_gain:,}")

with kpi4:
    mpd = runs_2022.distance.sum() / runs_2022.index[0].day_of_year
    kpi4.metric(label="Miles Per Day", value=round(mpd, 2))

with kpi5:
    mpr = runs_2022.distance.sum() / runs_2022.shape[0]
    kpi5.metric(label="Miles Per Run", value=round(mpr, 2))

with kpi6:
    time_running_ytd = to_time_readout(runs_2022.moving_time.sum())
    kpi6.metric(label='Time Running YTD', value=time_running_ytd)

st.markdown('---')


choices = {'W-Mon': '%A, %b %d %Y', 'M': '%B %Y', 'Y': '%Y'}
choices_txt = {'By Week': 'W-Mon', 'By Month': 'M', 'By Year': 'Y'}

choice_selector = st.radio('Totals by Week, Month, or Year', choices_txt.keys())
choice = choices_txt[choice_selector]

# #strava_activities_clean[strava_activities_clean['sport_type'] == 'Run'].resample('W-Mon', closed='left').distance.sum().tail(15)
df_slice = activities[activities['sport_type'] == 'Run'].resample(choice, closed='left').distance.sum().tail(12)
#df_slice.index = df_slice.index.strftime('%B %Y')
df_slice.index = df_slice.index.strftime(choices[choice])

fig = px.line(df_slice, range_y=[0,df_slice.max()])
st.plotly_chart(fig)

st.dataframe(df_slice)


        # #strava_activities_clean[strava_activities_clean['sport_type'] == 'Run'].resample('W-Mon', closed='left').distance.sum().tail(15)
df_slice_2 = activities[activities['sport_type'] == 'Run'].resample(choice, closed='left')[['distance', 'total_elevation_gain']].sum().tail(12)
#df_slice.index = df_slice.index.strftime('%B %Y')
df_slice_2.index = df_slice_2.index.strftime(choices[choice])
st.dataframe(df_slice_2)




    

#  p = Path.home()
# emojis = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / 'emoji.json')
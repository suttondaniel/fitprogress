import pandas as pd
#pd.options.display.max_rows = 999

import time
import datetime as dt
import numpy as np
from pathlib import Path
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import streamlit as st
import time

import plotly.express as px
import plotly.graph_objs as go
#import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None

def main():
    # render the readme as markdown using st.markdown
    p = Path.home()
    emojis = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / 'emoji.json')

    #st.markdown(open(readme).read())
    strava_activities_raw = pd.read_csv('strava_activities.csv')

    cols_to_drop = ['Unnamed: 0.1', 'athlete', 'resource_state', 'start_date_local', 'timezone', 
    'utc_offset', 'trainer', 'commute', 'type', 'manual', 'visibility', 'flagged', 'gear_id', 'start_latlng', 'end_latlng', 'display_hide_heartrate_option',
    'upload_id_str', 'external_id', 'from_accepted_tag', 'total_photo_count', 'athlete.resource_state', 'map.id', 'map.summary_polyline', 'map.resource_state', 
    'average_watts', 'kilojoules', 'device_watts', 'photo_count', 'heartrate_opt_out', 'upload_id', 'athlete.id', 'workout_type',
    'has_heartrate', 'location_city', 'location_state', 'location_country', 'private', 'has_kudoed', 'Unnamed: 0']


    strava_activities_clean = strava_activities_raw.drop(labels=cols_to_drop, axis=1)

    # meters to miles
    strava_activities_clean['distance'] = strava_activities_clean.distance * .000621

    # might be a fun metric to plot over time. perhaps my suffering per minute has gone down as ive gotten fitter
    strava_activities_clean['SPM'] = strava_activities_clean.suffer_score / (strava_activities_clean.moving_time / 60)

    rename = {'start_date': 'start_time'}
    strava_activities_clean.rename(rename, axis=1, inplace=True)

    # convert start_time to pandas Timestamp object. then we can access seconds, minutes, hours, etc. and can add the moving_time
    strava_activities_clean['start_time'] = pd.to_datetime(strava_activities_clean['start_time'])

    # have to manually adjust one activity; the run was on 6/12 not 6/13
    strava_activities_clean.loc[strava_activities_clean.id == 7299973019, 'start_time'] = pd.Timestamp(year=2022, month=6, day=12, hour=2, minute=8, second=36, tz='UTC')

    strava_activities_clean.set_index('start_time', inplace=True)

    types_of_activities = strava_activities_clean.sport_type.unique()
    activity_choice = st.sidebar.selectbox('Select an activity', types_of_activities)

    


    if activity_choice == activity_choice:
        numtimes = strava_activities_clean[strava_activities_clean.sport_type == activity_choice].shape[0]
        em = pd.read_json(emojis, orient='index')
        em = list(em.index)
        emojis = np.random.choice(em, 3)
        st.markdown(f'### You\'ve {activity_choice} {numtimes} times over the past 3 years :{emojis[0]}::{emojis[1]}::{emojis[2]}:')

    choice = st.selectbox('Select the time frame you want to see your totals for', ['W-Mon', 'M', 'Y'])

    #strava_activities_clean[strava_activities_clean['sport_type'] == 'Run'].resample('W-Mon', closed='left').distance.sum().tail(15)
    df_slice = strava_activities_clean[strava_activities_clean['sport_type'] == activity_choice].resample(choice, closed='left').distance.sum().tail(15)
    df_slice.index = df_slice.index.strftime('%B %Y')
    #df_slice.index = df_slice.index.strftime('Week of %A, %b %d')
    st.dataframe(df_slice)

        # st.markdown(f'# Running :{emojis[0]}::{emojis[1]}::{emojis[2]}:')
        # st.subheader(f'Select a distance to see your top 5 efforts: ')
        # dists = ['2.0 mi.', '5k', '4.0 mi.', '5.0 mi.', '10k', '7.0 mi.']
        # dist = st.selectbox('Select a distance to see your top 5 efforts', dists) 

        # dist_int = [i for i in range(2,8)]
        # dist_choice = dist_int[dists.index(dist)]

        # four_milers = run[round(run.distance, 0) == dist_choice]
        
        # four_milers = four_milers[['distance', 'calories', 'pace', 'avg_run_cadence']]
        # four_milers.sort_values(by='pace', ascending=True, inplace=True)
        # st.dataframe(four_milers.head(5))

if __name__ == "__main__":
    main()
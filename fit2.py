import pandas as pd
from pandas.io.json import json_normalize
pd.options.display.max_rows = 999

import time
import datetime as dt
import numpy as np
import shutil
import os
from pathlib import Path
import requests
import json
import csv
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#import plotly.express as px
#import plotly.graph_objs as go
#import matplotlib.pyplot as plt

import streamlit as st
import time

pd.options.mode.chained_assignment = None

def main():
    # render the readme as markdown using st.markdown
    p = Path.home()
    emojis = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / 'emoji.json')

    #st.markdown(open(readme).read())
    strava_activities_raw = pd.read_csv('strava_activities.csv')

    cols_to_drop = ['Unnamed: 0', 'resource_state', 'start_date_local', 'timezone', 
    'utc_offset', 'trainer', 'commute', 'manual', 'visibility', 'flagged', 'gear_id', 'start_latlng', 'end_latlng', 'display_hide_heartrate_option',
    'upload_id_str', 'external_id', 'from_accepted_tag', 'total_photo_count', 'athlete.resource_state', 'map.id', 'map.summary_polyline', 'map.resource_state', 
    'average_watts', 'kilojoules', 'device_watts', 'heartrate_opt_out', 'upload_id', 'athlete.id', 'workout_type',
    'has_heartrate', 'location_city', 'location_state', 'location_country']

    strava_activities = strava_activities_raw.drop(labels=cols_to_drop, axis=1)

    types_of_activities = strava_activities.sport_type.unique()
    activity_choice = st.sidebar.selectbox('Select an activity', types_of_activities)

    if activity_choice == activity_choice:
        numtimes = strava_activities[strava_activities.sport_type == activity_choice].shape[0]
        st.markdown(f'###You\'ve ran {numtimes} over the past year. ')
        em = pd.read_json(emojis, orient='index')
        em = list(em.index)
        emojis = np.random.choice(em, 3)

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
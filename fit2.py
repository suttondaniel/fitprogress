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

strava_activities_raw = pd.read_csv('strava_activities.csv')

cols_to_drop = ['Unnamed: 0', 'resource_state', 'start_date_local', 'timezone', 
'utc_offset', 'trainer', 'commute', 'manual', 'visibility', 'flagged', 'gear_id', 'start_latlng', 'end_latlng', 'display_hide_heartrate_option',
'upload_id_str', 'external_id', 'from_accepted_tag', 'total_photo_count', 'athlete.resource_state', 'map.id', 'map.summary_polyline', 'map.resource_state', 
'average_watts', 'kilojoules', 'device_watts', 'heartrate_opt_out', 'upload_id', 'athlete.id', 'workout_type',
'has_heartrate', 'location_city', 'location_state', 'location_country']

strava_activities = strava_activities_raw.drop(labels=cols_to_drop, axis=1)

st.dataframe(strava_activities.head())
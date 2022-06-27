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

import plotly.express as px
import plotly.graph_objs as go
import matplotlib.pyplot as plt

import streamlit as st
import time

pd.options.mode.chained_assignment = None

def main():
    # render the readme as markdown using st.markdown
    p = Path.home()
    emojis = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / 'emoji.json')

    if os.path.exists(activities_csv_downloaded):
        download_to_raw()
    
    st.markdown(open(readme).read())

    # read in our processed activities.csv
    data = pd.read_csv(activities_csv_raw)
    data = prep_df(data)
    #data = clean_time(data)
    #data = cols_to_float(data)

    run, bike = split_run_and_bike(data)
    run = clean_run_pace(run)

    # create a clean pace column for output purposes
    run['pace'] = run.avg_pace.apply(lambda x: str(x).split(' ')[2])
    
    bike = clean_bike_pace(bike)

    # moved the activity selecter to the sidebar, will flesh out other activity monitors later
    types_of_activities = data.activity_type.unique()
    activity_choice = st.sidebar.selectbox('Select an activity', types_of_activities)
           
    if activity_choice == 'Running':
        numtimes = run.shape[0]

        em = pd.read_json(emojis, orient='index')
        em = list(em.index)
        emojis = np.random.choice(em, 3)

        st.markdown(f'# Running :{emojis[0]}::{emojis[1]}::{emojis[2]}:')
        st.subheader(f'Select a distance to see your top 5 efforts: ')
        dists = ['2.0 mi.', '5k', '4.0 mi.', '5.0 mi.', '10k', '7.0 mi.']
        dist = st.selectbox('Select a distance to see your top 5 efforts', dists) 
        
        dist_int = [i for i in range(2,8)]
        dist_choice = dist_int[dists.index(dist)]

        four_milers = run[round(run.distance, 0) == dist_choice]
        
        four_milers = four_milers[['distance', 'calories', 'pace', 'avg_run_cadence']]
        four_milers.sort_values(by='pace', ascending=True, inplace=True)
        st.dataframe(four_milers.head(5))
        
        st.subheader(f'You\'ve done this activity {numtimes} times over the last two years.  \
                         Select the number you\'d like to display: ')
        
        # '''
        # TO-DO: Flesh out the datetime slider.  it works technically, but the slider logic is backwards.  
                
        # date_min_val = run.index[0].to_pydatetime()
        # date_max_val = run.index[-1].to_pydatetime()
        # date_starter_val = run.index[5].to_pydatetime()
        # date_selected = st.slider('Select how far back you want to see: ', min_value=date_min_val, max_value=date_max_val)
        # run_slice = run[:date_selected]
        # '''

        # another TO-DO: have a select a date for the start and end of the df slice.  
        num_runs_selected = st.slider('', 1, run.shape[0], 5)
        run_slice = run.iloc[:num_runs_selected]
        #st.write(type(run_slice.distance[2]))
        # preserve the original run index....
        run_slice_index_orig = run_slice.index

        # ...then set the index to a more appealing date format, for display purposes only...
        run_slice.index = run_slice.index.strftime('%m/%d/%Y')
        st.dataframe(run_slice[['distance', 'calories', 'pace', 'avg_run_cadence']])

        #...then go head and set it right back
        run_slice.index = run_slice_index_orig
        
        num_days = (run_slice.index[0] - run_slice.index[-1]).days
        avg_miles = round(run_slice.distance.mean(), 2)
        total_miles = run_slice.distance.sum()
        mi_per_day = total_miles / num_days
        avg_pace = str(run_slice.avg_pace.mean()).split(' ')[2].split('.')[0]

        st.markdown(f'Number of days in this slice: **{num_days} days** :sunglasses:')
        st.markdown(f'Total miles ran in this slice: **{total_miles: .2f} miles** :stuck_out_tongue_winking_eye:')
        st.markdown(f'Average miles per run in this slice: **{avg_miles: .2f} miles**  :sweat_drops: :sweat_drops:')
        st.markdown(f'Average miles ran per day: **{mi_per_day: .2f} miles**  baby :video_game:')
        st.markdown(f'Average pace per run on this slice:  **{avg_pace}** :fire::fire::fire:')        
        
        # theme choices: ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

        choices = ['time', 'avg_run_cadence', 'avg_pace']
        choice = st.selectbox('Select what you would like to see', choices) 
        
        fig = px.scatter(data_frame=run_slice, 
                        y=choice,   # choice 
                        hover_data=['distance', 'calories'], 
                        labels=dict(x='Date', time='Time', avg_run_cadence='Average Run Cadence', avg_pace='Average Pace'), 
                        title='Snapshot',
                        size='distance',
                        color='distance',
                        template='plotly',
                        height=700, 
                        width=1200,
                        )
        #if choice == 'avg_pace':
            #fig.update_yaxes(tickformat='%M:%S')
        #elif choice == 'time':
            #fig.update_yaxes(tickformat='%H:%M:%S')
        
        #fig.update_xaxes(tickformat='%m/%d/%Y'),
        st.plotly_chart(fig)

        #last_15_weeks = pd.DataFrame(data[data.activity_type == 'Running'].resample('W-MON').distance.sum().tail(15))
        #st.line_chart(last_15_weeks)

def prep_df(df):
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df.drop(df.columns[17:29], axis=1, inplace=True)
    df.drop(['favorite'], axis=1, inplace=True)
    df.replace('--', '0', inplace=True)
    df.date = pd.to_datetime(df.date)
    df.set_index('date', inplace=True)
    return df

def clean_time(df):
    #df.time = df.time.split('.')[0]
   # df.time = df.time.apply()
    df.time.apply(lambda x: (lambda y: y.split(':')).insert(0, '00') if len(x) < 3 else x)
    time_pieces = df.time.apply(lambda x: x.split(':'))
    #df.time = pd.to_timedelta(df.time)
    #time = time.split('.')[0]
    #time_pieces = time.split(':')
    if len(time_pieces) < 3:
        time_pieces.insert(0, '00')
    time = ':'.join(time_pieces)
    time = dt.datetime.strptime(time, '%H:%M:%S')
    df.time = time
    return df

def cols_to_float(df):
    df.calories = df.calories.str.replace(',', '').astype(float)
    df.distance = df.distance.astype(float)
    df.iloc[:, 5:10] = df.iloc[:, 5:10].replace('--', '0')
    df.iloc[:, 5:10] = df.iloc[:, 5:10].astype(float)
    return df



def clean_run_pace(df):
    '''
    Converts our mm:ss string to a datetime object, then back to a string but in HH:MM:SS format since
    that's what to_timedelta() takes.  

    Time deltas are for durations, while datetimes are for moments in time.      
    '''
    df.best_pace = df.best_pace.apply(lambda x: dt.datetime.strptime(x, '%M:%S'))
    df.best_pace = df.best_pace.apply(lambda x: x.strftime('%H:%M:%S'))
    df.best_pace = pd.to_timedelta(df.best_pace)
    df.avg_pace = df.avg_pace.apply(lambda x: dt.datetime.strptime(x, '%M:%S'))
    df.avg_pace = df.avg_pace.apply(lambda x: x.strftime('%H:%M:%S'))
    df.avg_pace = pd.to_timedelta(df.avg_pace)
    return df

def clean_bike_pace(df):
    df.avg_pace = df.avg_pace.astype(float)
    return df

def download_to_raw():
    activities_df_downloaded = pd.read_csv(activities_csv_downloaded)
    activities_df_raw = pd.read_csv(activities_csv_raw)
    activities_df_raw = pd.concat([activities_df_downloaded, activities_df_raw]).drop_duplicates(subset='Date')
    activities_df_raw.to_csv(activities_csv_raw, index=False)
    os.remove(activities_csv_downloaded)





def split_run_and_bike(df):
    run = df[df.activity_type == 'Running']
    bike = df[df.activity_type == 'Cycling']
    return run, bike

p = Path.home()
cwd = Path.cwd()

readme = str(p / 'Documents' / 'Python' / 'fitprogress' / 'README.md')
activities_csv_downloaded = str(p / 'Downloads' / 'Activities.csv')
activities_csv_raw = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / '01_raw' / 'Activities.csv')
activities_csv_processed = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / '02_processed' / 'Activities_processed.csv')
emojis = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / 'emoji.json')

if __name__ == "__main__":
    main()

    
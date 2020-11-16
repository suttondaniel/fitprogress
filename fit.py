import pandas as pd
import datetime as dt
import numpy as np
import shutil
import os
from pathlib import Path
import plotly.express as px
import matplotlib.pyplot as plt

import streamlit as st

pd.options.mode.chained_assignment = None

def main():
    # render the readme as markdown using st.markdown
    if os.path.exists(activities_csv_downloaded):
        download_to_raw()
    
    st.markdown(open(readme).read())

    # read in our processed activities.csv
    data = pd.read_csv(activities_csv_raw)
    data = prep_df(data)
    data = clean_and_convert(data)
    run, bike = split_run_and_bike(data)
    run = clean_run_pace(run)
    bike = clean_bike_pace(bike)
    last_10 = data[['activity_type', 'distance', 'calories', 'avg_pace']].head(10)
    st.write(last_10)

    types_of_activities = data.activity_type.unique()
    activity_choice = st.selectbox('Select an activity', types_of_activities)
    
    if activity_choice == 'Running':
        last_5 = run.loc[:, ['distance', 'calories', 'time', 'avg_pace']].head()
        numtimes = run.shape[0]

    if activity_choice == 'Cycling':
        last_5 = bike.loc[:, ['distance', 'calories', 'time', 'avg_pace', 'best_pace', 'elev_gain']].head()
        numtimes = bike.shape[0]
    else:
        last_5 = data[data.activity_type == str(activity_choice)].head(5)
        numtimes = int(data.activity_type.value_counts().loc[activity_choice])
    st.subheader(f'You\'ve done this activity {numtimes} times over the last two years. Here are your last five: ')
    st.dataframe(last_5)

    if activity_choice == 'Running':
        choices = ['time', 'avg_run_cadence', 'avg_pace']
        choice = st.selectbox('Select what you would like to see', choices) 

        num_runs_selected = st.slider("Select the your last x number of runs to display pace on", 1, run.shape[0], 5)
        run_slice = run.iloc[:num_runs_selected]
        
        # theme choices: ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none"]

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
        
        fig.update_xaxes(tickformat='%m/%d/%Y'),
        st.plotly_chart(fig)

        #last_15_weeks = pd.DataFrame(data[data.activity_type == 'Running'].resample('W-MON').distance.sum().tail(15))
        #st.line_chart(last_15_weeks)

def clean_and_convert(df):
    df = clean_time(df)
    df = cols_to_float(df)
    return df

def clean_and_convert(df):
    df = clean_time(df)
    df = cols_to_float(df)
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

def prep_df(df):
    df.columns = df.columns.str.lower().str.replace(' ', '_')
    df.drop(df.columns[17:], axis=1, inplace=True)
    df.drop(['favorite'], axis=1, inplace=True)
    df.replace('--', '0', inplace=True)
    df.date = pd.to_datetime(df.date)
    df.set_index('date', inplace=True)
    return df

def clean_time(df):
    df.time = pd.to_timedelta(df.time)
    #df.time = df.time.apply(lambda x: x.split('.')[0])
    #df.time = df.time.apply(lambda x: dt.datetime.strptime(x, '%H:%M:%S'))
    #df.time = df.time.dt.time
    return df

def cols_to_float(df):
    df.calories = df.calories.str.replace(',', '').astype(float)
    df.iloc[:, 5:10] = df.iloc[:, 5:10].replace('--', '0')
    df.iloc[:, 5:10] = df.iloc[:, 5:10].astype(float)
    return df

def split_run_and_bike(df):
    run = df[df.activity_type == 'Running']
    bike = df[df.activity_type == 'Cycling']
    return run, bike

p = Path.home()
cwd = Path.cwd()
readme = cwd / 'README.md'
activities_csv_downloaded = str(p / 'Downloads' / 'Activities.csv')
activities_csv_raw = str(cwd / 'data' / '01_raw' / 'Activities.csv')
activities_csv_processed = str(cwd / 'data' / '02_processed' / 'Activities_processed.csv')


if __name__ == "__main__":
    main()

    
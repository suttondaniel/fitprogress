import requests
import pandas as pd
import time
import json

from google.cloud import bigquery

def get_df_from_bq(table_id, project_id):
    '''
    returns a dataframe of activities that are already in BQ
    '''
    client = bigquery.Client(project_id)
    table = bigquery.Table(table_id)
    bq_activities = client.list_rows(table).to_dataframe()
    bq_activities = bq_activities.set_index('start_time')
    bq_activities = bq_activities.sort_index(ascending=False) 

    return bq_activities

def create_new_bq_table(table_name, dataset_id, project_id):
    '''
    just making a function out of this to stay organized
    '''
    client = bigquery.Client(project_id)
    dataset = bigquery.Dataset(dataset_id)
    table_ref = dataset.table(table_name)
    table = bigquery.Table(table_ref)
    
    result = client.create_table(table)
    return result

def new_activities(df_existing_activities):
    '''
    returns a dataframe of new activities that need to be uploaded
    '''
    existing_activity_ids = df_existing_activities.id.values

    with open('strava_tokens.json') as json_file:
        strava_tokens = json.load(json_file)

    if strava_tokens['expires_at'] < time.time():
        response = requests.post(
                            url = 'https://www.strava.com/oauth/token',
                            data = {
                                    'client_id': strava_tokens['client_id'],
                                    'client_secret': strava_tokens['client_secret'],
                                    'grant_type': 'refresh_token',
                                    'refresh_token': strava_tokens['refresh_token']
                                    }
                        ) 
        new_strava_tokens = response.json() 
        with open('strava_tokens.json', 'w') as outfile:
            json.dump(new_strava_tokens, outfile)
        strava_tokens = new_strava_tokens

    page = 1
    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens['access_token']
    
    df_new_activities = pd.DataFrame()

    # each page includes 200 activities
    r = requests.get(url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page))
    r = r.json()
    r_df = pd.DataFrame.from_dict(r, orient='columns')
    r_df = prepare_data(r_df)

    # keep just the activities that are not in our database
    df_new_activities = r_df[~r_df.id.isin(existing_activity_ids)]
    return df_new_activities

def prepare_data(df):

    # going to include start_latlng and end_latlng
    cols_to_keep = ['name', 'distance', 'moving_time', 'elapsed_time', 'total_elevation_gain', 'sport_type', 'id', 'start_date', 'achievement_count',
       'kudos_count', 'comment_count', 'athlete_count', 'average_heartrate', 'max_heartrate']

    activities = df[cols_to_keep]

    rename = {'start_date': 'start_time'}
    activities.rename(rename, axis=1, inplace=True)

    # meters to miles
    activities['distance'] = activities.distance * .000621

    # meters to feet
    activities['total_elevation_gain'] = activities['total_elevation_gain'] * 3.28084

    # have to manually adjust one activity; the run was on 6/12 not 6/13
    #strava_activities_clean.loc[strava_activities_clean.id == 7299973019, 'start_time'] = pd.Timestamp(year=2022, month=6, day=12, hour=2, minute=8, second=36, tz='UTC')
    activities['start_time'] = pd.to_datetime(activities['start_time'])

    #strava_activities_clean.set_index('start_time', inplace=True)
    activities.set_index('start_time', inplace=True)

    return activities


def get_all_activities(csv_file):
    '''
    I need to repurpose this for the cloud; it shouldnt need to take in a .csv in order to output a .csv
    but those are the least of my worrieS;  get a PoC by uploading a .csv to BQ via an offline script first
    then find a way to do it with a cloud function later

    1/6/23: keeping this function if I ever want to download all of my activities. otherwise 
    "new_activities" will do moving forward
    '''
    with open('strava_tokens.json') as json_file:
        strava_tokens = json.load(json_file)

    if strava_tokens['expires_at'] < time.time():
        response = requests.post(
                            url = 'https://www.strava.com/oauth/token',
                            data = {
                                    'client_id': 88709,
                                    'client_secret': '54dab45b88619205ee1e47eb94d0f2d84762a4b2',
                                    'grant_type': 'refresh_token',
                                    'refresh_token': strava_tokens['refresh_token']
                                    }
                        ) 
        new_strava_tokens = response.json() 
        with open('strava_tokens.json', 'w') as outfile:
            json.dump(new_strava_tokens, outfile)
        strava_tokens = new_strava_tokens

    page = 1
    url = "https://www.strava.com/api/v3/activities"
    access_token = strava_tokens['access_token']

    activities = pd.read_csv(csv_file)

    while True:
        r = requests.get(url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page))
        r = r.json()
        r_df = pd.DataFrame.from_dict(r, orient='columns')     
    
        # if there are no new values (i.e. activities) found in r_df, just break.  otherwise keep going
        if len([v for v in list(r_df['id']) if v not in list(activities['id'])]) == 0:
            activities.drop_duplicates(subset=['id'], inplace=True)
            activities.sort_values(by='id', ascending=False, inplace=True)
            activities.to_csv(csv_file, index=False)
            return activities

        if (not r):   # if no results then exit loop
            break
            
        activities = pd.concat([r_df, activities])
        page += 1
    
    activities.drop_duplicates(subset=['id'], inplace=True)
    activities.sort_values(by='id', ascending=False, inplace=True)
    activities.to_csv(csv_file, index=False)
    return activities
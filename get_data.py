import pandas as pd

def prepare_data(df):

    # going to include start_latlng and end_latlng
    cols_to_drop = ['Unnamed: 0.1', 'athlete', 'resource_state', 'start_date_local', 'timezone', 
    'utc_offset', 'trainer', 'commute', 'type', 'manual', 'visibility', 'flagged', 'gear_id', 'display_hide_heartrate_option',
    'upload_id_str', 'external_id', 'from_accepted_tag', 'total_photo_count', 'athlete.resource_state', 'map.id', 'map.summary_polyline', 'map.resource_state', 
    'average_watts', 'kilojoules', 'device_watts', 'photo_count', 'heartrate_opt_out', 'upload_id', 'athlete.id', 'workout_type',
    'has_heartrate', 'location_city', 'location_state', 'location_country', 'private', 'has_kudoed', 'Unnamed: 0']

    strava_activities_clean = df.drop(labels=cols_to_drop, axis=1)

    # meters to miles
    strava_activities_clean['distance'] = strava_activities_clean.distance * .000621

    # meters to feet
    for column in ['total_elevation_gain', 'elev_high', 'elev_low']:
        strava_activities_clean[column] = strava_activities_clean[column] * 3.28084

    # search results for my pace (pick a pace, any pace) and see my suffering go down over time
    # might be a fun metric to plot over time. perhaps my suffering per minute has gone down as ive gotten fitter
    strava_activities_clean['SPM'] = strava_activities_clean.suffer_score / (strava_activities_clean.moving_time / 60)

    rename = {'start_date': 'start_time'}
    strava_activities_clean.rename(rename, axis=1, inplace=True)

    # convert start_time to pandas Timestamp object. then we can access seconds, minutes, hours, etc. and can add the moving_time
    strava_activities_clean['start_time'] = pd.to_datetime(strava_activities_clean['start_time'])

    # have to manually adjust one activity; the run was on 6/12 not 6/13
    strava_activities_clean.loc[strava_activities_clean.id == 7299973019, 'start_time'] = pd.Timestamp(year=2022, month=6, day=12, hour=2, minute=8, second=36, tz='UTC')

    strava_activities_clean.set_index('start_time', inplace=True)

    return strava_activities_clean


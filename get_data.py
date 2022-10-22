import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapiExercises")     # initialize Nominatim API

def get_float_coords(elem):
    '''
    converts the latitude / longitude from a string that looks like a list to a functioning list of two floats
    '''
    try:
        return [float(coord) for coord in elem.split('[')[1].split(']')[0].split(',')]
    except ValueError:
        return np.nan

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

    strava_activities_clean['start_latlng'] = strava_activities_clean['start_latlng'].apply(get_float_coords)

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

def city_state_county(row):
    try:
        lat = row['start_latlng'][0]
        long = row['start_latlng'][1]
        coord = f"{str(lat)}, {str(long)}"
        location = geolocator.reverse(coord, exactly_one=True)
        address = location.raw['address']
        city = address.get('city', 'N/A')
        state = address.get('state', 'N/A')
        county = address.get('county', 'N/A')
        row['city'] = city
        row['state'] = state
        row['county'] = county
    except TypeError:
        return np.nan
    return row


def to_time_readout(element):
    time = element / 60 / 60
    hrs = int(time)
    mins = (time - hrs) * 60
    return f'{int(round(hrs, 0))}h {int(mins)}m'

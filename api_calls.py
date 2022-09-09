import requests
import pandas as pd
import time
import json

def get_strava_data(csv_file):
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
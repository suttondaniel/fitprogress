### Strava Activities Dashboard

[Link to Strava Dashboard on Tableau](https://public.tableau.com/app/profile/daniel.sutton/viz/StravaDashboard_16722004506040/StravaDashboard2)

I wanted to keep track of how many miles I had run in a given year and compare it to all previous years.  I also wanted to have a dashboard that would show me my mileage and elevation gain in a given time period, instead of just YTD as shown in the Strava app.  

Strava allows you to request an archive of your activities that come in a .csv format.  However, this does not come immediately, and as such was not ideal for my purposes.  I could also export my activites to .csv through Garmin Connect, which was much easier but still not ideal for data extraction.  

Enter the Strava API.  Instead of logging onto Garmin Connect and manually downloading my activities once or twice a week, I was now able to pull them down via the API and do the necessary aggregations and datacleaning.  

And instead of working locally in a bunch of .csvs, I wanted to host my activities in a cloud warehouse.  I chose Google's BigQuery given my familiarity with their other products.  After loading an initial .csv to a BigQuery project, I now have a pipeline that starts with the Strava API and ends with a Tableau dashboard.  The script proceeds as follows:  

### 1) Pull existing activities down from BigQuery and into a pandas dataframe: 

```python
def get_df_from_bq(table_id, project_id):

    client = bigquery.Client(project_id)
    table = bigquery.Table(table_id)
    bq_activities = client.list_rows(table).to_dataframe()
    bq_activities = bq_activities.set_index('start_time')
    bq_activities = bq_activities.sort_index(ascending=False) 

    return bq_activities
```

### 2) Compare existing activities to the Strava API output and receive back a dataframe of new activities: 

```python
def new_activities(df_existing_activities):

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
```
### 3) Push new activities back up to BigQuery: 
```python
client.load_table_from_dataframe(new_activities, table)
```

### 4) Connect the BigQuery data source to Tableau and visualize away: 
![dashboard](https://github.com/suttondaniel/fitprogress/blob/master/images/strava_db_1_6_23.png)









To-do list for future iterations: 
1. Move script to a Google Cloud Function so it can run periodically on its own
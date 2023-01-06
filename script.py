#from api_calls import get_strava_data, get_df_from_bq, new_activities, prepare_data
from api_calls import *
import pandas as pd
from google.cloud import bigquery


def main():
    project_id = 'playground-371704'
    client = bigquery.Client(project_id)

    dataset_id = 'playground-371704.grocery1'
    dataset = bigquery.Dataset(dataset_id)

    table_id = 'playground-371704.grocery1.activities_5'
    table = bigquery.Table(table_id)

    # pull down existing activities from BQ
    df_from_bq = get_df_from_bq(table_id, project_id)

    # compare existing activities to strava API output and receive back a df of new activities only
    new_activities = new_activities(df_from_bq)

    # upload new activities to BQ
    client.load_table_from_dataframe(new_activities, table)


if __name__ == "__main__":
    main()
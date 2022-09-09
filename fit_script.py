import pandas as pd
from get_data import prepare_data


from pathlib import Path

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
pd.options.mode.chained_assignment = None

import streamlit as st


def main():
    # render the readme as markdown using st.markdown
    p = Path.home()
    emojis = str(p / 'Documents' / 'Python' / 'fitprogress' / 'data' / 'emoji.json')

    activities = prepare_data()

    types_of_activities = activities.sport_type.unique()

    runs = activities[activities['sport_type'] == 'Run']
    runs_2022 = runs[runs.index.year == 2022]

    st.title('Running Dashboard')

    miles_run = runs_2022.distance.sum()
    elev_gain = runs_2022.total_elevation_gain.sum()
    mpd = runs_2022.distance.sum() / runs_2022.index[0].day_of_year
    
    col1, col2, col3 = st.columns(3)

    # you can pass in a percentage or $ amt as a second variable to show growth or shrinkage over time

    #col1.metric("Miles Ran", miles_run, "-$1.25")
    col1.metric("Miles Ran (YTD)", round(miles_run, 2))
    col2.metric("Elevation Gain (YTD)", round(elev_gain, 2))
    col3.metric("Miles Per Day", round(mpd, 2))

    activity_choice = st.sidebar.selectbox('Select an activity', types_of_activities)
           
    if activity_choice == 'Run':
        choices = {'W-Mon': '%A, %b %d %Y', 'M': '%B %Y', 'Y': '%Y'}
        choices_txt = {'By Week': 'W-Mon', 'By Month': 'M', 'By Year': 'Y'}

        choice_selector = st.radio('Totals by Week, Month, or Year', choices_txt.keys())
        choice = choices_txt[choice_selector]

        # #strava_activities_clean[strava_activities_clean['sport_type'] == 'Run'].resample('W-Mon', closed='left').distance.sum().tail(15)
        df_slice = activities[activities['sport_type'] == activity_choice].resample(choice, closed='left').distance.sum().tail(5)
        #df_slice.index = df_slice.index.strftime('%B %Y')
        df_slice.index = df_slice.index.strftime(choices[choice])
        st.dataframe(df_slice)

                # #strava_activities_clean[strava_activities_clean['sport_type'] == 'Run'].resample('W-Mon', closed='left').distance.sum().tail(15)
        df_slice_2 = activities[activities['sport_type'] == activity_choice].resample(choice, closed='left')[['distance', 'total_elevation_gain']].sum().tail(5)
        #df_slice.index = df_slice.index.strftime('%B %Y')
        df_slice_2.index = df_slice_2.index.strftime(choices[choice])
        st.dataframe(df_slice_2)


    
    
    # TALLY HOW MANY TIMES YOU DID THE ACTIVITY
    # if activity_choice == activity_choice:
    #     numtimes = strava_activities_clean[strava_activities_clean.sport_type == activity_choice].shape[0]
    #     em = pd.read_json(emojis, orient='index')
    #     em = list(em.index)
    #     emojis = np.random.choice(em, 3)
    #     st.markdown(f'### You\'ve {activity_choice} {numtimes} times over the past 3 years :{emojis[0]}::{emojis[1]}::{emojis[2]}:')

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
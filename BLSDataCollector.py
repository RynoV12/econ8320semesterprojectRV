# Import necessary libraries
import streamlit as st
import pandas as pd
import requests
import json

# Retrieval of series data
@st.cache_data(ttl = "1d") # Caches json_data for 24 hours
def collect_bls_data():
    headers = {'Content-type': 'application/json'}
    data = json.dumps({"seriesid": ['LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001'],"startyear":"2022", "endyear":"2024"})
    p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
    json_data = json.loads(p.text)
    return json_data

# Iterate over the JSON response and extract data from each inputted series
@st.cache_data(ttl = "1d") # Caches dataframes_dict data for 24 hours
def process_bls_data(json_data):
    dataframes_dict = {}
    for series in json_data['Results']['series']:
        series_id = series['seriesID']
        parsed_data = []

        # Setting variables equal to collected data frame columns
        for item in series['data']:
            year = item['year']
            period = item['period']
            value = item['value']
            footnotes = ",".join(footnote['text'] for footnote in item['footnotes'] if footnote)

            # Creation of a dictionary with the common BLS series data labels
            row_data = {
                'seriesID': series_id,
                'year': year,
                'period': period,
                'value': value,
                'footnotes': footnotes,
            }

            # Add row_data dictionary to empty parsed_data list
            parsed_data.append(row_data)

        # Creation of a data frame for the current series
        columns = ['seriesID', 'year', 'period', 'value', 'footnotes']
        data = [[entry.get(i, None) for i in columns] for entry in parsed_data]
        df = pd.DataFrame(data, columns=columns)

        # Changing and reformatting values for columns
        df['value'] = pd.to_numeric(df['value'])
        df['month'] = pd.to_numeric(df['period'].replace({'M': ''}, regex=True))
        df['date'] = pd.to_datetime(df['month'].map(str) + '-' + df['year'].map(str), format='%m-%Y')
        df = df.sort_values(by=['date'], ascending=True)

        # Reordering of the data frame's columns
        df = df[['date', 'value', 'seriesID', 'year', 'month', 'period', 'footnotes']]

        # Resetting the index to start from 0
        df.reset_index(drop=True, inplace=True)

        # Replacing any empty strings with NaN
        df.replace('', pd.NA, inplace=True)

        # Dropping columns with values of NaN or pd.NA
        df = df.dropna(axis=1, how='all')

        # Adding the data frame to the dictionary with the Series ID as the key
        dataframes_dict[series_id] = df

    # Return the dictionary of data frames
    return dataframes_dict

# Setting variables equal to the results of the collection and processing functions
json_data = collect_bls_data()
dataframes_dict = process_bls_data(json_data)

# Label the data frames corresponding to each series
civ_emp_df = dataframes_dict['LNS12000000']
civ_unemp_df = dataframes_dict['LNS13000000']
unemp_rt_df = dataframes_dict['LNS14000000']
nonfarm_emp_df = dataframes_dict['CES0000000001']

# Addition of title and header in Streamlit
st.title('ECON 8320 Fall 2024 Semester Project - Ryan Vilter')
st.header(':flag-us: _:red[U.S.] Bureau of Labor Statistics :blue[Data]_ :flag-us:')

# Add data frames and labels to the Streamlit dashboard
st.subheader("Civilian Employment Data (Numbers in Thousands), 2022-2024", divider = "red")
st.dataframe(civ_emp_df)

st.subheader("Civilian Unemployment Data (Numbers in Thousands), 2022-2024", divider = "red")
st.dataframe(civ_unemp_df)

st.subheader("Unemployment Rate Data (Numbers in Thousands), 2022-2024", divider = "red")
st.dataframe(unemp_rt_df)

st.subheader("Nonfarm Employment Data (Numbers in Thousands), 2022-2024", divider = "red")
st.dataframe(nonfarm_emp_df)

# Plot dataframes as line charts and label them in the Streamlit dashboard
st.subheader("Civilian Employment, 2022-2024", divider = "blue")
st.line_chart(civ_emp_df,
             x='month',
             y='value',
             x_label='Month',
             y_label='Number of Employed Civilians (in Thousands)',
             color='year')

st.subheader("Civilian Unemployment, 2022-2024", divider = "blue")
st.line_chart(civ_unemp_df,
             x='month',
             y='value',
             x_label='Month',
             y_label='Number of Unemployed Civilians (in Thousands)',
             color='year')

st.subheader("Unemployment Rate, 2022-2024", divider = "blue")
st.line_chart(unemp_rt_df,
             x='month',
             y='value',
             x_label='Month',
             y_label='Unemployment Rate',
             color='year')

st.subheader("Nonfarm Employment, 2022-2024", divider = "blue")
st.line_chart(nonfarm_emp_df,
             x='month',
             y='value',
             x_label='Month',
             y_label='Number of Nonfarm Workers (in Thousands)',
             color='year')

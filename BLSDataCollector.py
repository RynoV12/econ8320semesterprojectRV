# Import necessary libraries
import streamlit as st
import pandas as pd
import requests
import json

dataframes_dict = {}
headers = {'Content-type': 'application/json'}

# Retrieval of series data
data = json.dumps({"seriesid": ['LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001'],"startyear":"2023", "endyear":"2024"})
p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', data=data, headers=headers)
json_data = json.loads(p.text)

# Iterate over the JSON response and extract data from each inputted series
for series in json_data['Results']['series']:
    series_id = series['seriesID']
    parsed_data = []

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

        parsed_data.append(row_data)

    # Creation of a dataframe for the current series
    columns = ['seriesID', 'year', 'period', 'value', 'footnotes']
    data = [[entry.get(i, None) for i in columns] for entry in parsed_data]
    df = pd.DataFrame(data, columns=columns)

    df['value'] = pd.to_numeric(df['value'])
    df['month'] = pd.to_numeric(df['period'].replace({'M': ''}, regex=True))
    df['date'] = pd.to_datetime(df['month'].map(str) + '-' + df['year'].map(str), format='%m-%Y')
    df = df.sort_values(by=['date'], ascending=True)

    # Reordering of the dataframe's columns
    df = df[['date', 'value', 'seriesID', 'year', 'month', 'period', 'footnotes']]

    # Resetting the index to start from 0
    df.reset_index(drop=True, inplace=True)

    # Replacing any empty strings with NaN
    df.replace('', pd.NA, inplace=True)

    # Dropping columns with values of NaN or pd.NA
    df = df.dropna(axis=1, how='all')

    # Adding the dataframe to the dictionary with the Series ID as the key
    dataframes_dict[series_id] = df

# Create dataframes for each series
civ_emp_df = dataframes_dict['LNS12000000']
civ_unemp_df = dataframes_dict['LNS13000000']
unemp_rt_df = dataframes_dict['LNS14000000']
nonfarm_emp_df = dataframes_dict['CES0000000001']

# Addition of title and header in Streamlit
st.title('ECON 8320 Fall 2024 Semester Project - Ryan Vilter')
st.header('_:red[U.S.] Bureau of Labor Statistics :blue[Data]_ :flag_us:')

# Add data frames and labels to my Streamlit dashboard
st.subheader("Civilian Employment Data Frame", divider = "blue")
st.dataframe(civ_emp_df)

st.subheader("Civilian Unemployment Data Frame", divider = "blue")
st.dataframe(civ_unemp_df)

st.subheader("Unemployment Rate Data Frame", divider = "blue")
st.dataframe(unemp_rt_df)

st.subheader("Nonfarm Employment Data Frame", divider = "blue")
st.dataframe(nonfarm_emp_df)

# Plot dataframes as bar charts and label them in my Streamlit dashboard
st.subheader("Civilian Employment Line Chart", divider = "red")
st.line_chart(civ_emp_df,
             x=['month', 'year']
             y='value',
             x_label='Civilian Employment per Month and Year',
             y_label='Number of Employed Civilians',
            color = 'year')

st.subheader("Civilian Unemployment Line Chart", divider = "red")
st.line_chart(civ_unemp_df,
             x=['month', 'year']
             y='value',
             x_label='Civilian Unemployment per Month and Year',
             y_label='Number of Unemployed Civilians',
            color = 'year')

st.subheader("Unemployment Rate Line Chart", divider = "red")
st.line_chart(unemp_rt_df,
             x=['month', 'year'],
             y='value',
             x_label='Unemployment Rate per Month and Year',
             y_label='Unemployment Rate',
             color = 'year')

st.subheader("Nonfarm Employment Line Chart", divider = "red")
st.line_chart(nonfarm_emp_df,
             x=['month', 'year'],
             y='value',
             x_label='Nonfarm Worker Employment per Month and Year',
             y_label='Number of Nonfarm Workers',
             color = 'year')

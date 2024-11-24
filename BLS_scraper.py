import streamlit as st
from streamlit.connections import BaseConnection
import requests
import pandas as pd
import json

class BLSScraper(BaseConnection):
    def __init__(self, connection_name, **kwargs): #Initializes the BLSScraper object
        super().__init__(connection_name=connection_name, **kwargs)

    # Implementation of connection setup
    def _connect(self, **kwargs):
        pass

    # Collection of BLS data and returning a dictionary of dataframes
    def collectblsdata(self, series_ids, start_year, end_year, api_key=None, **kwargs):
        dataframes_dict = {}
        headers = {
            'Content type': 'application/json',
        }

        # Payload of required parameters
        payload = {
            "series": series_ids,
            "start_year": start_year,
            "end_year": end_year,
            "api_key": api_key,
        }

        # Updated payload with additional parameters via **kwargs
        payload.update(kwargs)

        # API request made using the post method with the payload
        try:
            p = requests.post('https://api.bls.gov/publicAPI/v2/timeseries/data/', json=payload, headers=headers)
            if p.status_code == 200: # Checking for a successful response code
                if p.text_strip(): # Making sure the response isn't empty before parsing
                    try:
                        json_data = json.loads(p.text)
                        print("Successfully parsed JSON:", json_data)
                    except:
                        print("Response is not valid JSON!")
                else:
                    print("Response body is empty!")
            else:
                print(f"Request failed with status code: {p.status_code}")
        except requests.RequestException as e:
            print (f"An error occurred while making the POST request: {e}"

        # Iterate over the JSON response and extract data from each inputted series
        for series in json_data['Results']['series']:
            series_id = series['seriesID']
            parsed_data = []

            # Extraction of catalog data from current series if applicable
            series_title = series.get('catalog', {}).get('series_title')
            survey_name = series.get('catalog', {}).get('survey_name')

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
                    'series_title': series_title,
                    'survey_name': survey_name,
                    'catalog': series.get('catalog'),
                    'calculations': item.get('calculations'),
                    'annualaverage': item.get('annualaverage'),
                    'aspects': item.get('aspects')
                }

                parsed_data.append(row_data)

            # Creation of a dataframe for the current series
            columns = ['Series ID', 'Year', 'Period', 'Value', 'Catalog', 'Calculations', 'Annual Average', 'Aspects', 'Footnotes']
            data = [[entry.get(i, None) for i in columns] for entry in parsed_data]
            df = pd.DataFrame(data, columns=columns)

            df['value'] = pd.to_numeric(df['value'])
            df['month'] = pd.to_numeric(df['period'].replace({'M': ''}, regex=True))
            df['date'] = pd.to_datetime(df['month'].map(str) + '-' + df['year'].map(str), format='%m-%Y')
            df = df.sort_values(by=['date'], ascending=True)
            df['%_change_value'] = df['value'].pct_change()

            # Reordering of the dataframe's columns
            df = df[['date', 'value', '%_change_value', 'seriesID', 'series_title', 'year', 'month', 'period', 'survey_name', 'catalog', 'calculations', 'annualaverage', 'aspects', 'footnotes']]

            # Resetting the index to start from 0
            df.reset_index(drop=True, inplace=True)

            # Replacing any empty strings with NaN
            df.replace('', pd.NA, inplace=True)

            # Dropping columns with values of NaN or pd.NA
            df = df.dropna(axis=1, how='all')

            # Adding the dataframe to the dictionary with the Series ID as the key
            dataframes_dict[series_id] = df

        return dataframes_dict

    @classmethod
    @st.cache_data(ttl="3600") # Caches the data for 3600 seconds (1 hour)

    # Collection of data from the BLS API
    # The api_key argument is set to none as BLS V1 series do not require an API key
    def query(cls, series_ids, start_year, end_year, api_key=None, **kwargs):
        try:
            connection = cls("bls_connection")

            dataframes_dict = connection.collectblsdata(
                series_ids=series_ids,
                start_year=start_year,
                end_year=end_year,
                api_key=api_key, # Pass the API key or set it to None
                **kwargs         # Pass any other keyword arguments
            )
            return dataframes_dict
        except KeyError:
            with st.sidebar:
                st.error("Failed to collect latest data. Query limit has been reached.")
            return None

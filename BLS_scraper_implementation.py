import streamlit as st
from BLS_scraper import BLSScraper

# Set up a connection to the BLS website
bls_conn = st.connection('bls', type=BLSScraper)

# Input parameters
series_ids_list = ['LNS12000000', 'LNS13000000', 'LNS14000000', 'CES0000000001']
start_year_str = '2019'
end_year_str = '2024'

# Collect data using the established connection
dataframes_dict = bls_conn.query(series_ids_list,
                                   start_year_str,
                                   end_year_str,
                                   api_key=None)

# Create dataframes
civ_emp_df = dataframes_dict['LNS12000000']
civ_unemp_df = dataframes_dict['LNS13000000']
unemp_rt_df = dataframes_dict['LNS14000000']
nonfarm_emp_df = dataframes_dict['CES0000000001']

# Addition of title and header in Streamlit
st.title('ECON 8320 Fall 2024 Semester Project - Ryan Vilter')
st.header('U.S. Bureau of Labor Statistics')

# Plot dataframes as bar charts in my Streamlit dashboard
st.bar_chart(civ_emp_df,
             x='month',
             y='year',
             x_label='Civilian Employment per Month',
             y_label='Civilian Employment per Year (2019-2024)')
st.bar_chart(civ_unemp_df,
             x='month',
             y='year',
             x_label='Civilian Unemployment per Month',
             y_label='Civilian Unemployment per Year (2019-2024)')
st.bar_chart(unemp_rt_df,
             x='month',
             y='year',
             x_label='Unemployment Rate per Month',
             y_label='Unemployment Rate per Year (2019-2024)')
st.bar_chart(nonfarm_emp_df,
             x='month',
             y='year',
             x_label='Nonfarm Worker Employment per Month',
             y_label='Nonfarm Worker Employment per Year (2019-2024)')
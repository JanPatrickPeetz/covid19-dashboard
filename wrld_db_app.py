from enum import auto
from multiprocessing.sharedctypes import Value
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import altair as alt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import streamlit as st
from millify import millify
from numerize import numerize
from prophet import Prophet


#### page settings
st.set_page_config(page_title= 'Covid-19 Dashboard', 
# wide page layout to display all I want
layout= 'wide',
# side bar should be collapsed at first
initial_sidebar_state='expanded')


def main():


    #####Get the Data from WHO

    # Loading WHO by Date data
    df_data_by_date  = pd.read_csv("data/WHO-COVID-19-global-data.csv", delimiter=",", decimal=",",thousands=".")

    # Setting column names and first row as index and first column as non numeric index
    colnames = ['Name', 'WHORegion', 'TotalCases', '100000Cases',
    'Cases7Days', '100000Cases7Days', '24HCases', 'TotalDeaths',
    '100000Deaths', 'Deaths7Days', '100000Deaths7Days', '24HDeaths']

    #Loading covid-19 data
    #!Note before importing data from WHO the last comma in second row needs to be deleted. Otherwise Pandas interprets the data wrong
    df_data_country = pd.read_csv('data/WHO-COVID-19-global-table-data.csv',delimiter=",", decimal=",",thousands=",",names=colnames, header=0, index_col=('Name'))

    # Loading table with country positions
    df_country_pos = pd.read_csv("data/world_country_and_usa_states_latitude_and_longitude_values.csv",delimiter=",", decimal=",",thousands=",", index_col=3)

    # Loading Vaccination table
    df_vacc = pd.read_csv('data/vaccination-data.csv', thousands=',')



    #####Preparing Data for output; data wrangling
    
    # Adding new columns CasesDiff, DeathsDiff, smoothcases and smoothdeath to data_by_date
    # Preparing data for metrics output: difference between new_cases in rows; dropping emtpy and convert to integer
    df_data_by_date['CasesDiff'] = df_data_by_date['New_cases'].diff().fillna(0).astype(int)
    # Preparing data for metrics output: difference between new_deaths in rows; dropping emtpy and convert to integer
    df_data_by_date['DeathsDiff'] = df_data_by_date['New_deaths'].diff().fillna(0).astype(int)
    # Adding smoothing for 7 days to data
    df_data_by_date['smoothcases'] = df_data_by_date['New_cases'].rolling(7).mean()
    df_data_by_date['smoothdeath'] = df_data_by_date['New_deaths'].rolling(7).mean()

    # handling of df_country_pos
    #dropping columns 'usa_state_code', 'usa_state_latitude', 'usa_state_longitude', 'usa_state' from table --> not further needed
    df_country_pos = df_country_pos.drop(['usa_state_code', 'usa_state_latitude', 'usa_state_longitude', 'usa_state'], axis=1)

    #handling of df_data_country
    #Concat tables df_data_country and df_country_pos into df_data_country
    df_data_country = pd.concat([df_data_country, df_country_pos], axis=1).reindex(df_data_country.index)
    # setting datatypes for columns
    df_data_country['100000Cases7Days'] = df_data_country['100000Cases7Days'].astype(float).round(2)
    # drop all rows where latitude = <NA>
    df_data_country = df_data_country.dropna(0, subset=['country_code'])

    #Calculate mortality rate: cum.death/cum.cases *100
    df_data_country['mortalityrate'] = df_data_country['TotalDeaths'].div(df_data_country.TotalCases, fill_value=0)
    df_data_country['mortalityrate'] = df_data_country['mortalityrate'] * 100
    df_data_country['mortalityrate'] = df_data_country['mortalityrate'].fillna(0)


    ## Handling of vaccination dataframe
    # Handling of datatype for columns
    df_vacc['PERSONS_FULLY_VACCINATED_PER100'] = df_vacc['PERSONS_FULLY_VACCINATED_PER100'].astype(float)
    # groupby WHO regions
    df_vacc = df_vacc.groupby('WHO_REGION').mean()
    #drop others index row
    df_vacc =df_vacc.drop('OTHER')
    # reindex index names
    df_vacc = df_vacc.rename(index={'AFRO':'Africa', 'AMRO':'Americas', 'EMRO':'Eastern Mediterranean', 'EURO':'Europe', 'SEARO':'South-East Asia', 'WPRO':'Western Pacific'})


    # get newest date for setting max range
    actualdate = df_data_by_date['Date_reported'].max()


    # Define table for output
    df_KPI_table = df_data_country.drop(columns=['country_code', 'latitude', 'longitude', '100000Cases', 'Cases7Days', '100000Deaths', 'Deaths7Days', '100000Deaths7Days'])
    df_KPI_table['TotalCases'] = df_KPI_table['TotalCases'].astype(int).round(0)
    df_KPI_table['24HCases'] = df_KPI_table['24HCases'].astype(int)
    df_KPI_table['TotalDeaths'] = df_KPI_table['TotalDeaths'].astype(int) 
    df_KPI_table['24HDeaths'] = df_KPI_table['24HDeaths'].astype(int)

    


    ##### Output data - Printing Graphs
    #set page title
    st.title('Global Covid-19 Dashboard')

    col1, col2 = st.columns(2)

    # Define selectbox for country to be displayed
    with col1:
        st.caption('Last update on ' + actualdate)
    col2.empty()

    col1,col2 = st.columns(2)
    with col1:
        option_country = st.selectbox('Which country would you like to see?', options=df_data_country.index)
    country_selector = df_data_by_date.query("Country == @option_country")
    col2.empty()
        



    #Further data handling for output
    # get data series of dataframe with newest date
    ds_country_selector = country_selector.query('Date_reported == @actualdate')
    
    # drop 3 times mindate due to falsified data
    i = 1
    while i <= 3:
        mindate = country_selector['Date_reported'].min()
        country_selector = country_selector[country_selector.Date_reported != mindate]
        i += 1


    #selecting mortalityrate
    mortrate = df_data_country['mortalityrate'].filter(like=option_country, axis=0).round(3)
    
    st.markdown('***')

   #Print metrics in columns
    metr_cont = st.container()
    with metr_cont:
        #TODO fix formatting of metrices
        st.subheader('Key figures from ' + actualdate + ' of ' + option_country)
        col1, col2,  col3, col4 =  st.columns(4)
        col1.metric(label = '7 Day Incidence per 100k population', value=(df_data_country['100000Cases7Days'].filter(like=option_country)))
        col2.metric(label = 'New cases compared to last day', value=(ds_country_selector.New_cases),delta=ds_country_selector.CasesDiff.astype(int).item(), delta_color='inverse')
        col3.metric(label = 'New deaths compared to last day', value=(ds_country_selector.New_deaths), delta=ds_country_selector.DeathsDiff.astype(int).item(),delta_color='inverse')
        col4.metric(label = 'Mortality Rate in %', value=(mortrate))

    st.markdown('***')
    
    
    #plotly graph line/bar chart
    fig_case= go.Figure()

    fig_case.add_trace(
        go.Line(
            x=country_selector['Date_reported'],
            y=country_selector['smoothcases'],
            name='Smoothed cases per 7 days',
            marker_color= 'rgb(0,0,255)',
            ))
    
    fig_case.add_trace(
        go.Bar(
            x=country_selector['Date_reported'],
            y=country_selector['New_cases'],
            name='New cases per day',
            marker_color= 'darkblue',
    ))
        
    fig_case.update_layout(
        width=1300,
        yaxis=dict(title='New Cases')
        #title='New cases per day for ' + option_country,
    )
    col1,col2 = st.columns(2)
    col1.subheader('New cases per day of ' + option_country)
    col2.metric(label = 'Cumulated Cases',value=(ds_country_selector.Cumulative_cases))
    st.write(fig_case)




    ##printing death data line chart
    fig_death = go.Figure()
    fig_death.add_trace(
        go.Line(
            x=country_selector['Date_reported'],
            y=country_selector['smoothdeath'],
            name='Smoothed deaths per 7 days',
            marker_color = 'indianred',
            ))

    fig_death.add_trace(
        go.Bar(
            x=country_selector['Date_reported'],
            y=country_selector['New_deaths'],
            name='New deaths per day',
            marker_color = 'lightsalmon'))

    fig_death.update_layout(
        #title='New deaths per day for ' + option_country,
        width=1300,
        yaxis=dict(title='New Deahts')
    )
    col1, col2 = st.columns(2)
    col1.subheader('New deaths per day of ' + option_country)
    col2.metric(label = 'Cumulated deaths',value=(ds_country_selector.Cumulative_deaths))
    st.write(fig_death)
    
    st.markdown('***')

    map_cont = st.container()
    with map_cont:
            st.subheader('Actual 7 day incidence per 100k population')
            show_country = st.radio(
            "What do you want to see in the map?",
            ('Actual country', 'All countries'))
            if show_country == 'Actual country':
                country_choice = df_data_country.query('index == @option_country').index
                z_country = df_data_country['100000Cases7Days'].filter(like=option_country).round(1)
            elif show_country == 'All countries':
                country_choice = df_data_country.index
                z_country = df_data_country['100000Cases7Days'].round(1)
    
    
# show totalcases world map
    fig_map = go.Figure(
                data=go.Choropleth(
                locationmode = 'country names',
                locations= country_choice,
                #locations= df_data_country['Name'].filter(like=option_country),
                z= z_country,
                zmin = df_data_country['100000Cases7Days'].min(), # defining min value for colorscale
                zmax = df_data_country['100000Cases7Days'].max(), # defining max value for colorscale
                #text = df_data_country['Name'].filter(like=option_country),
                text = country_choice, 
                colorscale = 'blues',

            ))
    fig_map.update_layout(
                geo=dict(
                    showframe=False,
                    showcoastlines=False,
                    projection_type='kavrayskiy7',
                    #bgcolor='#262730',
                ),
                #autosize=True,
                width=1300,
                #height=600,
                margin={"r":0,"t":0,"l":0,"b":0},
                autosize=False,
                hovermode='closest',
            )
    fig_map.update_geos(
                #fitbounds = 'locations'
            )

   
    st.write(fig_map)

    st.markdown('***')
    
   
    col1,col2 = st.columns(2)
    with col1:
        st.subheader('Average mortality rate by WHO region')
        ## Average mortality rate per WHO Region
        df_avg_mortrate = df_data_country.groupby(['WHORegion']).mean().round(3)
        whoregions = df_avg_mortrate.index

        fig_mortality = px.bar(df_avg_mortrate, y='mortalityrate', x=whoregions, text='mortalityrate',text_auto='.2s')
        fig_mortality.update_traces(texttemplate='%{text:.2s}', textposition='inside', marker_color='indianred', width=0.4)
        fig_mortality.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=600, yaxis_title = 'Mortality in percent', xaxis_title ='WHO region')

        st.write(fig_mortality)

    with col2:
        st.subheader('Full vaccination per 100 in WHO regions')
        whoregions = df_vacc.index
        fig_vacc = px.bar(df_vacc, y='PERSONS_FULLY_VACCINATED_PER100', x=whoregions, text='PERSONS_FULLY_VACCINATED_PER100')
        fig_vacc.update_traces(texttemplate='%{text:.2s}', textposition='inside', marker_color='purple', width=0.4)
        fig_vacc.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', width=600, xaxis_title ='WHO region', yaxis_title = 'Proportion of fully vaccinated persons')
        
        st.write(fig_vacc)
        

    st.markdown('***')

    

    table_cont = st.container()
    with table_cont:
            st.subheader('Table of KPIs by country from: ' + actualdate)
            col1, col2 = st.columns(2)
            with col1:
                show_country = st.radio(
                '',
            ('Actual country', 'All countries'))
            col2.info('Please note, that decimal numbers are separated by . (dot)!')
            if show_country == 'Actual country':
                df_KPI_table = df_KPI_table.query('index == @option_country')
            elif show_country == 'All countries':
                st.empty() 

    st.dataframe(df_KPI_table)
    

    st.markdown('***')
    # st.subheader('Experimantal forecasting of Covid-19 cases for '+  option_country)

    # # Define dataframe more forecasting scenario
    # df_forecast = country_selector.filter(['Date_reported','New_cases'], axis=1)
    # df_forecast = df_forecast.rename(columns={'Date_reported':'ds', 'New_cases':'y'})
    # df_forecast
    # m = Prophet()
    # m.fit(df_forecast)

    # #forecasting for 30 days
    # future = m.make_future_dataframe(periods=30)

    # forecast = m.predict(future)
    # forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    # fig1 = m.plot_components(forecast)
    # st.write(fig1)

if __name__ == '__main__':
    main()
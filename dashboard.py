"""" This module was created to show a dashboard on streamlit according to House Rocket project
premises.

Author: Joao Renato Freitas Mendes <joaorenatomendes@gmail.com>

Created on Nov 10th, 2021.
"""

###---IMPORTS---###
import pandas as pd   #to handle csv files and DataFrame structures
#import numpy as np
#import folium         #to handle the map with price density
import plotly.express as px
import matplotlib.pyplot as plt   #to plot graphic results of the metrics
import seaborn as sns     #to plot graphic results of the metrics given
#from matplotlib import gridspec  #helps to create multiple plots
import streamlit as st  #to create the dashboard page
import Functions  #functions created to modularize the code
pd.set_option('display.float_format', lambda x: '%.2f' % x)  #limits the quantity of float numbers (decimal)

st.set_page_config(layout = 'wide')
@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path) #loads the archive
    return data


### What are the estates that House Rocket should buy and for how much? ###
### COLOCAR MAPA DE DENSIDADE EM CIMA OU EMBAIXO
def buy_estates(data):

    st.title('House Rocket Exploratory Data Analysis')
    st.header('1. How many estates should House Rocket buy?')
    c1, c2 = st.beta_columns(2)

    #st.header('1. What are the estates that House Rocket should buy and for how much?')
    c1.header('Dataset overview')
    df = data[['id', 'date', 'price', 'condition', 'zipcode', 'waterfront']].copy()
    df_group_median = df[['price', 'zipcode']].groupby('zipcode').median().reset_index()  # calculating the average price per region

    buy_estate_result = pd.merge(df, df_group_median, on='zipcode', how='inner')         #merges into a single dataframe with all data of interest
    buy_estate_result.rename(columns= {'price_x': 'price', 'price_y': 'median_price'}, inplace = True)
    buy_estate_result.sort_values('zipcode')    #organizes the dataframe by zipcode order

    buy_estate_result['buy_estate']=buy_estate_result.apply(Functions.buy_estate, axis = 1) #for more details, check Functions archive

    c1.write(buy_estate_result.head(15))

    c2.header('Quantity of estates to buy:')
    buy_estate_plot = buy_estate_result[['id', 'buy_estate']].groupby('buy_estate').count().reset_index()

    fig = px.histogram(
        data_frame=buy_estate_plot,
        x="buy_estate",
        y="id",
        histfunc="avg",
        title = 'Number of houses to buy',

        )
    fig.update_layout(font_family = "Courier New",
                      font_color = "blue",
                      title_font_family = "Times New Roman",
                      legend_title_font_color = "black")

    fig.update_xaxes(title_font_family = "Arial")

    c2.plotly_chart(fig, use_container_width=True)  #creates a minor dataframe with a description of how many estates HR should buy

#----SET SEASONS ON DATAFRAME----#
    st.header('2. What is/are the best season(s) to buy a estate?')
    st.subheader('Prices according to season period')


    data_pivot = buy_estate_result[buy_estate_result['buy_estate'] == 'yes'].copy()  #collecting only the dataframe estates that House Rocket will probably buy. that will help to create a final dataframe
    data_pivot.rename(columns = {'price': 'price_buy'}, inplace = True) #renaming
    data_pivot['date'] = pd.to_datetime(data_pivot['date'])

    data_pivot['season'] = (data_pivot['date'].dt.month%12 + 3)//3   #Calculating respective seasons according to date column on data frame

    seasons = {
           1: 'Winter',
           2: 'Spring',
           3: 'Summer',
           4: 'Autumn'
            }

    data_pivot['season_name'] = data_pivot['season'].map(seasons)

    season_pivot = data_pivot[['price_buy', 'season_name', 'zipcode']].groupby(['season_name', 'zipcode']).median().reset_index()
    data_seasons = pd.merge(data_pivot, season_pivot, on=['zipcode', 'season_name'], how='inner')         #merges the dataframe we used to help us gettting the info we wanted
    data_seasons.rename(columns={"price_buy_x": "price_buy", "price_buy_y": "price_median"}, inplace=True)
    data_seasons = data_seasons[['id', 'zipcode', 'season_name', 'price_buy', 'price_median']]

    data_seasons['sale_price'] = data_seasons.apply(Functions.price_sale, axis=1)
    data_seasons['percentual'] = data_seasons.apply(Functions.percentual_sale, axis=1)

    st.write(data_seasons)

    return None

if __name__ == '__main__':
    # ETL
    # ---- Data Extraction
    path = 'kc_house_data.csv'
    data = get_data(path)

    # ---- Transformation
    buy_estates(data)
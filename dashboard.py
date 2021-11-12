"""" This module was created to show a dashboard on streamlit according to House Rocket project
premises.

Author: Joao Renato Freitas Mendes <joaorenatomendes@gmail.com>

Created on Nov 10th, 2021.
"""

###---IMPORTS---###
import pandas as pd   #to handle csv files and DataFrame structures
#import numpy as np
#import folium
#import plotly.express as px
#import matplotlib.pyplot as plt   #to plot graphic results of the metrics
#import seaborn as sns     #to plot graphic results of the metrics given
#from matplotlib import gridspec  #helps to create multiple plots
import streamlit as st
import Functions
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
    df_group_median = df[['price', 'zipcode']].groupby('zipcode').median().reset_index()  #MEDIA DOS PREÇOS POR REGIÃO

    buy_estate_result = pd.merge(df, df_group_median, on='zipcode', how='inner')         #MERGE EM DF E DF_GROUP
    buy_estate_result.rename(columns= {'price_x': 'price', 'price_y': 'median_price'}, inplace = True)
    buy_estate_result.sort_values('zipcode')

    buy_estate_result['buy_estate']=buy_estate_result.apply(Functions.buy_estate, axis = 1)

    c1.write(buy_estate_result.head())

    c2.header('Quantity of estates to buy:')
    c2.write(buy_estate_result[['id', 'buy_estate']].groupby('buy_estate').count().reset_index())

#----SET SEASONS ON DATAFRAME----#
    st.header('2. What is/are the best season(s) to buy a estate?')
    st.subheader('Prices according to season period')


    data_pivot = buy_estate_result[buy_estate_result['buy_estate'] == 'yes'].copy()
    data_pivot.rename(columns = {'price': 'price_buy'}, inplace = True)
    data_pivot['date'] = pd.to_datetime(data_pivot['date'])

    data_pivot['season'] = (data_pivot['date'].dt.month%12 + 3)//3   #CALCULANDO ESTAÇÃO DE ACORDO COM A DATA DOS IMOVEIS NO DF

    seasons = {
           1: 'Winter',
           2: 'Spring',
           3: 'Summer',
           4: 'Autumn'
            }

    data_pivot['season_name'] = data_pivot['season'].map(seasons)

    season_pivot = data_pivot[['price_buy', 'season_name', 'zipcode']].groupby(['season_name', 'zipcode']).median().reset_index()
    data_seasons = pd.merge(data_pivot, season_pivot, on=['zipcode', 'season_name'], how='inner')
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
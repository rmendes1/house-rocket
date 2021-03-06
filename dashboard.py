"""" This module was created to show a dashboard on streamlit according to House Rocket project
premises.

Author: Joao Renato Freitas Mendes <joaorenatomendes@gmail.com>

Created on Nov 10th, 2021.
"""

###---IMPORTS---###
import pandas as pd   #to handle csv files and DataFrame structures
import folium         #to handle the price density map
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px #to plot graphic results of the metrics
import streamlit as st  #to create the dashboard page
import Functions  #functions created to modularize the code
pd.set_option('display.float_format', lambda x: '%.2f' % x)  #limits the quantity of float numbers (decimal)

st.set_page_config(layout = 'wide')
@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path) #loads the archive
    return data

def data_overview_map(data):
    st.title('House Rocket Exploratory Data Analysis')
    c1, c2 = st.beta_columns(2)
    st.sidebar.title("Modify the table to your preferences:")
    st.sidebar.markdown('Select the columns and/or area of interest:')
    f_attributes = st.sidebar.multiselect('Enter columns', data.columns)
    f_zipcode = st.sidebar.multiselect('Enter zipcode', sorted(set(data['zipcode'].unique())))
    c1.header('Data Overview')
    # attributes + zipcode = Select columns and rows
    # atributes = select colunmns
    # zipcode = select lines
    # 0 + 0 = returns original dataset

    if (f_zipcode != []) & (f_attributes != []):
        data = data.loc[data['zipcode'].isin(f_zipcode), f_attributes]

    elif (f_zipcode != []) & (f_attributes == []):
        data = data.loc[data['zipcode'].isin(f_zipcode), :]

    elif (f_zipcode == []) & (f_attributes != []):
        data = data.loc[:, f_attributes]

    else:
        data = data.copy()

    c1.dataframe(data, height = 520)

    c2.header('Portfolio Density')

    df = data.sample(15000)

    # -----------
    # MAP CONSTRUCTION - folium
    # --------------

    density_map = folium.Map(location=[data['lat'].mean(), data['long'].mean()],
                             default_zoom_start=15)

    # st.write(density_map)
    marker_cluster = MarkerCluster().add_to(density_map)

    for name, row in df.iterrows():
        folium.Marker(([row['lat'], row['long']]),
                      popup='Price {0}, Sold on: {1}, with sqft: {2} m2'.format(row['price'],
                                                                                row['date'],
                                                                                row['sqft_living']), max_width = 700).add_to(
            marker_cluster)

    with c2:
        folium_static(density_map)

    return None



### What are the estates that House Rocket should buy and for how much? ###
def buy_estates(data):

    st.header('1. How many estates should House Rocket buy?')
    c1, c2 = st.beta_columns(2)

    #st.header('1. What are the estates that House Rocket should buy and for how much?')
    #c1.header('Dataset overview')
    data['zipcode'] = data['zipcode'].astype(str) # Transforms "ZIPCODE" feature data type from INT - STRING
    df = data[['id', 'date', 'price', 'condition', 'zipcode', 'waterfront']].copy()
    df_group_median = df[['price', 'zipcode']].groupby('zipcode').median().reset_index()  # calculating the average price per region

    buy_estate_result = pd.merge(df, df_group_median, on='zipcode', how='inner')         #merges into a single dataframe with all data of interest
    buy_estate_result.rename(columns= {'price_x': 'price', 'price_y': 'median_price'}, inplace = True)
    buy_estate_result.sort_values('zipcode')    #organizes the dataframe by zipcode order

    buy_estate_result['buy_estate']=buy_estate_result.apply(Functions.buy_estate, axis = 1) #for more details, check Functions archive
    buy_estate_result.sort_values('condition', inplace = True)

    st.header('Quantity of estates to buy')
    fig = px.histogram(
        data_frame=buy_estate_result,
        x="buy_estate",
        y="id",
        color = "condition",
        histfunc="count",
        barmode = "group",
        labels={
             "buy_estate": "Estates to be bought", "condition": "Condition"
        },
        color_discrete_sequence = px.colors.sequential.Viridis
        )

    st.plotly_chart(fig, use_container_width=True)  #creates a minor plot with a description of how many estates HR should buy

#----SET SEASONS ON DATAFRAME----#
    st.header('2. What is/are the best season(s) to buy a estate?')
    c1, c2 = st.beta_columns(2)
    c1.subheader('Estates per region x Sales Percentual')
    c2.subheader('Mean price sell per region')



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
    data_seasons = pd.merge(data_pivot, season_pivot, on=['zipcode', 'season_name'], how='inner')        #merges the dataframe we used to help us gettting the info we wanted
    data_seasons.rename(columns={"price_buy_x": "price_buy", "price_buy_y": "season_median"}, inplace=True)
    data_seasons = data_seasons[['id', 'zipcode', 'season_name', 'price_buy', 'season_median']].sort_values('zipcode', ascending=True)

    data_seasons['sale_price'] = data_seasons.apply(Functions.price_sale, axis=1)
    data_seasons['percentual'] = data_seasons.apply(Functions.percentual_sale, axis=1)

    #st.dataframe(data_seasons)
    fig2 = px.histogram(data_seasons,
                       x="zipcode",
                       y="id",
                       color="percentual",
                       barmode="stack",
                       histfunc = "count",
                       labels = {
                         "percentual": "Percentual Profit", "zipcode": "Zipcode"
                       },
                       color_discrete_sequence = px.colors.cyclical.Edge
                       )

    c1.plotly_chart(fig2, use_container_width=True)

    mean_price_sell_by_zipcode = data_seasons[['zipcode', 'sale_price']].groupby('zipcode').mean().reset_index()
    fig3 = px.line(mean_price_sell_by_zipcode,
                   x = "zipcode",
                   y = "sale_price",
                   labels={
                    "zipcode": "Zipcode"
                   },
                   color_discrete_sequence=px.colors.cyclical.Edge
                   )
    c2.plotly_chart(fig3, use_container_width=True)

    return None

def business_hypo_1(data):
    st.title('Business hypothesis')
    st.header('A. More than 10% of Estates with waterfront are cheaper than average')
    data['zipcode'] = data['zipcode'].astype(str)
    c1, c2 = st.beta_columns(2)
    c1.subheader('Estates with waterfront vs Price Avg')
    c2.subheader('Estates per region vs Price Avg')
    data_new = Functions.create_price_mean_col(data)  #Merges column price_mean on the current dataset

    data_new['percentual'] = data_new.apply(Functions.percentual_growth, axis=1)
    data_new['bigger_smaller'] = data_new.apply(Functions.bigger_smaller_than_avg, axis=1)
    data_new.sort_values('zipcode', inplace=True) #organizing dataframe by region order so that the plot is organized

    wf = data_new[data_new['waterfront'] == 1]
    wf = wf[['waterfront', 'bigger_smaller', 'zipcode']]

    ##### SECOND PLOT: Estates with waterfront vs Price Avg
    fig1 = px.pie(wf, values='waterfront', names='bigger_smaller', color_discrete_sequence = px.colors.cyclical.Edge)
    fig1.update_traces(textposition='inside', textfont_size=15)
    #fig1.update_layout(uniformtext_minsize=14, uniformtext_mode='hide')
    c1.plotly_chart(fig1, use_container_width=True)

    ##### THIRD PLOT: Estates per region vs Price Avg
    fig2 = px.histogram(wf,
                       x="zipcode",
                       y="waterfront",
                       color="bigger_smaller",
                       histfunc="count",
                       barmode="stack",
                        labels={
                            "bigger_smaller": "Bigger/Smaller than Avg", "zipcode": "Zipcode"
                        },
                        color_discrete_sequence = px.colors.cyclical.Edge
                       )
    c2.plotly_chart(fig2, use_container_width=True)

    return None

def business_hypo_2(data):
    st.header('B. More than 60% of Estates with year built before 1955 are cheaper than average')
    data['zipcode'] = data['zipcode'].astype(str)
    data_new = Functions.create_price_mean_col(data)  # Merges column price_mean on the current dataset

    data_new['percentual'] = data_new.apply(Functions.percentual_growth, axis=1)
    data_new['bigger_smaller'] = data_new.apply(Functions.bigger_smaller_than_avg, axis=1)
    data_new.sort_values('zipcode', inplace=True)  # organizing dataframe by region order so that the plot is organized

    df_yrbuilt = data_new[data_new['yr_built'] < 1955].copy()
    df_yrbuilt = df_yrbuilt[['id', 'yr_built', 'zipcode', 'condition', 'bigger_smaller']].copy()
    df_yrbuilt.sort_values('zipcode', inplace=True)

    total_df_yrbuilt = df_yrbuilt[['id', 'bigger_smaller', 'zipcode']].groupby(['zipcode', 'bigger_smaller']).count().reset_index()
    total_df_condition = df_yrbuilt[['id', 'condition', 'bigger_smaller']].groupby(['bigger_smaller', 'condition']).count().reset_index()
    total_df_condition = df_yrbuilt[['id', 'bigger_smaller', 'condition']].groupby(
        ['condition', 'bigger_smaller']).count()

    total_df_condition['percentual'] = total_df_condition.groupby(level=[0, 0]).apply(lambda g: (g / (g.sum()) * 100))
    total_df_condition.reset_index(inplace=True)
    total_df_condition['percentual'] = total_df_condition['percentual'].transform(lambda x: '%.2f' % x).transform(
                                                                                                        lambda x: f'{x}%')
    st.subheader('Condition of Estates with Year Built < 1955')

    fig1 = px.bar(total_df_condition,
                  x = 'condition',
                  y = 'id',
                  color = 'bigger_smaller',
                  text = 'percentual',
                  labels={
                      "bigger_smaller": "Bigger/Smaller than Avg"
                  },
                  color_discrete_sequence=px.colors.cyclical.Edge
                  )

    st.plotly_chart(fig1, use_container_width=True)

    c1, c2 = st.beta_columns(2)

    c1.subheader('Price Avg of Estates with Year Built < 1955')
    c2.subheader('Estates per region vs Price Avg')



    fig2 = px.pie(total_df_yrbuilt, values= 'id', names='bigger_smaller', color_discrete_sequence = px.colors.cyclical.Edge)
    fig2.update_traces(textposition='inside', textfont_size=15)
    c1.plotly_chart(fig2, use_container_width=True)

    fig3 = px.histogram(df_yrbuilt,
                        y='id',
                        x='zipcode',
                        color='bigger_smaller',
                        histfunc='count',
                        barmode= 'stack',
                        color_discrete_sequence=px.colors.cyclical.Edge,
                        labels={
                            "bigger_smaller": "Bigger/Smaller than Avg", "zipcode": "Zipcode"
                        }
                        )

    c2.plotly_chart(fig3, use_container_width=True)

    return None


def business_hypo_3(data):
    st.header('C. Estates with basement have total area (sqrt_lot) 40% bigger than estates without basement.')

    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
    data['zipcode'] = data['zipcode'].astype(str)
    data.sort_values('zipcode', inplace=True)

    no_basement = data.loc[data['sqft_basement'] == 0] #dataframe with estates without basement
    no_basement = no_basement[['sqft_lot', 'zipcode']].groupby('zipcode').mean().reset_index()

    with_basement = data.loc[data['sqft_basement'] > 0] #dataframe with estates with basement
    with_basement = with_basement[['sqft_lot', 'zipcode']].groupby('zipcode').mean().reset_index()

    data = pd.merge(data, no_basement, on='zipcode', how='inner') #merging dataframe with estates without basement and original dataframe
    data.rename(columns={"sqft_lot_x": "sqft_lot", "sqft_lot_y": "no_basement_sqft_lot"}, inplace=True)

    basement = pd.merge(data, with_basement, on='zipcode', how='inner') #merges original dataframe with dataframe containing estates with basement
    basement.rename(columns={"sqft_lot_x": "sqft_lot", "sqft_lot_y": "with_basement_sqft_lot"}, inplace=True)

    basement['no_basement_size_avg'] = basement.apply(Functions.basement_size_col, percentage=40, axis=1)
    basement_plot = basement[['id', 'no_basement_size_avg']].groupby('no_basement_size_avg').count().reset_index() #preparing data for plot

    c1, c2 = st.beta_columns(2)


    # FIRST PLOT: PIE CHART
    c1.subheader('Basement area relation')
    fig1 = px.pie(basement_plot, values='id', names='no_basement_size_avg',
                  color_discrete_sequence=px.colors.cyclical.Edge)
    fig1.update_traces(textposition='inside', textfont_size=15)
    c1.plotly_chart(fig1, use_container_width=True)


    #SECOND PLOT: BAR CHART
    c2.subheader('Basement size area per region')
    fig2 = px.histogram(basement,
                        x='zipcode',
                        y='id',
                        color='no_basement_size_avg',
                        labels={
                            "no_basement_size_avg": "Without basement estates size avg", "zipcode": "Zipcode"
                        },
                        histfunc='count',
                        barmode='stack',
                        color_discrete_sequence=px.colors.cyclical.Edge)
    c2.plotly_chart(fig2, use_container_width=True)

    return None

def business_hypo_4(data):
    st.header('D. The estates growth price YoY (Year over Year) in 2015 is 10% in most regions')
    st.subheader('YoY variation from 2014 to 2015 in all regions')
    data['zipcode'] = data['zipcode'].astype(str)
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
    data.sort_values('date', inplace=True)
    year_summary = data[['id', 'zipcode', 'date', 'price']].copy()
    year_summary['year'] = pd.to_datetime(year_summary['date']).dt.strftime('%Y')
    year_summary = year_summary[['zipcode', 'price', 'year']].groupby(['zipcode', 'year']).mean().reset_index()


    year_summary['price'] = year_summary['price'].astype('float')

    # LOOP TO CALCULATE THE PRICE DIFFERENCE BETWEEN YEARS
    for i in range(len(year_summary)):
        if year_summary.loc[i, 'year'] == '2015':
            year_summary.loc[i, 'difference'] = year_summary.loc[i, 'price'] - year_summary.loc[i - 1, 'price']

    else:
        year_summary.loc[i, 'difference'] = 'NaN'  #because there are no years before 2014

    # it is necessary to perform this data type transformation, otherwise the division below will not occur
    year_summary['difference'] = year_summary['difference'].astype(float)

    year_summary_1 = year_summary[year_summary['year'] == '2015'].copy()
    year_summary_1.drop('year', axis=1, inplace=True)
    year_summary_1['YoY_percentage_diff (%)'] = (year_summary_1['difference']) / (year_summary_1['price']) * 100

    # PLOT SETTINGS
    fig1 = px.line(year_summary_1,
                   x='zipcode',
                   y='YoY_percentage_diff (%)',
                   labels={
                       "YoY_percentage_diff (%)": "YoY difference (%)", "zipcode": "Zipcode"
                   },
                   color_discrete_sequence=px.colors.cyclical.Edge
                   )

    st.plotly_chart(fig1, use_container_width=True)

    return None

def business_hypo_data_5(data):
    st.header('E. The estates price growth MoM (Month over MonthO between 2014-2015 is 20%')
    st.subheader('Estates MoM variation from 2014 to 2015')
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')
    data['zipcode'] = data['zipcode'].astype(str)
    data.sort_values('date', inplace=True)

    monthly = data[['id', 'date', 'price']].copy()

    monthly['year_month'] = pd.to_datetime(monthly['date']).dt.strftime('%Y-%m')
    monthly = monthly[['price', 'year_month']].groupby('year_month').mean().reset_index()
    monthly['difference'] = monthly['price'].diff(1)
    monthly['MoM_diff (%)'] = (monthly['difference'] / monthly['price']) * 100

    fig1 = px.line(monthly,
                  x='year_month',
                  y='MoM_diff (%)',
                  labels={
                       "MoM_diff (%)": "MoM difference (%)", "year_month": "Year month"
                   },
                  color_discrete_sequence=px.colors.cyclical.Edge
                  )

    st.plotly_chart(fig1, use_container_width=True)

if __name__ == '__main__':
    # ETL
    # ---- Data Extraction
    path = 'kc_house_data.csv'
    data = get_data(path)

    # ---- Transformation
    data_overview_map(data)
    buy_estates(data)
    business_hypo_1(data)
    business_hypo_2(data)
    business_hypo_3(data)
    business_hypo_4(data)
    business_hypo_data_5(data)
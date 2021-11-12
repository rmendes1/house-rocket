import pandas as pd

def buy_estate(row):
    if (row.price < row.median_price) & (row.condition >= 3):
        buy_estate = 'yes'
    else:
        buy_estate = 'no'

    return buy_estate

def summer_price_sell(row):
    if row.price_buy > row.summer_median:
        price_sell = row.price_buy +(row.price_buy *0.1)
    else:
        price_sell = row.price_buy +(row.price_buy *0.3)

    return price_sell

def autumn_price_sell(row):
    if row.price_buy > row.autumn_median:
        price_sell = row.price_buy + (row.price_buy *0.1)
    else:
        price_sell = row.price_buy + (row.price_buy *0.3)

    return price_sell

def winter_price_sell(row):
    if row.price_buy > row.winter_median:
        price_sell = row.price_buy +(row.price_buy *0.1)
    else:
        price_sell = row.price_buy +(row.price_buy *0.3)

    return price_sell

def spring_price_sell(row):
    if row.price_buy > row.spring_median:
        price_sell = row.price_buy + (row.price_buy *0.1)
    else:
        price_sell = row.price_buy + (row.price_buy *0.3)

    return price_sell


##### HIPOTESES DE NEGOCIO ####

def mean_feature(feature):  # Calculates the mean of a given feature
    return feature.mean()


def percentual_growth(row):  # Calculates the percentual difference in relation to the mean value
    if row.price > row.price_mean:
        percentual = ((row.price - row.price_mean) / row.price_mean) * 100

    else:
        percentual = ((row.price_mean - row.price) / row.price_mean) * 100

    return percentual


def percentage_index(plot, feature):  # Sets an indication of percentage in barplots
    total = feature.sum()
    for p in plot.patches:
        percentage = str(((p.get_height() / total) * 100).round(1)) + '%'
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        plot.annotate(f'{percentage}', (x + width / 2, y + height),
                      ha='center', fontsize=25)
    return None

def quantity_index(plot, feature):  # Sets an indication of quantity in barplots
    total = feature.sum()
    for p in plot.patches:
        width = p.get_width()
        height = p.get_height()
        x, y = p.get_xy()
        plot.annotate(f'{height}', (x + width / 2, y + height),
                      ha='center', fontsize=25)
    return None

def bigger_smaller_than_avg(
        row):  # Calculates if a given estate has a bigger or smaller price in relation to the mean value
    if row.price > row.price_mean:
        bigger_smaller = 'bigger'
    else:
        bigger_smaller = 'smaller'

    return bigger_smaller


def create_price_mean_col(data):  # Merges column price_mean on the current dataset
    price_mean = data[['zipcode', 'price']].groupby('zipcode').mean().reset_index()
    df = pd.merge(data, price_mean, on='zipcode', how='inner')
    df.rename(columns={"price_x": "price", "price_y": "price_mean"}, inplace=True)

    return df


def waterfront_expensive_col(row,
                             percentage):  # Creates column to indicate if a given estate has a more expensive price (%) than the mean value
    if (row.price >= row.price_mean * ((percentage / 100) + 1)):
        expensive_index = f'more expensive than {percentage}% of the avg'
    else:
        expensive_index = f'less expensive than {percentage}% of the avg'

    return expensive_index


def yrbuilt_expensive_col(row,
                          percentage):  # Creates column to indicate if a given estate with year of construction < 1955 has a cheaper/expensive price than the mean value
    if (row.yr_built < 1955) & (row.price < row.price_mean * (percentage / 100)):
        cheaper_index = f'cheaper than {percentage}%  of avg'
    else:
        cheaper_index = f'{percentage}% more expensive than avg'
    return cheaper_index


def basement_size_col(row, percentage):
    if row.no_basement_sqft_lot > (row.with_basement_sqft_lot * ((percentage / 100) + 1)):
        no_basement_sqft = f'bigger than {percentage} of avg%'
    else:
        no_basement_sqft = f'smaller than {percentage} of avg%'
    return no_basement_sqft
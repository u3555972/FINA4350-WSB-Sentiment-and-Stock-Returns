#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 17:08:05 2022

@author: uttsant
"""

import yfinance as yf
import pandas as pd
import scipy.stats as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import numpy as np
from numpy.polynomial.polynomial import polyfit
import os

save_path = r'/Users/uttsant/Desktop'
market_shocks = ['2018-09-20', '2020-02-20','2021-01-11', '2018-09-05', '2021-03-10'] # CRYPTO, COVID, GME + 2 random dates

#create dataframe for csv with sentiment values
sentiment_csv_path = r'/Users/uttsant/Desktop/Updated_Data.csv'
df = pd.read_csv(sentiment_csv_path)

df['date'] = df['date'].apply(lambda x: x.split()[0]) #convert date to yyyy-mm-dd format

#create a list of lists of relevant stock tickers for the 3 market shocks and random dates
tickers_on_market_shocks = []
for date in market_shocks:
    tickers_on_market_shocks.append(list(df[df['date'] == date].groupby('ticker').mean().index))


list_of_final_cs = []
list_of_returns = []
list_of_corr_p = []

def based_on_timeframe(number,period): #add 's' e.g. days, weeks, months, years
    #returns part
    zip_ = zip(market_shocks, tickers_on_market_shocks)
    for date, ticker_group in zip_:
        return_list = []
        ticker_list = []
        start_date = datetime.strptime(date, '%Y-%m-%d') + relativedelta(days = 1)
        if period == 'days':
            end_date = start_date + relativedelta(days = number)
        elif period == 'weeks':
            end_date = start_date + relativedelta(weeks = number)
        elif period == 'months':
            end_date = start_date + relativedelta(months = number)
        elif period == 'years':
            end_date = start_date + relativedelta(years = number)
        for ticker in ticker_group:
            try:
                temp_df = yf.download(ticker, start = start_date, end = end_date, interval='1d')
                return_list.append((temp_df['Close'][-1] - temp_df['Close'][0])/ temp_df['Close'][0])
                ticker_list.append(ticker + ' ' + date)
                # full_return_df = full_return_df.append(temp_df)
                
            except:
                pass
        list_of_returns.append(return_list)
    
        #sentiment value part
        if period == 'days':
            range_ = datetime.strptime(date, '%Y-%m-%d') + relativedelta(days = number)
        elif period == 'weeks':
            range_ = datetime.strptime(date, '%Y-%m-%d') + relativedelta(weeks = number)
        elif period == 'months':
            range_ = datetime.strptime(date, '%Y-%m-%d') + relativedelta(months = number)
        elif period == 'years':
            range_ = datetime.strptime(date, '%Y-%m-%d') + relativedelta(years = number)
            
        final_range = datetime.strftime(range_, '%Y-%m-%d')
        # get average of compound signal based on market shock and timeframe
        
        # get average for relevant shock and ones that have return data available
        
        cs_average_series = df[(df['date'] >= date) & (df['date'] <= final_range)].groupby('ticker').mean()['Updated Score']
        # print(cs_average_series)
        
        relevant_tickers = []
        for i in ticker_list:
            if i.split()[1] == date:
                relevant_tickers.append(i.split()[0])
                
        final_cs = cs_average_series.loc[relevant_tickers]
        list_of_final_cs.append(list(final_cs))


        list_of_corr_p.append(st.pearsonr(list(final_cs),return_list))
        print(st.pearsonr(list(final_cs),return_list))
    
    #scatterplot for each market shock
    for i in range(len(list_of_final_cs)):
        plt.figure()
        # plt.scatter(x = list_of_final_cs[i],y = list_of_returns[i])
        
        x = np.array(list_of_final_cs[i])
        y = np.array(list_of_returns[i])
        b, m = polyfit(x, y, 1)
        plt.plot(x, y, '.')
        plt.plot(x, b + m * x, '-')
        
        plt.ylabel('Stock Returns')
        plt.xlabel('WSB Sentiment Values')
        plt.savefig(save_path + os.sep + str(i) + '.png')

    plt.show()
    
    #print correlation values and p-values for all the market shocks for this timeframe
    print(list_of_corr_p)
    


#updated
# all_ = [[(-0.17258532596164328, 0.4310074112183944),
#   (0.49982001860157044, 0.05780329386762233),
#   (-0.03085443227169377, 0.8646552290584371),
#   (0.03162920230883916, 0.8806962388398492),
#   (0.04976502860608715, 0.89140820013998)],
#   [(-0.007327915425555498, 0.9735279187099298),
#   (0.4643824237021545, 0.08117920547080883),
#   (-0.03258044445695158, 0.8571593381255875),
#   (0.14139836127940084, 0.5001865185580648),
#   (-0.4124199072101614, 0.2362554611266908)],
#   [(-0.16989130216464382, 0.43834398947175374),
#   (0.2061422843639627, 0.46106395608620565),
#   (-0.08265448519634755, 0.6474628423445268),
#   (-0.025266870823935215, 0.9045740257090061),
#   (0.2654310192082488, 0.4585769172890083)],
#   [(-0.04954985002704003, 0.8181492698196237),
#   (0.2153761055979721, 0.44076800445156294),
#   (-0.06569499969467663, 0.7120268633609121),
#   (-0.05921217470152252, 0.778595169063763),
#   (-0.1820261168850586, 0.614750827334311)],
#   [(-0.10674662261126869, 0.6195734002046364),
#   (0.26645042084553955, 0.3370854508753875),
#   (-0.0818922553791022, 0.64001849491716),
#   (-0.18187875072244783, 0.38423127770411936),
#   (-0.2042397284359013, 0.5469152814088715)],
#   [(-0.16004544338300722, 0.4447452126676084),
#   (-0.006611652374476196, 0.9813429357841086),
#   (-0.00037044593061519304, 0.9982891530942188),
#   (-0.17087494863156866, 0.41411927222885203),
#   (0.021554120605213348, 0.94698949976478)]]



# #crypto shock
# crypto_corr = [row[0][0] for row in all_]
# crypto_p = [row[0][1] for row in all_]
# x = ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year']
# sns.lineplot(x, crypto_corr, label = 'correlation value').set(title='Overall Correlation Trend for the Crypto Shock')
# sns.lineplot(x, crypto_p, label = 'p-value')

# # #covid shock
# covid_corr = [row[1][0] for row in all_]
# covid_p = [row[1][1] for row in all_]
# x = ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year']
# sns.lineplot(x, covid_corr, label = 'correlation value').set(title='Overall Correlation Trend for the Covid Shock')
# sns.lineplot(x, covid_p, label = 'p-value')

# # #gme shock
# gme_corr = [row[2][0] for row in all_]
# gme_p = [row[2][1] for row in all_]
# x = ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year']
# sns.lineplot(x, gme_corr, label = 'correlation value').set(title='Overall Correlation Trend for the GME Shock')
# sns.lineplot(x, gme_p, label = 'p-value')

# # #random date 1
# rand1_corr = [row[3][0] for row in all_]
# rand1_p = [row[3][1] for row in all_]
# x = ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year']
# sns.lineplot(x, rand1_corr, label = 'correlation value').set(title='Overall Correlation Trend for Control No.1')
# sns.lineplot(x, rand1_p, label = 'p-value')

# # #random date 2
# rand2_corr = [row[4][0] for row in all_]
# rand2_p = [row[4][1] for row in all_]
# x = ['1 day', '1 week', '1 month', '3 months', '6 months', '1 year']
# sns.lineplot(x, rand2_corr, label = 'correlation value').set(title='Overall Correlation Trend for Control No.2')
# sns.lineplot(x, rand2_p, label = 'p-value', color = 'black')


















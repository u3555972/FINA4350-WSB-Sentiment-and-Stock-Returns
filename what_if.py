#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 18:27:09 2022

@author: potatobook
"""
import yfinance as yf
import pandas as pd
pd.options.mode.chained_assignment = None
import matplotlib.pyplot as plt
import textcleaner as tc
import numpy as np
import math
import os
from wordcloud import WordCloud

# ask some questions:
ticker_required = input('ticker: ')
if ticker_required == '':
    ticker_required = 'TSLA'
    print('No input, TSLA as an example here')

start_date = input('start(YYYY-MM-DD):')
if start_date == '':
    start_date = '2020-01-01'
    print('No input, default 2020-01-01')

end_date = input('end(YYYY-MM-DD):')
if end_date == '':
    end_date = '2020-12-31'
    print('No input, default 2020-12-31')

# download stock price history from yahoo finance
oneday_int_df = yf.download(ticker_required,
                            start=start_date, end=end_date, interval='1d')
oneday_int_df = oneday_int_df.rename(columns=str.lower).astype(float)
oneday_int_df.reset_index(inplace=True)
oneday_int_df['Date'] = oneday_int_df['Date'].astype(str) #make date column into string format, for merge later

# Info from sentiment analysis file
export_path = os.path.abspath('/Users/potatobook/documents/FINA4350/project/backtest')
rawdata = pd.read_csv(export_path + os.sep + 'Updated_Data.csv')

core_data_df = rawdata[['date','ticker','Updated Score']]
core_data_df.dropna(inplace=True) #drop nan values
core_data_df = core_data_df.copy()
core_data_df['Date'] = core_data_df['date'].astype(str).str[:10] #keep date only, no need time
core_data_df = core_data_df.copy()
core_data_df = core_data_df[core_data_df.columns[1:4]]

# aggregate the scores of same ticker on same day into average score
aggregation_functions = {'Updated Score': 'mean'}
integrated_sentiment_df = core_data_df.groupby(['Date','ticker']).aggregate(aggregation_functions).reset_index()
integrated_sentiment_df = integrated_sentiment_df.copy()
# select the data with specific ticker collected only
sentiment_merge_df = integrated_sentiment_df[integrated_sentiment_df['ticker']== ticker_required]
# drop the ticker column as long as all data comes within same column
sentiment_merge_df.drop('ticker', inplace=True, axis=1)
sentiment_merge_df = sentiment_merge_df.copy()

# Merge 2 dataframes
process_df = oneday_int_df.merge(sentiment_merge_df, how='left', on='Date')
# fillna to 0
process_df = process_df.copy()
process_df['Updated Score'] = process_df['Updated Score'].fillna(0)
# change Date column to datetime format
process_df = process_df.copy()
process_df['Date'] = process_df['Date'].astype('datetime64[ns]')

# Export paths
folder = str(ticker_required) + ' ' + str(start_date) + ' to ' + str(end_date)
# create new folders
mypath = os.path.join(export_path, folder)
if not os.path.exists(mypath):
    os.makedirs(mypath)


# describe base return (just hold it)
stronghold = (float(process_df.tail(1)['close']) -
              float(process_df.head(1)['close'])) / float(
    oneday_int_df.head(1)['close']) * 100

stronghold_exp = str(
    'If we just buy and hold ' + str(ticker_required) +
    ', return from ' + str(start_date) + ' to ' + str(
        end_date) + ' is: ' + str(stronghold) + '%')

# define new function to identify the trading points

WSB_result = []  # data collection


def buy_sell_WSB(signal):
    buy = []  # list will be merged into df later
    Sell = []  # list will be merged into df later
    flag = -1  # avoid repeat action of continous buy or sell

    for i in range(0, len(signal)):

        if (  # trading policies
                process_df['Updated Score'][i] < 0 
        ):
            buy.append(np.nan)  # sell, not buy
            if flag != 0:  # previous action not sell
                Sell.append(process_df['close'][i])  # mark item
                flag = 0  # mark action as buy
                # collect data for analysis later (Reverse Trading)
                WSB_result.append({
                    'date': process_df['Date'][i],
                    'action': 'buy',
                    'price': process_df['close'][i]
                })
            else:  # previous action is sell
                Sell.append(np.nan)  # pass

        elif (  # trading policies
                    process_df['Updated Score'][i] > 0 
            ):
                Sell.append(np.nan)  # buy, not sell
                if flag != 1:  # previous action not buy
                    buy.append(process_df['close'][i])  # mark item
                    flag = 1  # mark action as buy
                    # collect data for analysis later (Reverse trading)
                    WSB_result.append({
                        'date': process_df['Date'][i],
                        'action': 'sell',
                        'price': process_df['close'][i]
                    })
                else:  # previous action is buy
                    buy.append(np.nan)  # pass
        else:  # not satisfied the trading policies
            buy.append(np.nan)  # both do nothing
            Sell.append(np.nan)
    return buy, Sell


# run the function
WSB_trade = buy_sell_WSB(process_df)

# merge the sell and buy signals into the df
process_df = process_df.copy()
process_df['WSB_buy_signal'] = WSB_trade[0]
process_df = process_df.copy()
process_df['WSB_sell_signal'] = WSB_trade[1]
process_df = process_df.copy()


print('\n')
print('Trading Timespots: ')

# plot the figure displaying the trading timespot
plt.figure(figsize=(8, 4.5))
plt.scatter(process_df['Date'], process_df['WSB_sell_signal'],
            label='sell', marker='v', alpha=1,
            color='red')
plt.scatter(process_df['Date'], process_df['WSB_buy_signal'],
            label='buy', marker='^', alpha=1,
            color='green')
plt.plot(process_df['Date'],process_df['close'], label='Close Price', alpha=0.35)
plt.title('WSB Trading timespots' + " for " + ticker_required )
plt.legend(loc='upper left')
WSB_trading_expt = str(ticker_required) + ' WSB Trading timespots ' + str(
    start_date) + ' to ' + str(end_date) + str('.png')
plt.savefig(os.path.join(mypath, WSB_trading_expt), dpi=240)
plt.gcf().set_dpi(80)
plt.show()

process_df['Date']= process_df['Date'].astype('datetime64[ns]')

stronghold_return = float(oneday_int_df.tail(1)['close']) - float(
    oneday_int_df.head(1)['close'])

# wordcloud and frequency chart

def wordcloud_generator(target_string, path=mypath):
    cloud = WordCloud(collocations=False,
                      background_color="white", #make a wordcloud
                      width=1920,
                      height=1080,
                      margin=2).generate(target_string)
    fullname = str(str(start_date) + ' to ' + str(end_date) + ' wordcloud.png')
    cloud.to_file(os.path.join(path, fullname))
    plt.figure(figsize=(8,4.5))
    plt.imshow(cloud, interpolation='bilinear')
    plt.gcf().set_dpi(80)
    plt.axis("off")
    plt.show()
    return

def string_word_count(target_string):
    doc = tc.document(target_string) #use textcleaner to progress it
    doc_dict = dict(doc.each_word_count) #textcleaner count
    word_count_df = pd.DataFrame(list(doc_dict.items()), #transform dict to dataframe
                                 columns=['ticker', 'frequency']).sort_values(by=['frequency'], ascending=False)
    return word_count_df

def freq_barchart(word_count_df, path=mypath): #make a frequency chart
    chart = word_count_df.iloc[:10].plot.bar(x='ticker',
                                             y='frequency',
                                             rot=0,
                                             figsize=(8, 4.5),
                                             title=str('Top 10 Most Mentioned Tickers during ' + str(start_date) + ' to ' + str(end_date)))
    fullname = str(str(start_date) + ' to ' + str(end_date) + ' freqchart.png')
    plt.savefig(os.path.join(path, fullname), dpi=240)
    plt.gcf().set_dpi(80)
    plt.show()
    return chart

frequency_df = core_data_df.copy()
# change Date column from string format to datetime format
frequency_df.index = frequency_df['Date'].astype('datetime64[ns]')
# filter the dataframe with specific timerange designated
frequency_df = frequency_df.loc[start_date:end_date]

# merge the dataframe column to string
ticker_str=(" ").join(frequency_df['ticker'].tolist())
print('\n')
print('WordCloud: ')

wordcloud_generator(ticker_str,mypath)
ticker_count = string_word_count(ticker_str)
print('\n')
print('Frequency Chart: ')

freq_barchart(ticker_count,mypath)

print('\n')
print('Done! Output in folder: ' + str(folder))

print('\n' + stronghold_exp + '\n')
print('return is ' + str(stronghold_return) + '\n')




# Reverse Trading Analysis
def result_summary(signals):
    pairs = zip(*[iter(signals)] * 2)  # unpack the dictionary
    # initialize
    rows = []
    profit_count = 0
    profit_pct_avg = 0

    # calculate profit % and absolute amount
    for (buy, sell) in pairs:
        profit = sell['price'] - buy['price']
        profit_pct = profit / buy['price']

        if profit > 0:
            profit_count += 1
        profit_pct_avg += profit_pct
        # create a dict for each pair of trade
        row = {
            'buy_date': buy['date'],
            'duration': (sell['date'] - buy['date']).days,
            'profit': profit,
            'profit_pct': "{0:.2%}".format(profit_pct)
        }
        # append them into a list
        rows.append(row)
    # list of dict to df
    df = pd.DataFrame(rows, columns=['buy_date', 'duration', 'profit', 'profit_pct'])

    total_transaction = math.floor(len(signals) / 2)
    stats = {  # create a statistics of summary
        'total_transaction': total_transaction,
        'profit_rate over all trades': "{0:.2%}".format(profit_count / total_transaction),
        'avg_profit_per_transaction': "{0:.2%}".format(profit_pct_avg / total_transaction),
        'Profit Summation per stock': df['profit'].sum()
    }

    # string return
    export_stat_df = pd.Series(stats)
    export_stat_df.reset_index()
    df_str = df.to_string(header=True, index=True)
    export_str = str(df_str) + '\n' + " " + '\n' + str(export_stat_df)

    return export_str

# get summary
WSB_summary = result_summary(WSB_result)

# export txt analysis
txtname ='Reverse ' + str(ticker_required) + ' ' + str(start_date) + ' to ' + str(
    end_date) + ' Results.txt'

txt_loc = os.path.join(mypath, txtname)

f = open(txt_loc, 'w')
f.write('Stock: ' + str(ticker_required) + '\n')
f.write('from ' + str(start_date) + ' to ' + str(end_date) + '\n')
f.write('\n')
f.write(stronghold_exp + '\n')
f.write('return = ' + str(stronghold_return) + '\n')
f.write('\n')
f.write("WSB Result" + '\n' + WSB_summary + '\n')
f.write('\n')
f.close()

print(WSB_summary + '\n')

'''
tickers = list(set(rawdata['ticker'].tolist()))
'''

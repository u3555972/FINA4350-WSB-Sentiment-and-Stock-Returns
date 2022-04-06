#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 26 22:35:12 2022

@author: CHAN Cheuk Hang

Cleaning and Identifying Stock
"""

# Import the ibraries needed to run code
import pandas as pd
import numpy as np
import emoji
import os
import time

def combineDF(df_lst):
    '''
    This function concatenate all the DataFrames, returns a DataFrame
    '''
    
    # Concatenate all the DataFrames and automatically reset index
    df = pd.concat(df_lst, ignore_index = True)
    
    # Returns df for cleaning
    return df

def cleanData(df):
    '''
    This function cleans the DataFrame. It removes deleted posts, special
    words, and any confusing punctuation that may be referring to another
    user
    '''
    
    # Takes rows where title is NOT deleted by user
    df = df[(df['title'] != '[deleted by user]')].reset_index(drop = True)
    
    # Takes rows where content is NOT removed or deleted
    df = df[(df['content'] != '[removed]') & (df['content'] != '[deleted]')].reset_index(drop = True)
    
    # Takes rows where comment is NOT removed or deleted
    df = df[(df['comment_content'] != '[removed]') & (df['comment_content'] != '[deleted]')].reset_index(drop = True)
    
    # Removing links
    #re.sub(r"http\S+", "", df[''])
    
    # Removing Punctuation besides '!'
    #re.sub(r'[^\w\s\!]', '', s2)
    
    # Removing links and punctuation
    # re.sub(r'[^\w\s\!\$]|http\S+', '', s2)
    
    # Use emoji module to create emoji list to keep emojis
    emoji_lst = [i for i in emoji.UNICODE_EMOJI['en']]
    
    # Create a text of emojis so that it will not be filtered out when cleaning
    emojis = '|'.join(emoji_lst)
    
    # Remove punctuations (except '!'), links, line space, usernames or subreddits from title
    df['title'] = df['title'].replace(r'[^\w\s\!\{emojis}]|http\S+|\n|u/\S+|r/\S+'.format(emojis = emojis), '', regex = True)
    
    # Remove punctuations (except '!'), links, line space, usernames or subreddits from content
    df['content'] = df['content'].replace(r'[^\w\s\!\{emojis}]|http\S+|\n|u/\S+|r/\S+'.format(emojis = emojis), '', regex = True)
    
    # Remove punctuations (except '!'), links, line space, usernames or subreddits from comment
    df['comment_content'] = df['comment_content'].replace(r'[^\w\s\!\{emojis}]|http\S+|\n|u/\S+|r/\S+'.format(emojis = emojis), '', regex = True)
    
    # Combines all content into 1 cell for future use
    df['all_content'] = df[['title', 'content', 'comment_content']].fillna('').agg(' '.join, axis = 1)
    
    # Returns the cleaned df for stock matching
    return df

def ignoreWords(text):
    '''
    This functions takes in the text and removes certain words for stock
    search afterwards, returning the whole text after editing
    '''
    
    # Words to ignore consisting of abbreviations redditors often use and other
    # common abbreviations
    ignore_words = {
        'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC',
        'A', 'I', 'U', 'ELON', 'MUSK',  'ETF', 'DFV','CATHIE', 'WOODS', 'TOS', 'ROPE', 'YOLO', 
        'CEO', 'CTO', 'CFO', 'COO', 'DD', 'IT', 'ATH', 'POS',  'IMO', 'RED', 'KMS', 'KYS', 
        'GREEN', 'TLDR', 'LMAO', 'LOL', 'CUNT', 'SUBS', 'USD', 'CPU', 'AT', 'GG', 'AH',
        'AM', 'PM', 'TICK', 'IS', 'EZ', 'RAW', 'ROFL', 'FOMO', 'FBI', 'SEC', 'GOD',
        'CIA', 'LONG', 'SHORT', 'ATM', 'OTM', 'ITM', 'TYS', 'IIRC', 'IIUC', 'PDT',
        'TOS', 'TYS', 'OPEN', 'IRS', 'ALL', 'OK', 'BTFD', 'US', 'USA', 'GDP', 'FD',
        'TL', 'OP', 'PS', 'WTF', 'FOMO', 'CALL', 'PUT', 'BE', 'PR', 'GUH', 'JPOW',
        'BULL', 'BEAR', 'BUY', 'SELL', 'HE', 'ONE', 'OF', 'SHE', 'HODL', 'FINRA',
        'WSB', 'MODS', 'MOD', 'EPS', 'IRA', 'ROTH', 'BS', 'RIP', 'OMG', 'IM', 'YOU'
        'DOW', 'ARE', 'FREE', 'MONEY'
        }
    
    #text = re.sub('|'.join("((?<=\s)|(?<=^)){}((?=\s)|(?=$))".format(i) for i in ignore_words), '', text)
    
    # Split the text into a list of words
    text_lst = text.split()
    
    # for word in list(text.split()):
    #     if len(word) > 5 or (not word.isupper() and not word.islower()):
    #         text_lst.remove(word)
    
    # Loop through the list of words in text
    for word in list(text.split()):
        
        # Conditions in order to remove words: 
        # Greater than 5 (length of stock ticker)
        # Word in ignore_words set
        # Not lower or uppercase words (e.g. Last) and not lowercase words
        if len(word) > 5 or word in ignore_words or (not word.isupper() and not word.islower()) or word.islower():
            text_lst.remove(word)
    
    # Returns a string after joining the list of words in text
    return ' '.join(text_lst)

def stockSearch(text_lst, t_df):
    '''
    This function searches for the stock ticker to match with the text list
    given. It then returns the FIRST stock identified.
    '''
    
    # Convert the stock ticker Series into a list
    tickers_lst = (t_df['Symbol'].to_list())
    
    # If there is no text, return NaN
    if len(text_lst) == 0:
        return np.nan
    
    # Else, try to find the stock ticker
    else:
        
        # For loop to loop through words in a text list
        for word in text_lst:
            
            # If the word matches the one in tickers list, returns the word
            # and breaks since only taking FIRST instance
            if word in tickers_lst:
                return word
                break

def stockMatch(df, t_df):
    '''
    This function attempts to recognize the stock mentioned in the title,
    comment, or comment post. Each word will be compared to a list of stock
    tickers. If there is no match, the row will not be included in the 
    new DataFrame.
    '''
    
    
    # Initialize new column to add data in
    # df['ticker'] = np.nan
    
    #df['title_ticker'] = df['title'].apply(lambda x: x in nasdaq_df['Symbol'].to_list())
    
                
    #df['ticker'] = df['all_content'].map(lambda x: findStock(x.split()))
    
    
    # ignore_words = {
    #     'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC',
    #     'A', 'I', 'U', 'ELON', 'MUSK',  'ETF', 'DFV','CATHIE', 'WOODS', 'TOS', 'ROPE', 'YOLO', 
    #     'CEO', 'CTO', 'CFO', 'COO', 'DD', 'IT', 'ATH', 'POS',  'IMO', 'RED', 'KMS', 'KYS', 
    #     'GREEN', 'TLDR', 'LMAO', 'LOL', 'CUNT', 'SUBS', 'USD', 'CPU', 'AT', 'GG', 'AH',
    #     'AM', 'PM', 'TICK', 'IS', 'EZ', 'RAW', 'ROFL', 'FOMO', 'FBI', 'SEC', 'GOD',
    #     'CIA', 'LONG', 'SHORT', 'ATM', 'OTM', 'ITM', 'TYS', 'IIRC', 'IIUC', 'PDT',
    #     'TOS', 'TYS', 'OPEN', 'IRS', 'ALL', 'OK', 'BTFD', 'US', 'USA', 'GDP', 'FD',
    #     'TL', 'OP', 'PS', 'WTF', 'FOMO', 'CALL', 'PUT', 'BE', 'PR', 'GUH', 'JPOW',
    #     'BULL', 'BEAR', 'BUY', 'SELL', 'HE', 'ONE', 'OF', 'SHE', 'HODL', 'FINRA',
    #     'WSB', 'MODS', 'MOD', 'EPS', 'IRA', 'ROTH', 'BS', 'RIP', 'OMG'
    #     }
    
    # tickers = tickers_df['Symbol'].to_list()
    
    # df['removed_words'] = df['all_content'].replace(r'[{ignore_words}]'.format(ignore_words = ignore_words), '', regex = True)
    
    #df['removed_words'] = df['removed_words'].apply(lambda x: ignoreWords(x))
    
    #df['removed_words'] = df['all_content'].str.replace('|'.join("((?<=\s)|(?<=^)){}((?=\s)|(?=$))".format(i) for i in ignore_words), '', regex = True)
    
   
    
    #re.sub('|'.join("((?<=\s)|(?<=^)){}((?=\s)|(?=$))".format(i) for i in ticker_lst), '', text2)
    
    # Create a new column called "removed_words" to show the text after all
    # necessary words (ignored_words) are removed
    df['removed_words'] = df['all_content'].map(lambda x: ignoreWords(x))
    

    # print('Just Finished Removing Words')
    
    #df['without_ticker'] = df['all_content'].str.replace('|'.join("((?<=\s)|(?<=^)){}((?=\s)|(?=$))".format(i) for i in tickers), '', regex = True)
    
    # Create a new column called "ticker" to place the ticker identified
    df['ticker'] = df['removed_words'].map(lambda x: stockSearch(x.split(), t_df))
    
    
    # def pattern_searcher(search_str:str, search_list:str):

    # search_obj = re.search(search_list, search_str)
    # if search_obj :
    #     return_str = search_str[search_obj.start(): search_obj.end()]
    # else:
    #     return_str = 'NA'
    # return return_str
    #df['all_tickers'] = reddit_df['removed_words'].replace(r'[^{tickers}]'.format(tickers = tickers), '', regex = True)
    
    #df['tickers'] = reddit_df['all_tickers'].map(lambda x: ignoreWords(x))
    
    
    # re.sub(r'[^\s|{tickers}]'.format(tickers = tickers), '', text)
    
    # re.sub(r'[^\s|AAPL|TSLA]', '', text)
    
    # conditions = list(map(df['removed_words'].str.contains, list(tickers_df.Symbol)))
    # reddit_df['tickers'] = np.select(conditions, list(tickers_df.Symbol), np.nan)
    
    # for row in range(len(df)):
        
    #     text_lst = df['title'].iat[row].split()
        
    #     for word in list(text_lst):
    #         if word in ignore_words:
    #             text_lst.remove(word)
                
    #     for stock in tickers_df['Symbol'].to_list():
    #         if stock in text_lst:
    #             df['all_content'].iloc[row] = stock
    #             break
            
        # for word in text_lst:
        #     if word in tickers_df['Symbol'].to_list():
        #         df['title_ticker'].iloc[row] = word
        #         break
            
        
        # for word in df['title'].iat[row].split():
        #     # print(df['title'].iat[row].split()
        #     if word in tickers_df['Symbol'].to_list():
        #         # print(word)
        #         # print(row)
        #         df['title_ticker'].iloc[row] = word
        #         break
        
    
        
            # else:
            #     df['title_ticker'].iloc[row] = np.nan
                
            # else:
            #     title_lst.append([np.nan])
    
    #ticker_lst = df['title'].map(lambda word: word if word in nasdaq_df['Symbol'].values)
    
    # for row in range(len(df)):
        
    #     for word in df['title'].iat[row]:
            
    #         if word.upper() == nasdaq_df['Symbol'].values:
                
    # print(lst)
    # df['title_ticker'] = lst
    
    # Only takes rows where a stock ticker has been identified
    df = df[df['ticker'].notna()].reset_index(drop = True)
    
    # Returns the DataFrame to main to be outputted as csv
    return df
        
def main():
    
    # Track start time
    start = time.time()
    
    # Path to access and output files
    path = r'/Users/XFlazer/Documents/HKU/FBE/Finance/Natural Language Processing/Reddit Project'
    
    # Read all reddit csv files as DataFrame
    reddit_2018 = pd.read_csv(path + os.sep + 'Reddit WSB Data with most upvote comments 2018-09-01 to 2018-12-31.csv')
    reddit_2019 = pd.read_csv(path + os.sep + 'Reddit WSB Data with most upvote comments 2019-01-01 to 2019-12-31.csv')
    reddit_2020 = pd.read_csv(path + os.sep + 'Reddit WSB Data with most upvote comments 2020-01-01 to 2020-12-31.csv')
    reddit_2021 = pd.read_csv(path + os.sep + 'Reddit WSB Data with most upvote comments 2021-01-01 to 2021-12-31.csv')
    
    # Make a copy to not affect original DataFrame
    r_18 = reddit_2018.copy()
    r_19 = reddit_2019.copy()
    r_20 = reddit_2020.copy()
    r_21 = reddit_2021.copy()
    
    # Place them into a list to combine them
    r_lst = [r_18, r_19, r_20, r_21]
    
    # Combine all reddit DataFrames
    reddit_df = combineDF(r_lst)
    
    # Clean the data
    reddit_df = cleanData(reddit_df)
    
    # Read all stock ticker csv files as DataFrames
    nasdaq_df = pd.read_csv(path + os.sep + 'Nasdaq.csv')
    nyse_df = pd.read_csv(path + os.sep + 'Nyse.csv')
    amex_df = pd.read_csv(path + os.sep + 'Amex.csv')
    
    # Place them into a list to combine them
    tickers_lst = [nasdaq_df, nyse_df, amex_df]
    
    # Combine all stock ticker DataFrames
    tickers_df = combineDF(tickers_lst)
    
    # Match the stock mentioned in text to a real stock ticker
    reddit_df = stockMatch(reddit_df, tickers_df)
    
    # Output file as csv for further analysis
    reddit_df.to_csv(path + os.sep + 'reddit_with_ticker.csv', index = False)
    
    # Prints out how long the program took in seconds
    print('The time it took to run the program:', time.time() - start, 'seconds')

# Calls main program
main()

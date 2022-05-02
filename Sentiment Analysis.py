Python 3.10.3 (tags/v3.10.3:a342a49, Mar 16 2022, 13:07:40) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
#!/usr/bin/env python
# coding: utf-8

# Import the necessary libraries
import pandas as pd 
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Setting up a dictionary with wsb terminology 
# https://github.com/mdominguez2010/wsb-sentiment-analysis/blob/main/stocks_to_trade.py
wsb_lingo = {
    'citron': -4.0,  
    'hidenburg': -4.0,        
    'moon': 4.0,
    'highs': 2.0,
    'mooning': 4.0,
    'long': 2.0,
    'short': -2.0,
    'call': 4.0,
    'calls': 4.0,    
    'put': -4.0,
    'puts': -4.0,    
    'break': 2.0,
    'tendie': 2.0,
    'tendies': 2.0,
    'town': 2.0,     
    'overvalued': -3.0,
    'undervalued': 3.0,
    'buy': 4.0,
    "hold": 1.0,
    'sell': -4.0,
    'gone': -1.0,
    'gtfo': -1.7,
    'paper': -1.7,
    'bullish': 3.7,
    'bearish': -3.7,
    'bagholder': -1.7,
    'stonk': 1.9,
    'green': 1.9,
    'money': 1.2,
    'print': 2.2,
    'rocket': 2.2,
    'bull': 2.9,
    'bear': -2.9,
    'pumping': -1.0,
    'sus': -3.0,
    'offering': -2.3,
    'rip': -4.0,
    'downgrade': -3.0,
    'upgrade': 3.0,     
    'maintain': 1.0,          
    'pump': 1.9,
    'hot': 1.5,
    'drop': -2.5,
    'rebound': 1.5,  
    'crack': 2.5,
    "BTFD": 4.0,
    "FD": 4.0,
    "diamond hands": 0.0,
    "paper hands": 0.0,
    "DD": 4.0,
    "GUH": -4.0,
    "pump": 4.0,
    "dump": -4.0,
    "gem stone": 4.0, # emoji
    "rocket": 4.0, # emoji
    "andromeda": 0.0,
    "to the moon": 4.0,
}

# Update the VADER Sentiment Analyzer with the above terms
sia = SentimentIntensityAnalyzer()
sia.lexicon.update(wsb_lingo)

# Import the cleaned dataframe from the previous step
cleaned_dataframe = pd.read_csv("reddit_with_ticker.csv", lineterminator = "\n") 

# Run the post content through VADER and store the output
sentiment_list = []
for content in cleaned_dataframe["all_content"]:
    sentiment_list.append([sia.polarity_scores(content)["neg"], sia.polarity_scores(content)["neu"], 
                      sia.polarity_scores(content)["pos"], sia.polarity_scores(content)["compound"]])
sentiment = pd.DataFrame(sentiment_list, columns = ["Sell Signal", "Hold Signal", "Buy Signal", "Compound Signal"])


# Combine the results with the original dataframe
df_concat = pd.concat([cleaned_dataframe, sentiment], axis=1)

# Save the new dataframe as a csv file
df_concat.to_csv('reddit_with_ticker_with_sentiment.csv')




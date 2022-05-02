Python 3.10.3 (tags/v3.10.3:a342a49, Mar 16 2022, 13:07:40) [MSC v.1929 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
#!/usr/bin/env python
# coding: utf-8

# Import the necessary modules
import os
import re
import pandas as pd
import numpy as np

# Obtains the percentiles for homogeneous data
def find_percentiles(data):
    p_20 = np.nanpercentile(data, 20)
    p_40 = np.nanpercentile(data, 40)
    p_60 = np.nanpercentile(data, 60)
    p_80 = np.nanpercentile(data, 80)
    return [p_20, p_40, p_60, p_80]

# Updates the sentiment score for homogeneous data
def updatep(column, data):

    # Store the percentiles in a list
    percentile = find_percentiles(df[column])

    # Split the data into 5 different categories based on percentile
    data[column + "_category"] = np.where(data[column] <= percentile[0], "E", data[column + "_category"])
    data[column + "_category"] = np.where((data[column] > percentile[0]) & (data[column] <= percentile[1]), "D", data[column + "_category"])
    data[column + "_category"] = np.where((data[column] > percentile[1]) & (data[column] <= percentile[2]), "C", data[column + "_category"])
    data[column + "_category"] = np.where((data[column] > percentile[2]) & (data[column] <= percentile[3]), "B", data[column + "_category"])
    data[column + "_category"] = np.where(data[column] > percentile[3], "A", data[column + "_category"])

    # Update the Sentiment score based on the category
    data["Updated Score"] = np.where(data[column + "_category"] == "E", data["Updated Score"]*0.5, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "D", data["Updated Score"]*0.75, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "C", data["Updated Score"]*1, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "B", data["Updated Score"]*1.25, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "A", data["Updated Score"]*1.5, data["Updated Score"])
    
    return data

# Updates the sentiment score for heterogeneous data
def updates(column, data):
        
    # Find the mean and standard deviations of the data
    mean = np.mean(df[column])
    sd = np.std(df[column])

    # Split the data into 5 categories according to mean plus varying mutiples of sd
    data[column + "_category"] = np.where((data[column] <= mean), "E", data[column + "_category"])
    data[column + "_category"] = np.where((data[column] > mean) & (data[column] <= mean+0.5*sd), "D", data[column + "_category"])
    data[column + "_category"] = np.where((data[column] > mean+0.5*sd) & (data[column] <= mean+sd), "C", data[column + "_category"])
    data[column + "_category"] = np.where((data[column] > mean+sd) & (data[column] <= mean+1.5*sd), "B", data[column + "_category"])
    data[column + "_category"] = np.where((data[column] > mean+1.5*sd), "A", data[column + "_category"])

    # Update the sentiment scores based on the category
    data["Updated Score"] = np.where(data[column + "_category"] == "E", data["Updated Score"]*0.8, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "D", data["Updated Score"]*0.9, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "C", data["Updated Score"]*1.1, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "B", data["Updated Score"]*1.4, data["Updated Score"])
    data["Updated Score"] = np.where(data[column + "_category"] == "A", data["Updated Score"]*1.8, data["Updated Score"])
        
    return data

# Import the dataframe from the previous step
df = pd.read_csv("reddit_with_ticker_with_sentiment.csv")

# Create new columns for categorization
df["upvotes_category"] = np.nan
df["num_crossposts_category"] = np.nan
df["num_comments_category"] = np.nan
df["comment_upvote_category"] = np.nan
df["upvote_ratio_category"] = np.nan
df["Updated Score"] = df.loc[:, 'Compound Signal']

# Run the above functions on the actual metrics
updatep("upvote_ratio", df)
updates("upvotes", df)
updates("num_crossposts", df)
updates("num_comments", df)
updates("comment_upvote", df)


# Save the updated dataframe as a csv file
df.to_csv("Updated_Data.csv")
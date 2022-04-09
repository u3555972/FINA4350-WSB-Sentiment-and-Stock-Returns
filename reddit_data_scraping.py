#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 20:25:39 2022

@author: HUNG Pui Kit
"""

# Import Modules #
import praw
import pandas as pd
import datetime as dt
import os
from psaw import PushshiftAPI
from praw.models import MoreComments

start_time = dt.datetime.now() 
def time_report():
    current_time = dt.datetime.now() 
    print('Time spent now: ', current_time - start_time)
    return

base_path = 'custom-defined export location'



# Key Variables #
start_scrape = dt.datetime(2021, 1, 1)
end_scrape = dt.datetime(2021, 12, 31)
start_time = dt.datetime.now() 
print('done')



# API Connection #
reddit = praw.Reddit(client_id='get it from reddit panel',
                     client_secret='get it from reddit panel',
                     user_agent='fina4350project',
                     check_for_async=False)

api = PushshiftAPI(reddit)

start_epoch=int(start_scrape.timestamp()) 
end_epoch=int(end_scrape.timestamp())

from_date = start_scrape.strftime('%Y-%m-%d')
to_date = end_scrape.strftime('%Y-%m-%d')

# time report
time_report()
print('API connected \n')



## Core Scraping Process ##
# 1. Use the PSAW library to generate the post IDs
start_time = dt.datetime.now()
print('running, please wait')
submissions_generator = api.search_submissions(after=start_epoch,
                                               before=end_epoch,
                                               subreddit='wallstreetbets',
                                               limit= None, #Scrape all posts
                                               score = ">1" #minimum upvote amount
                                               ) 
# return a list with post IDs
submissions = list(submissions_generator)
# time report
time_report()
print(len(submissions),'ID collected \n')


# 2. Use the PRAW library to scrape post details
posts = []
count = 0
comments_list = []

for submission_id in submissions:
    post = reddit.submission(id=submission_id)
    post_items = []
    comments_details = []
    

    # Scrape Comments
    for top_level_comment in post.comments:
        
        if isinstance(top_level_comment, MoreComments):
            comments_list.append(['no id',
                                  'no author',
                                      -100,
                                  'no comment',
                                      post.id])
            continue
        comments_list.append(['no id',
                              'no author',
                                      -100,
                              'no comment',
                                  post.id])
            
        comments_list.append([top_level_comment.id,
                                 top_level_comment.author,
                                 top_level_comment.score,
                                 top_level_comment.body,
                                 post.id])

    # Scrape other post details
    post_items.extend([post.id, post.created_utc, post.author, post.score,
                       post.num_crossposts, post.num_comments, post.upvote_ratio,
                       post.title, post.selftext, post.url, post.permalink])
    posts.append(post_items)
    count += 1

    # time report
    if count%10 ==0:
        time_report()
        print(count, ' posts collected')
        print('\n')
    
    
    

# Transform post details to a main dataframe  
posts = pd.DataFrame(posts, columns=['id', 'time', 'author', 'upvotes',
                                     'num_crossposts', 'num_comments', 'upvote_ratio',
                                     'title', 'content', 'url', 'permalink'])

# Transform comments details to another dataframe
comments_df = pd.DataFrame(comments_list, columns=['comment_id',
                                                   'comment_author',
                                                   'comment_upvote',
                                                   'comment_content',
                                                   'id'])

# Transfer Unix Time format to standard datetime format
posts['date'] = pd.to_datetime(posts['time'], utc=True, unit='s')
posts.pop('time')

# a new column to indicate whether the post maybe contains media by comparing url and permalink
posts['no_media']=posts['url'].str.contains('/r/wallstreetbets',regex=False)

#merge comments and main post details dataframe
posts = posts.merge(comments_df, how='left', on='id')


# reindex the dataframe
posts = posts.reindex(columns=['id', 'date', 'author', 'upvotes', 'no_media',
                               'num_crossposts', 'num_comments', 'upvote_ratio',
                               'comment_id','comment_author','comment_upvote','comment_content',
                               'title', 'content', 'url', 'permalink'])

time_report()
print('scrape done. exporting... \n')

# Export to CSV File
export_name = 'Reddit WSB Data with all comments ' + from_date + ' to ' + to_date + '.csv'
print('Export name: ', export_name)
posts.to_csv(os.path.join(base_path, export_name), index=False)
print('export complete')



# Modify the file
export_name = 'Reddit WSB Data with all comments ' + from_date + ' to ' + to_date + '.csv'
posts = pd.read_csv(base_path + os.sep + export_name)

posts_mod['upvotes'] = posts_mod['upvotes'].astype(int)
# Keep comments with highest upvote only
posts_mod['comment_upvote'] = posts_mod['comment_upvote'].fillna(-100).astype(int)
posts_mod = posts_mod.sort_values(by=['comment_upvote'], ascending=False).reset_index(drop=True)
posts_mod = posts_mod.drop_duplicates(subset=['id'],keep='first')

# Keep posts with upvote >=5


posts_mod = posts_mod[posts_mod['upvotes'] >=5 ]

# Export
posts_mod = posts_mod.sort_values(by=['date'], ascending=True).reset_index(drop=True)

mod_name = 'Reddit WSB Data with most upvote comments ' + from_date + ' to ' + to_date + '.csv'
posts_mod.to_csv(os.path.join(base_path, mod_name), index=False)
print('Modify done')

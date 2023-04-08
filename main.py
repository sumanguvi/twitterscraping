# --------------------------------------------------
# import libraries
# --------------------------------------------------

import streamlit as st
import pandas as pd
import datetime
import time

# !pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
# importing libraries and packages

import snscrape.modules.twitter as sntwitter
import pandas as pd
import pymongo
from pymongo import MongoClient

# --------------------------------------------------
# create connection to mongodb with pymongo
# --------------------------------------------------

# create client connection
twitter_client = MongoClient('mongodb://localhost:27017/')

# create database
mydb = twitter_client['twitter_db']

# create collection
twitter_collection = mydb['my_collection']

# -----------------------------
# date format
# -----------------------------
from datetime import datetime

# current time and date
# datetime object
time = datetime.now()
print("Without formatting:", time)

# formatting date using strftime
today_date = time.strftime("%d-%m-%Y")
# print("After formatting:", time.strftime("%d-%m-%Y"))

# --------------------------------------------------
# streamlit code
# --------------------------------------------------

# Functional Blocks

# 1. submit button function
#         st_submit_form()

# 2. function to create a dataframe from scraped tweets list
#         tw_list_to_df()

# 3. function to convert dataframe to csv
#         convert_df(df)

# 4. function to convert dataframe to json
#         convert_df_json(df)

# ---------------------------------------------------------------------------------

header = st.container()

with header:
    # st.header('''data science project - twitter_scraping''')
    st.markdown("<h2 style='text-align: center; color: white;'>Twitter_scraping project</h2>", unsafe_allow_html=True)
    # st.header('Twitter data scraping')
    st.markdown("<h6 style='text-align: center; color: white;'>[data scraping with Snscrape api]</h6>", unsafe_allow_html=True)
    st.text('')

# --------------------------------------------------
# create streamlit form
# --------------------------------------------------


twitterform = st.form(key='myform', clear_on_submit=True)

with twitterform:

    search = st.text_input('Enter the keyword or Hashtag to be searched', value='', key='word')
    result = search.title()

    startdate = st.date_input('Enter the start date :calendar:', key='sdate')

    enddate = st.date_input('Enter the end date :calendar:', key='edate')

    tweets_number = st.number_input('Enter number to scrape tweets', format=None, step=1)

    submit_form = st.form_submit_button()

tweets_list1 = []


# function to submit form
def st_submit_form():
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(
            f'{result},since:{startdate} until:{enddate}').get_items()):  # declare a username
        if i > tweets_number:  # number of tweets you want to scrape
            # st.error('Enter KEYWORD in Text Field and NUMBER in Number Field ', icon="🚨")
            break
        tweets_list1.append(
            [tweet.date, tweet.id, tweet.url, tweet.content, tweet.user.username, tweet.replyCount, tweet.retweetCount,
             tweet.lang, tweet.likeCount, tweet.source])  # declare the attributes to be returned

    mongo_data = {'Scraped Word': result, 'Scraped Date': today_date, 'Scraped Data': tweets_list1}
    rec = mydb.twitter_collection.insert_one(mongo_data)
    st.success('twitter scraping is successful and the data is stored in mongodb', icon="✅")

# main()
if result and tweets_number:
    if submit_form:
        st_submit_form()
else:
    if submit_form:
        st.error('you have to enter values in all fields , all fields are mandatory')


# function to Create a dataframe from the tweets list above

def tw_list_to_df():
    # Create a dataframe with date, id, url, tweet content, user,reply count, retweet count,language,
    # source, like count.

    tweetsdf = pd.DataFrame(tweets_list1,
                            columns=['Datetime', 'Tweet Id', 'URL', 'Text', 'Username', 'ReplyCount', 'RetweetCount',
                                     'Language', 'LikeCount', 'Source'])
    return tweetsdf


tweets_df = tw_list_to_df()


# st.dataframe(tweets_df)

# IMPORTANT: Cache the conversion to prevent computation on every rerun
@st.cache_data
# --------------------------------------------------
# STREAMLIT - DOWNLOAD DATA
# --------------------------------------------------
# function to convert dataframe to csv
def convert_df(df):
    return tweets_df.to_csv().encode('utf-8')


csv = convert_df(tweets_df)

st.download_button(
    label='Download data as csv',
    data=csv,
    file_name='tweets_data.csv',
    mime='text/csv'
)


# function to convert dataframe to json
def convert_df_json(df):
    return df.to_json().encode('utf-8')


tweets_json = convert_df_json(tweets_df)
tweets_json_string = tweets_df.to_json(orient='records')
st.download_button(
    label='Download data as json',
    data=tweets_json,
    file_name='tweets_data.json',
    mime='application/json'
)

#
# --------------------------------------------------
# create connection to mongodb with pymongo
# --------------------------------------------------

# create client connection
twitter_upload_conn = MongoClient('mongodb://localhost:27017/')

# create database
twitter_upload_db = twitter_upload_conn['tw_upload_db']

# create collection
twitter_upload_collection = twitter_upload_db['my_collection']

# ------------------------------------------------------------------------------------

uploaded_file = st.file_uploader('Choose a file', type=['csv'])
if uploaded_file is not None:
    file_details = {'FileName': uploaded_file.name, 'FileType': uploaded_file.type}
    tw_upload_csv = pd.read_csv(uploaded_file)
    # To convert a dataframe to a dictionary
    df_uploaded = tw_upload_csv.to_dict("records")
    # st.write(file_details)
    # streamlit to mongodb -> csv - dataframe - dictionary
    # tw_upload = twitter_upload_db.twitter_collection.insert_many(df_uploaded)
    mongo_data = {'Scraped Word': result, 'Scraped Date': today_date, 'Scraped Data': df_uploaded}
    tw_upload = twitter_upload_db.twitter_collection.insert_one(mongo_data)

    st.success('twitter data upload is successful and the data is stored in mongodb', icon="✅")
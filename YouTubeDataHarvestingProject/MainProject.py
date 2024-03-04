#Importing required packages
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
import re
import mysql.connector
import googleapiclient.discovery

import streamlit as st
import time
import pymongo
import plotly.express as px

#================================= CONNECTION ===============================#

#block of code to establish youtube api connection
api_key="AIzaSyCFga0poMf8o_yD9vC3ItCmLK7TuUU35rw"
api_service_name = "youtube"
api_version = "v3"

youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

#block of code to establish connection with mysql and create database named youtube
mycon = mysql.connector.connect(host="127.0.0.1",user="root",password="#Saravanan27")
mycursor = mycon.cursor()
mycursor.execute(f"CREATE DATABASE IF NOT EXISTS youtube;")

#block of code to establish connection with Mongodb and create database to store the data
mongo = pymongo.MongoClient('mongodb://localhost:27017')
mydb = mongo["YOUTUBE"]
mycollection = mydb['DATA']

#================================= NAVIGATION PANEL ============================#

#line of code to create a navigation panel
nav = st.sidebar.radio("Navigation panel",['HOME','JSON Data','SQL - TABLE','DATA ANALYSIS'])

#=============================== FUNCTION FOR DATA FETCH ==========================#

# function have been created to fetch the data
def data_ch(yt_ch_id):
    curr_channel = {}  # empty dictionary created to store the data

    # block of code to fetch required data from the list channel
    ch_request = youtube.channels().list(part="snippet,contentDetails,statistics,topicDetails",id=  yt_ch_id)
    ch_response = ch_request.execute()
    ch_name = (ch_response['items'][0]['snippet']['title'])
    ch_id = (ch_response['items'][0]['id'])
    vid_count = (ch_response['items'][0]['statistics']['videoCount'])
    sub_count = (ch_response['items'][0]['statistics']['subscriberCount'])
    ch_views = (ch_response['items'][0]['statistics']['viewCount'])
    ch_desc = (ch_response['items'][0]['snippet']['description'])
    pl_id = (ch_response['items'][0]['contentDetails']['relatedPlaylists']['uploads'])

    # block of code that creates the dictionary with required keys and values
    ch_info = {"Channel Name": {"channel_name": ch_name,
                                "Channel_Id": ch_id,
                                "Video_count": vid_count,
                                "Subscription_Count": sub_count,
                                "Channel_Views": ch_views,
                                "Channel_Description": ch_desc,
                                "Playlist_Id": pl_id}}

    curr_channel.update(ch_info)  # channel data have been successfully updated to the empty dictionary

    # block of code to fetch required data from the list playlist
    request = youtube.playlistItems().list(part="snippet", playlistId=(ch_info["Channel Name"]["Playlist_Id"]),maxResults=50)
    response = request.execute()

    vid_id = []  # an empty list have been created to append the iterated video data

    # itertating the list of video id from playlist
    for i in range(len(response['items'])):
        vid_id.append(response['items'][i]['snippet']['resourceId']['videoId'])

    # To iterate video id from the video ID list
    for i in range(len(vid_id)):

        # video data request
        vid_request = youtube.videos().list(part="snippet,contentDetails,statistics", id=vid_id[i])
        vid_response = vid_request.execute()

        # block of code to fetch required data from the list video
        vi_id = (vid_response['items'][0]['id'])
        vi_name = (vid_response['items'][0]['snippet']['localized']['title'])
        vi_desc = (vid_response['items'][0]['snippet']['localized']['description'])
        vi_tags = (vid_response['items'][0]['snippet']['tags']) if (vid_response['items'][0]['snippet']) == ['tags'] else "Not Available"
        vi_pub = (vid_response['items'][0]['snippet']['publishedAt'])
        vi_view = (vid_response['items'][0]['statistics']['viewCount'])
        vi_like = (vid_response['items'][0]['statistics'].get('likeCount'))
        vi_favrt = (vid_response['items'][0]['statistics']['likeCount'])
        vi_cmnt = (vid_response['items'][0]['statistics']['commentCount'])
        vi_dur = (vid_response['items'][0]['contentDetails']['duration'])
        vi_thumb = (vid_response['items'][0]['snippet']['thumbnails']['default']['url'])
        vi_cap = (vid_response['items'][0]['contentDetails']['caption'])
        vi_cap_st = "Available" if (vid_response['items'][0]['contentDetails']['caption']) else "Not Available"
        j = i + 1

        # function have been created to convert the format of duration of the video
        def conv_dur(duration):
            regex = r'PT(\d+H)?(\d+M)?(\d+S)?'
            match = re.match(regex, duration)
            if not match:
                return '00:00:00'
            hours, minutes, seconds = match.groups()
            hours = int(hours[:-1]) if hours else 0
            minutes = int(minutes[:-1]) if minutes else 0
            seconds = int(seconds[:-1]) if seconds else 0
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return '{:02d}:{:02d}:{:02d}'.format(int(total_seconds / 3600), int((total_seconds % 3600) / 60),int(total_seconds % 60))

        # block of code that creates the dictionary with required keys and values
        video_id = {fr"video_id_{j}":
                        {"Video_Id": vi_id,
                         "Video_Name": vi_name,
                         "Video_Description": vi_desc,
                         "Tags": list(vi_tags),
                         "PublishedAt": vi_pub,
                         "View_Count": vi_view,
                         "Like_Count": vi_like,
                         "Favorite_Count": vi_favrt,
                         "Comment_Count": vi_cmnt,
                         "Duration": conv_dur(vi_dur),
                         "Thumbnail": vi_thumb,
                         "Caption_Status": vi_cap_st,
                         "Comments": {}}}

        # comment data request
        cmt_request = youtube.commentThreads().list(part='snippet, replies', videoId=vid_id[i], maxResults=10)
        cmt_response = cmt_request.execute()

        # block of code to iterate the comment list and append it with the respective video
        for m in range(len(cmt_response["items"])):
            comm_id = (cmt_response['items'][m]['snippet']['topLevelComment']['id'])
            comm_txt = (cmt_response['items'][m]['snippet']['topLevelComment']['snippet']['textOriginal'])
            comm_auth = (cmt_response['items'][m]['snippet']['topLevelComment']['snippet']['authorDisplayName'])
            comm_pub = (cmt_response['items'][m]['snippet']['topLevelComment']['snippet']['publishedAt'])
            n = m + 1

            # block of code that creates the dictionary with required keys and values
            comments = {fr"Comment_Id_{n}": {"Comment_Id": comm_id,
                                             "Comment_Text": comm_txt,
                                             "Comment_Author": comm_auth,
                                             "Comment_PublishedAt": comm_pub}}

            video_id[fr"video_id_{j}"]["Comments"].update(comments)  # to append to the respective video

        curr_channel.update(video_id)  # updating the video data with the previously stored channel data

    mycollection.insert_one(curr_channel)  # storing the fetched data to the Mongodb
    return curr_channel


#================================== JSON DATA DISPLAY PAGE ==================================#

# defining the JSON DATA page
if nav == "JSON Data":
    if st.session_state.ch_id:  # process only if the input have been passed
        # progress bar have been defined for design
        pro = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            pro.progress(i + 1)
        # block of code to display the data from mongodb
        mongo = pymongo.MongoClient("mongodb://localhost:27017/")
        mydb = mongo["YOUTUBE"]
        mycollection = mydb['DATA']
        dbcursor = mycollection.find({})
        for document in dbcursor:
            st.write(document)

    else:  # Display error if the input have not been passed
        st.error("*Enter Channel ID in HOME PAGE*")


#================================== FUNCTION TO CONVERT NOSQL DATA INTO SQL ========================#

#function defined to convert nosql to sql
def sql_conv(result):
    #block of code to create dataframe for channel data
    ch_list=[]
    ch_sql = {"Channel_Id": result['Channel Name']['Channel_Id'],
              "channel_name": result['Channel Name']['channel_name'],
              "Video_Count": result['Channel Name']['Video_count'],
              "Subscriber_Count": result['Channel Name']["Subscription_Count"],
              "Channel_Views": result['Channel Name']['Channel_Views'],
              "Channel_Description": result['Channel Name']['Channel_Description']}
    ch_list.append(ch_sql)
    ch_df = pd.DataFrame(ch_list)
    #block of code to create dataframe for playlist data
    pl_list=[]
    pl_sql = {"Playlist_Id": result['Channel Name']['Playlist_Id'],"Channel_Id": result['Channel Name']['Channel_Id']}
    pl_list.append(pl_sql)
    pl_df= pd.DataFrame(pl_list)
    #block of code to create dataframe for video data
    cmt_sql_list = []
    vid_sql_list=[]
    for i in range(1, len(result) - 1):

        vid_sql = {"Video_Id": result[f"video_id_{i}"]['Video_Id'],
                   "Playlist_id":result['Channel Name']['Playlist_Id'],
                   "Video_Name": result[f"video_id_{i}"]['Video_Name'],
                   "Video_Description": result[f"video_id_{i}"]['Video_Description'],
                   "PublishedAt": result[f"video_id_{i}"]['PublishedAt'],
                   "View_Count": result[f"video_id_{i}"]['View_Count'],
                   "Like_Count": result[f"video_id_{i}"]['Like_Count'],
                   "Favorite_Count": result[f"video_id_{i}"]['Favorite_Count'],
                   "Comment_Count": result[f"video_id_{i}"]['Comment_Count'],
                   "Duration": result[f"video_id_{i}"]['Duration'],
                   "Thumbnail": result[f"video_id_{i}"]['Thumbnail'],
                   "Caption_Status": result[f"video_id_{i}"]['Caption_Status']}
        vid_sql_list.append(vid_sql)
        video_df = pd.DataFrame(vid_sql_list)

        #block of code to create dataframe for comment data
        for j in range(1,len(result[f"video_id_{i}"]['Comments'])):
            comment_data_sql = {"Comment_Id": result[f"video_id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_Id'],
                                "Video_Id": result[f"video_id_{i}"]['Video_Id'],
                                "Comment_Text": result[f"video_id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_Text'],
                                "Comment_Author": result[f"video_id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_Author'],
                                "Comment_PublishedAt": result[f"video_id_{i}"]['Comments'][f"Comment_Id_{j}"]['Comment_PublishedAt']}
            cmt_sql_list.append(comment_data_sql)
            Comments_df = pd.DataFrame(cmt_sql_list)

    return {'A':ch_df,'B':pl_df,'C':video_df,'D':Comments_df}


#============================ FUNCTION FOR DATATYPE DECLARATION AND CONVERTING DATAFRAME TO SQL =========================#

#function to declare datatype and covert df to sql table
def table(df):
    #accessing the sql conv function
    channel_df =df['A']
    video_df = df['C']
    Comments_df = df['D']
    playlist_df = df['B']
       #creating a engine using sqlalchemy for datatype decalaration
    engine = create_engine('mysql+mysqlconnector://root:#Saravanan27@localhost/youtube', echo=False)
    #converting channel dataframe to sql table channel
    channel_df.to_sql('channel', engine, if_exists='append', index=False,
                      dtype={"Channel_Name": sqlalchemy.types.VARCHAR(length=225),
                             "Channel_Id": sqlalchemy.types.VARCHAR(length=225),
                             "Video_count": sqlalchemy.types.INT,
                             "Subscriber_Count": sqlalchemy.types.BigInteger,
                             "Channel_Views": sqlalchemy.types.BigInteger,
                             "Channel_Description": sqlalchemy.types.TEXT,
                             "Playlist_Id": sqlalchemy.types.VARCHAR(length=225), })
       #converting playlist dataframe to sql table playlist
    playlist_df.to_sql('playlist', engine, if_exists='append', index=False,
                       dtype={"Channel_Id": sqlalchemy.types.VARCHAR(length=225),
                              "Playlist_Id": sqlalchemy.types.VARCHAR(length=225), })
       #converting video dataframe to sql table video
    video_df.to_sql('video', engine, if_exists='append', index=False,
                    dtype={'Video_Id': sqlalchemy.types.VARCHAR(length=225),
                           'Playlist_Id': sqlalchemy.types.VARCHAR(length=225),
                           'Video_Name': sqlalchemy.types.VARCHAR(length=225),
                           'Video_Description': sqlalchemy.types.TEXT,
                           'Published_date': sqlalchemy.types.String(length=50),
                           'View_Count': sqlalchemy.types.BigInteger,
                           'Like_Count': sqlalchemy.types.BigInteger,
                           'Favorite_Count': sqlalchemy.types.INT,
                           'Comment_Count': sqlalchemy.types.INT,
                           'Duration': sqlalchemy.types.VARCHAR(length=1024),
                           'Thumbnail': sqlalchemy.types.VARCHAR(length=225),
                           'Caption_Status': sqlalchemy.types.VARCHAR(length=225), })
       #converting comments dataframe to sql table comments
    Comments_df.to_sql('comments', engine, if_exists='append', index=False,
                       dtype={'Video_Id': sqlalchemy.types.VARCHAR(length=225),
                              'Comment_Id': sqlalchemy.types.VARCHAR(length=225),
                              'Comment_Text': sqlalchemy.types.TEXT,
                              'Comment_Author': sqlalchemy.types.VARCHAR(length=225),
                              'Comment_Published_date': sqlalchemy.types.String(length=50), })


#============================= HOME PAGE ===========================#


#defining the HOME PAGE
if nav=="HOME":
    st.title("PROJECT")
    st.subheader("DS_YouTube Data Harvesting and Warehousing using SQL, MongoDB and Streamlit")
    st.markdown(" ### AIM")
    st.write("This project aims to develop a user-friendly Streamlit application that utilizes the Google API to extract information on a YouTube channel, stores it in a MongoDB database, migrates it to a SQL data warehouse, and enables users to search for channel details and join tables to view data in the Streamlit app.")
    ch_id1= st.text_input("Channel ID")
    st.session_state['ch_id'] = ch_id1
    #runs only if the input has been given and press the run button
    if st.button("Run") and len(st.session_state.ch_id) == 24:
        st.session_state.results = data_ch(st.session_state.ch_id) # initialize fetching the data
        st.balloons()
        st.success("Data for concerned channel has been successfully retrived!")
        st.info(" *FOR MORE OPTIONS :* Kindly help yourself through navigation panel ")
        df = sql_conv(st.session_state.results)#initialize converting nosql to sql
        mycon = mysql.connector.connect(host="127.0.0.1", user="root", password="#Saravanan27",database='youtube')
        mycursor = mycon.cursor()
        table(df)#initialize declaring datatype and inserting data for sql

    if len(st.session_state.ch_id) != 24:#error occurs if the id is invalid
        st.error("Kindly Enter Valid Channel ID")

#============================= INITIATING SQL TABULATION AND DISPLAY THE TABLE ================================#

#defining SQL_TABLE page to display table
if nav == "SQL - TABLE":
    if st.session_state.ch_id:#process only if the input have been passed
        mycon = mysql.connector.connect(host="127.0.0.1", user="root", password="#Saravanan27",database='youtube')
        mycursor = mycon.cursor()
        #block of code to display table channel
        if st.checkbox("Channel Data"):
            st.subheader("TABLE_CHANNEL")
            mycursor.execute('SELECT * FROM channel;')
            ch_data = mycursor.fetchall()
            ch_df = pd.DataFrame(ch_data, columns=[i[0] for i in mycursor.description])
            st.dataframe(ch_df)
        #block of code to display table playlist
        if st.checkbox("Playlist Data"):
            st.subheader("TABLE_PLAYLIST")
            mycursor.execute('SELECT * FROM playlist;')
            pl_data = mycursor.fetchall()
            pl_df = pd.DataFrame(pl_data, columns=[i[0] for i in mycursor.description])
            st.dataframe(pl_df)
        #block of code to display table comments
        if st.checkbox("Comment Data"):
            st.subheader("TABLE_COMMENTS")
            mycursor.execute('SELECT * FROM comments;')
            cmt_data = mycursor.fetchall()
            cmt_df = pd.DataFrame(cmt_data, columns=[i[0] for i in mycursor.description])
            st.dataframe(cmt_df)
        #block of code to display table video
        if st.checkbox("Video Data"):
            st.subheader("TABLE_VIDEO")
            mycursor.execute('SELECT * FROM video;')
            vid_data = mycursor.fetchall()
            vid_df = pd.DataFrame(vid_data, columns=[i[0] for i in mycursor.description])
            st.dataframe(vid_df)

    else:#Display error if the input have not been passed
        st.error("*Enter Channel ID in HOME PAGE*")



#============================ DATA ANALYSIS SECTION =============================#

# defining DATA ANALYSIS page to display the anaysed data
if nav == "DATA ANALYSIS":
    if st.session_state.ch_id:  # process only if the input have been passed
        st.title("DATA ANALYSIS")
        # queries have been listed using a selectbox
        queries = st.selectbox('*Select your Question*',
                               ('1. What are the names of all the videos and their corresponding channels?',
                                '2. Which channels have the most number of videos, and how many videos do they have?',
                                '3. What are the top 10 most viewed videos and their respective channels?',
                                '4. How many comments were made on each video, and what are their corresponding video names?',
                                '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
                                '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
                                '7. What is the total number of views for each channel, and what are their corresponding channel names?',
                                '8. What are the names of all the channels that have published videos in the year 2022?',
                                '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
                                '10. Which videos have the highest number of comments, and what are their corresponding channel names?'),
                               key='collection_question')
        mycon = mysql.connector.connect(host="127.0.0.1", user="root", password="#Saravanan27", database='youtube')
        mycursor = mycon.cursor()
        # block of code to analyse 1st query
        if queries == '1. What are the names of all the videos and their corresponding channels?':
            mycursor.execute(
                "SELECT channel.Channel_Name, video.Video_Name FROM channel JOIN playlist JOIN video ON channel.Channel_Id = playlist.Channel_Id AND playlist.Playlist_Id = video.Playlist_Id;")
            result_1 = mycursor.fetchall()
            df1 = pd.DataFrame(result_1, columns=['Channel Name', 'Video Name']).reset_index(drop=True)
            df1.index += 1
            st.dataframe(df1)
        # block of code to analyse 2nd query
        elif queries == '2. Which channels have the most number of videos, and how many videos do they have?':
            mycursor.execute("SELECT Channel_Name, Video_Count FROM channel ORDER BY Video_Count DESC;")
            result_2 = mycursor.fetchall()
            df2 = pd.DataFrame(result_2, columns=['Channel Name', 'Video Count']).reset_index(drop=True)
            df2.index += 1
            st.dataframe(df2)
        # block of code to analyse 3rd query
        elif queries == '3. What are the top 10 most viewed videos and their respective channels?':
            col1, col2 = st.columns(2)
            with col1:
                mycursor.execute(
                    "SELECT channel.Channel_Name, video.Video_Name, video.View_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.Playlist_Id = video.Playlist_Id ORDER BY video.View_Count DESC LIMIT 10;")
                result_3 = mycursor.fetchall()
                df3 = pd.DataFrame(result_3, columns=['Channel Name', 'Video Name', 'View count']).reset_index(
                    drop=True)
                df3.index += 1
                st.dataframe(df3)

            with col2:
                fig_topvc = px.bar(df3, y='View count', x='Video Name', text_auto='.2s',
                                   title="Top 10 most viewed videos")
                fig_topvc.update_traces(textfont_size=18, marker_color='#F3ff5c')
                fig_topvc.update_layout(title_font_color='#5cfff0 ', title_font=dict(size=30))
                st.plotly_chart(fig_topvc, use_container_width=True)
        # block of code to analyse 4th query
        elif queries == '4. How many comments were made on each video, and what are their corresponding video names?':
            mycursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.Comment_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.Playlist_Id = video.Playlist_Id;")
            result_4 = mycursor.fetchall()
            df4 = pd.DataFrame(result_4, columns=['Channel Name', 'Video Name', 'Comment count']).reset_index(drop=True)
            df4.index += 1
            st.dataframe(df4)

        # block of code to analyse 5th query
        elif queries == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
            mycursor.execute(
                "SELECT channel.Channel_Name, video.Video_Name, video.Like_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.Playlist_Id = video.Playlist_Id ORDER BY video.Like_Count DESC;")
            result_5 = mycursor.fetchall()
            df5 = pd.DataFrame(result_5, columns=['Channel Name', 'Video Name', 'Like count']).reset_index(drop=True)
            df5.index += 1
            st.dataframe(df5)
        # block of code to analyse 6th query
        elif queries == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
            st.write('*Note:- In November 2021, YouTube removed the public dislike count from all of its videos.*')
            mycursor.execute(
                "SELECT channel.Channel_Name, video.Video_Name, video.Like_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.Playlist_Id = video.Playlist_Id ORDER BY video.Like_Count DESC;")
            result_6 = mycursor.fetchall()
            df6 = pd.DataFrame(result_6, columns=['Channel Name', 'Video Name', 'Like count']).reset_index(
                drop=True)
            df6.index += 1
            st.dataframe(df6)
        # block of code to analyse 7th query
        elif queries == '7. What is the total number of views for each channel, and what are their corresponding channel names?':

            col1, col2 = st.columns(2)
            with col1:
                mycursor.execute("SELECT Channel_Name, Channel_Views FROM channel ORDER BY Channel_Views DESC;")
                result_7 = mycursor.fetchall()
                df7 = pd.DataFrame(result_7, columns=['Channel Name', 'Total number of views']).reset_index(drop=True)
                df7.index += 1
                st.dataframe(df7)

            with col2:
                fig_topview = px.bar(df7, y='Total number of views', x='Channel Name', text_auto='.2s',
                                     title="Total number of views", )
                fig_topview.update_traces(textfont_size=18, marker_color='#F3ff5c')
                fig_topview.update_layout(title_font_color='#5cfff0 ', title_font=dict(size=30))
                st.plotly_chart(fig_topview, use_container_width=True)
        # block of code to analyse 8th query
        elif queries == '8. What are the names of all the channels that have published videos in the year 2022?':
          mycursor.execute("SELECT channel.Channel_Name, video.Video_Name, video.PublishedAt FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.Playlist_Id = video.Playlist_Id WHERE EXTRACT(YEAR FROM PublishedAt) = 2022;")
          result_8 = mycursor.fetchall()
          print(result_8)  # Add this line to check the retrieved data
          df8 = pd.DataFrame(result_8, columns=['Channel Name', 'Video Name', 'Year 2022 only']).reset_index(drop=True)
          df8.index += 1
          st.dataframe(df8)
        # block of code to analyse 9th query
        elif queries == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
            mycursor.execute(
                "SELECT channel.Channel_Name, TIME_FORMAT(SEC_TO_TIME(AVG(TIME_TO_SEC(TIME(video.Duration)))), '%H:%i:%s') AS duration  FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.Playlist_Id = video.Playlist_Id GROUP by Channel_Name ORDER BY duration DESC;")
            result_9 = mycursor.fetchall()
            print(result_9)  # Add this line to check the retrieved data
            df9 = pd.DataFrame(result_9, columns=['Channel Name', 'Average duration of videos (HH:MM:SS)']).reset_index(drop=True)
            df9.index += 1
            st.dataframe(df9)
        # block of code to analyse 10th query
        elif queries == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
            mycursor.execute(
                "SELECT channel.Channel_Name, video.Video_Name, video.Comment_Count FROM channel JOIN playlist ON channel.Channel_Id = playlist.Channel_Id JOIN video ON playlist.Playlist_Id = video.Playlist_Id ORDER BY video.Comment_Count DESC;")
            result_10 = mycursor.fetchall()
            df10 = pd.DataFrame(result_10, columns=['Channel Name', 'Video Name', 'Number of comments']).reset_index(
                drop=True)
            df10.index += 1
            st.dataframe(df10)

        mycon.close()

    else:  # Display error if the input have not been passed
        st.error("*Enter Channel ID in HOME PAGE*")
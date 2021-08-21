from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
import tweepy 
from textblob import TextBlob 
import pandas as pd
import numpy as np
import urllib.request
import re
import os

# Home and Intro page
def homepage(request):
    return render(request, "main/home.html", {})

# Returns the authenticated Tweepy api
def get_tweepy():
    try:
        consumer_key = os.environ.get('C_K')
        consumer_secret = os.environ.get('C_S')
        access_token = os.environ.get('A_T')
        access_token_secret = os.environ.get('A_T_S')

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth, wait_on_rate_limit = True)

        return api
    
    except Exception as e:
        print(e)

# returns the cleaned tweet text
def cleanTxt(text):
    #removes @mentions
    text = re.sub(r'@[A-Za-z0-9]+', '', text)
    #removes hashtags
    text = re.sub(r'#', '', text)
    #removes RT
    text = re.sub(r'RT[\s]+', '', text)
    #removes hyper link
    text = re.sub(r'https?:\/\/\S+', '', text)

    return text

# Returns polarity of the sentiments
def getPolarity(text):
    return TextBlob(text).sentiment.polarity


# Analyzes the polarity of the sentiments
def getAnalysis(score):
    if score < 0:
        return 'Negative'
    
    elif score == 0:
        return "Neutral"

    else:
        return 'Positive'

# result page shows the analyzation of the data
def result(request):
    if request.method == "POST":
        try:
            # Gets the text from the input bar
            text = request.POST.get('text')

            api = get_tweepy()

            # Searches for 500 tweets that contain the text
            cursor = api.search(text, count=1200, lang="en")

            # Adds Tweets found to a set to remove duplicate ones
            Tweets = set()
            for t in cursor:
                Tweets.add(t.text)

            # Creates a dataframe with a column for the tweets found
            df = pd.DataFrame(data=[tweet for tweet in Tweets], columns=['Tweets'])
            pd.set_option('display.max_colwidth', None)

            #  Gets the links of the tweets that exist in the Tweets set only
            links = []
            for i in Tweets:
                for s in cursor:
                    if s.text == i:
                        links.append("https://twitter.com/twitter/statuses/" + str(s.id))
                        break
                    
            # Creates a new column for links
            df["Links"] = links

            # Displays error message if the dataframe is empty
            if df.empty:
                messages.error(request, "Invalid Input")
                return render(request, 
                    "main/home.html", 
                    {})
            
            # Applies tweet text cleaning
            df['Tweets'] = df['Tweets'].apply(cleanTxt) 
            # Applies getPolarity to the Tweets column and creates a Polarity column with the resuts
            df['Polarity'] = df['Tweets'].apply(getPolarity)
            # Applies getAnalysis to the Polarity column and creates Analysis column with the results
            df['Analysis'] = df['Polarity'].apply(getAnalysis)

            # Add the links to a new column in the dataframe
            df["Links"] = links
            
            # List for tweet objects
            objects = []

            # Counting how many tweets are negative, positive or neutral
            # Creating Tweet object and adding it to objects list
            chart={"Negative":0, "Positive":0, "Neutral":0}
            for i in range(0,df.shape[0]):
                if(df['Analysis'][i] == 'Negative'):
                    chart['Negative'] +=1
 
                    TweetObject = Tweet(polarity="Negative", link=df["Links"][i], tweet= df["Tweets"][i])
                    objects.append(TweetObject)
    
                elif(df['Analysis'][i] == 'Positive'):
                    chart['Positive'] +=1
                    
                    TweetObject = Tweet(polarity="Positive", link=df["Links"][i], tweet= df["Tweets"][i])
                    objects.append(TweetObject)
    
                elif(df['Analysis'][i] == 'Neutral'):
                    chart['Neutral'] +=1
                    
                    TweetObject = Tweet(polarity="Neutral", link=df["Links"][i], tweet= df["Tweets"][i])
                    objects.append(TweetObject)
            
            sumOfTweets = chart["Negative"] + chart["Positive"] + chart["Neutral"]
            
            # Percentage of each result
            Negative_Percent = str(int((chart["Negative"] /  sumOfTweets) * 100)) + "%"
            Positive_Percent = str(int((chart["Positive"] /  sumOfTweets) * 100)) + "%"
            Neutral_Percent = str(int((chart["Neutral"] /  sumOfTweets) * 100)) + "%"

            return render(request, 
                    "main/result.html", 
                    {"analysis":chart, "negative":Negative_Percent, 
                    "posi":Positive_Percent, "neu":Neutral_Percent, "Text":text, "Tweets":objects})

        except Exception as e:
            print(e)

    return render(request, 
                  "main/home.html", 
                  {})

# Tweet class for storing tweet information         
class Tweet:
     def __init__(self, polarity, link, tweet):
        self.tweet = tweet
        self.link = link
        self.polarity = polarity

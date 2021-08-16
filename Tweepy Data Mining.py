import tweepy 
from textblob import TextBlob 
import pandas as pd
import numpy as np
import urllib.request
import re
import matplotlib.pyplot as plt

consumer_key = "aCl9MzDUdij6MQC4wE6VmG4x3"
consumer_secret = "T7l1vWsRhSNgwj0FYNIEBsGYoqfCOAH0ZGFlhK1bL57LHAFeyQ"
access_token = "1422123417533403137-KhXMWgcGgK1KQ3CJShSGgKrS2wGUgF"
access_token_secret = "t3diDW8IqKe7PSjR9K0K9HQXqZ8r1AmqwL5ysYqu7W7kp"


auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit = True)

product = input()

cursor = api.search(product, count=5000, lang="en")

Tweets = set()
for t in cursor:
    Tweets.add(t.text)


df = pd.DataFrame(data=[tweet.text for tweet in cursor], columns=['Tweets'])

if df.empty:
    print("no")

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

#Cleaned text
df['Tweets'] = df['Tweets'].apply(cleanTxt)


#Uses TextBlob to return how subjective text is
def getSubjectivity(text):
    return TextBlob(text).sentiment.subjectivity

#How positive or negative text is
def getPolarity(text):
    return TextBlob(text).sentiment.polarity


#Computes the positive, negative and neutral analysis.
def getAnalysis(score):
    if score < 0:
        return 'Negative'
    
    elif score == 0:
        return "Neutral"

    else:
        return 'Positive'

df['Subjectivity'] = df['Tweets'].apply(getSubjectivity)
df['Polarity'] = df['Tweets'].apply(getPolarity)

df['Analysis'] = df['Polarity'].apply(getAnalysis)



j=1
chart = {"Negative":0, "Positive":0, "Neutral":0}
for i in range(0, df.shape[0]):
    if(df['Analysis'][i] == 'Negative'):
        chart['Negative'] +=1
    
    elif(df['Analysis'][i] == 'Positive'):
        chart['Positive'] +=1
    
    elif(df['Analysis'][i] == 'Neutral'):
        chart['Neutral'] +=1
    

print(df)
print(chart["Negative"])
print(chart["Positive"])
print(chart["Neutral"])

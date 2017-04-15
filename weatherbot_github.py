# Program: WeatherBot
# Developer: Vishnu Unnikrishnan
# Date: 2017-04-12
# Description: A twitterbot that tweets you the weather when asked
#              by a user. The aim is to learn about building
#              twitter bots.
import tweepy
import requests
import json
import re

global api
global open_weather_key

#This is a tweet listener to find when the bot has been mentioned.
class MyStreamListener(tweepy.StreamListener):

	def on_data(self, data):
		postTweet(data)
		return True

	def on_error(self, status_code):
		if status_code == 420:
			#returning False in on_data disconnects the stream
			return False

def postTweet(data):
	global api

	tweet_data = json.loads(data)
	tweet_id = tweet_data["id"]
	tweeter = tweet_data["user"]["screen_name"]
	tweet_origin = tweet_data["user"]["lang"]
	tweet_text = tweet_data["text"]
	tweet_text_list = tweet_text.split()
	
	for e in tweet_text_list:
		if re.match("^\D{3,},\D{2}$", e, flags=0):
			weather = getWeather(e, tweet_origin)
			api.update_status("@"+tweeter+" "+weather, tweet_id)
			break

def twitterLogin(consumer_key,consumer_secret,access_key,access_secret):
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_key, access_secret)
	api = tweepy.API(auth)
	return api

def getWeather(data, language):
	degree_sign= u'\N{DEGREE SIGN}'

	global open_weather_key
	r = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+data+"&appid="+open_weather_key)
	weather_data = r.json()
	weather_desc = weather_data["weather"][0]["main"]
	temp = weather_data["main"]["temp"]
	if(language == "en_us"):
		# Use Farenheit not Celcius
		temp_int = long(temp)*1.8 - 459.00
		temp_str = str(temp_int)+ degree_sign+"F"
	else:
		# Use Rational measurement
		temp_int = long(temp)-273.00
		temp_str = str(temp_int)+ degree_sign+"C"

	weather = "It is " +weather_desc + " & " + temp_str + " in " + data[:data.index(",")]
	return weather

def main():
	consumer_key = ""
	consumer_secret = ""
	access_token_key = ""
	access_token_secret = ""
	global open_weather_key
	global api
	open_weather_key = ""
	#login to twitter
	api = twitterLogin(consumer_key,consumer_secret,access_token_key,access_token_secret)

	myStreamListener = MyStreamListener()
	myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
	myStream.filter(track=['@AskWeatherBot'],async = True)

	command = raw_input()
	if command == "quit":
		myStream.disconnect()

if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

#This is a demo using Wio Link by Kevin Lee
#pip install requests
#easy_install pytz
import os
import json
import urllib
import time
import requests              # 

from Nettime import TimeUpdate

from threading import Timer

#wio_link_server = "wss://cn.iot.seeed.cc/v1/node/event"
#This key is used for weather and ranger sensor and recoder
wio_link_key = "access_token=xxxxx"  

wio_link_key2 = "access_token=xxxxx"

YellowLed = "555500"
BlueLed   = "000055"
RainLed   = "002341"
WindLed   = "551200"
RedLed    = "330000"
Wio_link_ClearLed_Url = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/clear/50/000000?" + wio_link_key
Weather_Clear_Url     = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/segment/0/" + YellowLed*12 + "?" +  wio_link_key
Weather_Cloud_Url     = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/segment/12/" + BlueLed*12 + "?" +  wio_link_key
Weather_Rain_Url     = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/segment/24/" + RainLed*12 + "?" +  wio_link_key
Weather_Wind_Url     = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/segment/36/" + WindLed*12 + "?" +  wio_link_key

# Wio_link_temperature = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/clear/30/" + RedLed + "?" + wio_link_key2

Wio_link_test = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/clear/25/005500?access_token=7833b1f6ce1e66595aa63d7655c779a2"

Wio_link_recoder = "https://cn.iot.seeed.cc/v1/node/GroveRecorderD1/play_once?" + wio_link_key
Wio_link_ranger  = "https://cn.iot.seeed.cc/v1/node/GroveUltraRangerD2/range_in_cm?" + wio_link_key
weather_desc = "Unknow"                  # General description of the weather
Last_weather_desc = "UnKnow"
Last_temp    = None
tempOut      = "Unknow"                  # Temperature in C
pressure     = "Unknow"                  # Pressure in hPa
humidity     = "Unknow"                  # Humidity %
wind_speed   = "Unknow"   
Task1        = None
Task2        = None


TimeInterval1 = 10  #  update weather data time interval  unit second
TimeInterval2 = 10   #  update time data interval          unit second
TimeOutIndex = 0  # To Count how many times post url error

# weather information
city="shenzhen"
appID = "a9764b47b351cacfc45a5a352af45441"
url = "http://api.openweathermap.org/data/2.5/weather?q=" + city + "&APPID=" + appID


#def updateLocalWeather():
#    global weather_desc,tempOut,pressure,humidity,wind_speed,weather_Status
#    try:

#    except (IOError,TypeError) as e:



def updateWeather():
    global weather_desc,tempOut,pressure,humidity,wind_speed,weather_Status,Last_weather_desc,Last_temp
    try:
    	Last_temp = tempOut
    	
        jsonurl = urllib.urlopen(url)                      # open the url
        text = json.loads(jsonurl.read())
    
     #Get the Weather info form internet
        Last_weather_desc = weather_desc
        weather_desc=text["weather"][0]["main"]            # General description of the weather
        tempOut = float(text["main"]["temp"])-273.15       # Temperature in C
        pressure=text["main"]["pressure"]                  # Pressure in hPa
        humidity=text["main"]["humidity"]                  # Humidity %
        wind_speed=text["wind"]["speed"]                   # Wind speed mps

        print weather_desc,tempOut,pressure,humidity,wind_speed
        if Last_temp != tempOut:
            temp = str(int(tempOut) - 5)
            Wio_link_test = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/clear/30/000000?access_token=7833b1f6ce1e66595aa63d7655c779a2"
            UrlPost(Wio_link_test)  # clear all the rgb led first
            print temp
            Wio_link_test = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/clear/" + temp + " /551100?access_token=7833b1f6ce1e66595aa63d7655c779a2"
            UrlPost(Wio_link_test)
    # update the temperature rgb led
    #Wio_link_temperature = "https://cn.iot.seeed.cc/v1/node/GroveLedWs2812D0/clear/" + temp + "/" + RedLed + wio_link_key2
    #UrlPost(Wio_link_temperature)
    except IOError:
        print("Urlib IO Error")
    # Check if need to update the LED status, if the weather changes, change the LED status

    if Last_weather_desc != weather_desc:
        #Clear
        if weather_desc == "Clear":
            WeatherUrlPost(Weather_Clear_Url)
        #cloud
        elif weather_desc == "Clouds":
            WeatherUrlPost(Weather_Cloud_Url)
        elif weather_desc == "Haze":
            WeatherUrlPost(Weather_Cloud_Url)
        elif weather_desc == "Mist":
            WeatherUrlPost(Weather_Cloud_Url)
        #Rain
        elif weather_desc == "Rain":
            WeatherUrlPost(Weather_Rain_Url)
        elif weather_desc == "Drizzle":
            WeatherUrlPost(Weather_Rain_Url)
        #Wind
        else:
            WeatherUrlPost(Weather_Wind_Url)

    updateTask1()
    
def updateTime():
    # print(TimeUpdate())

    updateTask2()
    

# Create Tasks
def updateTask1():
    global Task1
    Task1 = Timer(TimeInterval1,updateWeather)
    Task1.start()
def updateTask2():
    global Task2
    Task2 = Timer(TimeInterval2,updateTime)
    Task2.start()
def UrlPost(url):
    result = requests.post(url)
    while result.status_code != 200:   # if response error try again 10 times
        global TimeOutIndex
        TimeOutIndex = TimeOutIndex + 1
        time.sleep(1)
        result = requests.post(url)
         # print the error info
        #print("The Weather Url Try times is " + url + ": "+TimeOutIndex)
        if TimeOutIndex == 10:
            TimeOutIndex = 0
            print("Still can't access the Url, please check the Wio Link Connection")
            break

def UrlGet(url):
    result = requests.get(url)
    while result.status_code != 200:   # if response error try again 10 times
        global TimeOutIndex
        TimeOutIndex = TimeOutIndex + 1
        time.sleep(1)
        result = requests.get(url)
         # print the error info
        print("The Weather Url Try times is " + url + ": "+str(TimeOutIndex))
        if TimeOutIndex == 10:
            TimeOutIndex = 0
            print("Still can't access the Url, please check the Wio Link Connection")
            return result
            break
    return result

def WeatherUrlPost(weather_url):
    UrlPost(Wio_link_ClearLed_Url)
    time.sleep(1)
    UrlPost(weather_url)
if __name__ == "__main__":
    updateWeather()
    #updateTime()
   
    #WeatherUrlPost(Weather_Wind_Url)
    #time.sleep(2)

    #WeatherUrlPost(Weather_Rain_Url)
    #time.sleep(2)

    #WeatherUrlPost(Weather_Cloud_Url)
    #time.sleep(2)

    #WeatherUrlPost(Weather_Clear_Url)
    #time.sleep(2)


    #updateLocalWeather()
    while True:
        try:
            # print(TimeUpdate())
            #UrlPost(Wio_link_recoder)
            #result = requests.get(Wio_link_ranger)
            #data_json = result.json()
            result = UrlGet(Wio_link_ranger)
            if result.status_code == 200:
                data_json = result.json()
                #ranger = data_json.get('range_cm')
                print data_json
                if data_json.get('range_cm') < 50:
                    time.sleep(2)
                    result = UrlGet(Wio_link_ranger)
                    if result.status_code == 200:
                        data_json = result.json()
                        if data_json.get('range_cm') < 50:
                            UrlPost(Wio_link_recoder)
                            print("OPen the recoder")
                        print data_json
						
            time.sleep(5)
        except KeyboardInterrupt:
            Task1.cancel()
            Task2.cancel()
            exit()
       

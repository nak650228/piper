import requests
import datetime
import sys


def getAPIData(endpoint,headers,params):
    endpoint = endpoint
    headers = headers
    params=params

    result = requests.get(endpoint, headers=headers, params=params)

    return result.json()

def printWeather(place, api_key):

    data = getAPIData(
        "https://api.openweathermap.org/data/2.5/weather",
        {},
        {
        "appid":api_key,
        "q":place,
        "lang":"ja"
        }
    )

    lon= data["coord"]["lon"] #経度
    lat= data["coord"]["lat"] #緯度

    data = getAPIData(
        "https://api.openweathermap.org/data/2.5/onecall",
        {},
        {
        "appid":api_key,
        "lon":lon,
        "lat":lat,
        "units":"metric",
        "lang":"ja",
        "exculde":"current,minutely,hourly,alerts"
        }
    )
    count = 0

    for day in data["daily"]:
        datedata=datetime.date.fromtimestamp(day["dt"])
        print(datedata.strftime("%m/%d"),":",
              day["weather"][0]["description"],
              day["temp"]["min"],"℃/",day["temp"]["max"],"%<br>") 
        count+=1
        if count >= 2 :
            break

if __name__ == '__main__':
    printWeather("Tama,JP","ReplaceYourOwnAPIKeyofOpenWeather")

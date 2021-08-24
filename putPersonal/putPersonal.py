#!/usr/bin/env python
#coding=utf-8

import os
import getTempInfo 
import getWeatherInfo
import getTrainInfo
import ast

# AWS Rekognitionの結果ファイルを読みだす 
ID_FILE = "/tmp/IDFile"


if os.path.isfile(ID_FILE) :
    fp = open(ID_FILE,'r')
    result_data = fp.read()
    fp.close()

    dic=ast.literal_eval(result_data)

    user_name =  dic['Name']
    train_list = dic['TrainInfo']
    work_place = dic['WorkPlace']

    print("Welcome <p2>",user_name,"</p2><br>")

    getTempInfo.printTemp()

    #一時的にアカウント凍結のためコメントアウト
    print("<p2>勤務地の天気(",work_place,")</p2><br>")
    getWeatherInfo.printWeather(work_place,"32b60394f9a24bcca05704fadebae134")

    getTrainInfo.printTrainInfo(train_list)
else:
    getTempInfo.printTemp()
    #一時的にアカウント凍結のためコメントアウト

    print("<p2>現在地の天気</p2><br>")
    getWeatherInfo.printWeather("Tama,JP","32b60394f9a24bcca05704fadebae134")

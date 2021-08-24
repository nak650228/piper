#!/usr/bin/env python3
#coding=utf-8

import os
import subprocess

def printTemp():
    HUMIDITY_SENSOR="./image/humidity.png"
    THERMOMETER="./image/thermometer.png"

    # 気温と湿度の表示
#    print("<p><img src=\"/home/pi/env/putPersonal/image/thermometer.png\", border=\"3\"></p>")
    tempdata=subprocess.run("/home/piper/dht11",stdout=subprocess.PIPE)
    out1=tempdata.stdout.decode()
    out2=out1.rstrip('\n')
    out3=out2.split(':')

    print("<p2>気温</p2>: ",out3[0],"℃ <p2>湿度:</p2> ",out3[1],"%</p2><br>")

if __name__ == '__main__':
    printTemp()

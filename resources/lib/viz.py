# -*- coding: utf-8 -*-
"""
    screensaver.embellir
    Copyright (C) 2019 nundrum

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import xbmc
import os
import json
import requests
import xbmcgui
import xbmcaddon
import xbmcvfs
from . import kodiutils
from .weatherutils import WeatherInfo
from random import randint, shuffle
from .drawutils import Drundle
from PIL import Image, ImageDraw
import time
import calendar
import controller
import operator
import random

TEMP = xbmc.translatePath("special://temp")

def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + datetime.timedelta(days=4)  # this will never fail
    return next_month - datetime.timedelta(days=next_month.day)

class EmbellirVizBase():

    def __init__(self, *args, **kwargs):
        pass

    def drawTime(self,draw):
        raise NotImplementedError

    def drawWeather(self,draw):
        raise NotImplementedError

    def log(self,msg):
        xbmc.log(str(msg), level=xbmc.LOGNOTICE)

class EmbellirVizRound(EmbellirVizBase):

    twelfth = (360/12)
    sixtieth = (360/60)
    weather = WeatherInfo()

    def __init__(self, *args, **kwargs):
        self.size = kwargs['size']
        self.x = kwargs['x']
        self.y = kwargs['y']
        self.config = kwargs['config']
        self.log(self.weather.weather)

    def drawTime(self,draw):
        #self.drawCalibrationRings(draw)
        size=self.size
        half=size * 0.5
        x=self.x
        y=self.y
        now = time.localtime()

        monthDegrees = now.tm_mon  * self.twelfth
        dayDegrees = now.tm_mday * (360 / calendar.monthrange(now.tm_year, now.tm_mon)[1])
        hourDegrees = (now.tm_hour % 12) * self.twelfth
        minuteDegrees = now.tm_min * self.sixtieth
        secondDegrees = now.tm_sec * self.sixtieth

        #radius
        rm = size * 0.99
        rd = size * 0.95
        rH = size * 0.80
        rM = size * 0.40
        rS = size * 0.30

        drm = Drundle(color=self.config['secondarycolor'], draw=draw)
        drd = Drundle(color=self.config['tertiarycolor'], draw=draw)
        drH = Drundle(color=self.config['primarycolor'], draw=draw)
        drM = Drundle(color=self.config['secondarycolor'], draw=draw)
        drS = Drundle(color=self.config['tertiarycolor'], draw=draw)


        drm.circleArc(x+half,y+half,rm,0,monthDegrees)
        drd.circleArc(x+half,y+half,rd,0,dayDegrees)
        drH.circleArc(x+half,y+half,rH,0,hourDegrees,width=30)
        drM.circleArc(x+half,y+half,rM,0,minuteDegrees,width=30)
        drS.circleArc(x+half,y+half,rS,minuteDegrees,minuteDegrees + secondDegrees,width=20)
        #drp.circleArc(0,0,rd,start,
        #        start+(dayDegrees*outlook)+1,width=10)
        #drc.circleArc(0,0,rd,dayStart+dayDegrees*(F-1)+1,
        #        dayStart+dayDegrees*(F-1)+dayDegrees-1,width=30)

    def drawCalibrationRings(self,draw):
        size=self.size
        half=size * 0.5
        calibrate = Drundle(color=(125,125,125,125), draw=draw)
        calibrate.translate(half,half)
        calibrate.circleArc(0,0,size*1.0,0,360,width=5)
        calibrate.circleArc(0,0,size*0.9,0,360,width=5)
        calibrate.circleArc(0,0,size*0.8,0,360,width=5)
        calibrate.circleArc(0,0,size*0.7,0,360,width=5)
        calibrate.circleArc(0,0,size*0.6,0,360,width=5)
        calibrate.circleArc(0,0,size*0.5,0,360,width=10)
        calibrate.circleArc(0,0,size*0.4,0,360,width=5)
        calibrate.circleArc(0,0,size*0.3,0,360,width=5)
        calibrate.circleArc(0,0,size*0.2,0,360,width=5)
        calibrate.circleArc(0,0,size*0.1,0,360,width=5)

    def drawWeather(self,draw):
        now = time.localtime()
        size=self.size
        half=size * 0.5
        x=self.x
        y=self.y
        targetRing = 0.6
        ring = size * targetRing
        rrad = ring * 0.5
        dayDegrees = (360 / calendar.monthrange(now.tm_year, now.tm_mon)[1])
        dayStart = dayDegrees * now.tm_mday

        drt = Drundle(color=self.config['primarycolor'], draw=draw) #temp
        drp = Drundle(color=self.config['secondarycolor'], draw=draw) #precip
        forecastSizeMax=drt.pointDistance(drt.calcCircle(0,rrad),
                drt.calcCircle(30,rrad))
        #self.log(forecastSizeMax)
        forecastSize=min(forecastSizeMax,
                (size*(targetRing+0.1) - size*(targetRing-0.1)) * 0.5)

        #hourly forecast circles
        drt.translate(half, half)
        drp.translate(half, half)
        hourlyForecast=self.weather.weather['hourly']
        #self.log(hourlyForecast)
        for F in hourlyForecast:
            temp=hourlyForecast[F]['temperature']
            precip=hourlyForecast[F]['precipitation']
            hour = now.tm_hour % 12
            hourDegree = hour * 30 + (F-1) * 30
            #self.log((F,temp,hour))
            xpos,ypos=drt.calcCircle(hourDegree,rrad)
            drt.translate(xpos,ypos)
            drp.translate(xpos,ypos)
            mid = hourDegree - 360
            tempArc = (360/100) * temp * 0.5
            precipArc = (360/100) * precip * 0.5
            drt.circleChord(0,0,forecastSize,0-tempArc+mid,tempArc+mid)
            drp.circleArc(0,0,forecastSize,0-precipArc+mid,precipArc+mid,width=5)
            drt.detranslate()
            drp.detranslate()

        #daily forecast circles
        drc = Drundle(color=(255,0,0,0), draw=draw) #clear
        drc.translate(half, half)
        drD = Drundle(color=self.config['tertiarycolor'], draw=draw) #day
        drD.translate(half, half)

        dailyForecast=self.weather.weather['daily']
        #self.log(dailyForecast)
        for F in dailyForecast:
            high=dailyForecast[F]['high']
            low=dailyForecast[F]['low']
            outlook=dailyForecast[F]['outlook']
            if high==None or low==None or outlook==None:
                continue
            self.log((low,high,outlook))
            low = min(low,120)
            low = max(low,0)
            high = min(high,120)
            high = max(high,0)
            high=high/120.0
            low=low/120.0
            outlook=outlook/100.0
            rd = size * 0.95
            #xpos,ypos=drt.calcCircle(hourDegree,rrad)
            start=dayStart+dayDegrees*(F-1)
            drD.circleArc(0,0,rd,start,
                    start+dayDegrees,width=40)
            drc.circleArc(0,0,rd,start+0.5,
                    start+dayDegrees-0.5,width=30)
            #drc.circleArc(0,0,rd,dayStart+dayDegrees*(F-1)+1,
            #        dayStart+dayDegrees*(F-1)+dayDegrees-1,width=30)
            drt.circleArc(0,0,rd,start+1+(dayDegrees*low),
                    start+1+(dayDegrees*high),width=30)
            drp.circleArc(0,0,rd,start,
                    start+(dayDegrees*outlook)+1,width=10)
        drt.detranslate()
        drp.detranslate()

class EmbellirVizSquare(EmbellirVizBase):

    def __init__(self, *args, **kwargs):
        self.size = kwargs['size']
        self.x = kwargs['x']
        self.y = kwargs['y']
        self.config = kwargs['config']


        self.paddingSize=self.size / 70
        self.boxSize=(self.size - (self.paddingSize * 3)) / 4

        #assign shorter variable names just to make this more readable
        p=self.paddingSize
        b=self.boxSize
        self.hourPositions=[
                (p*2+b*2, p*0+b*0),
                (p*3+b*3, p*0+b*0),
                (p*3+b*3, p*1+b*1),
                (p*3+b*3, p*2+b*2),
                (p*3+b*3, p*3+b*3),
                (p*2+b*2, p*3+b*3),
                (p*1+b*1, p*3+b*3),
                (p*0+b*0, p*3+b*3),
                (p*0+b*0, p*2+b*2),
                (p*0+b*0, p*1+b*1),
                (p*0+b*0, p*0+b*0),
                (p*1+b*1, p*0+b*0),
                ]
        self.log(self.hourPositions)
        self.minuteSize=self.boxSize / 5
        self.hourSize=self.minuteSize * 3 - self.paddingSize * 2
        self.hourOffset=self.minuteSize + self.paddingSize
        msz=self.minuteSize
        self.minutePositions=[
                [(msz*0,msz*0), (msz*0,msz*1), (msz*0,msz*2), (msz*0,msz*3), (msz*0,msz*4)],
                [(msz*1,msz*0), (msz*1,msz*4)],
                [(msz*2,msz*0), (msz*2,msz*4)],
                [(msz*3,msz*0), (msz*3,msz*4)],
                [(msz*4,msz*0), (msz*4,msz*1), (msz*4,msz*2), (msz*4,msz*3), (msz*4,msz*4)] ]
        self.secondsGrid = [(x,y) for x in range(8) for y in range(8)]
        shuffle(self.secondsGrid)
        self.secondSize=(self.boxSize*2 + self.paddingSize) / 8
        self.secondsOffset=self.boxSize + self.paddingSize
        #self.log("init round")
        #self.log(self.size)
        #self.log(self.x)
        #self.log(self.y)
        #self.log(self.config)
        #self.log(self.paddingSize)
        #self.log(self.boxSize)

    def drawTime(self,draw):
        size=self.size
        x=self.x
        y=self.y
        p=self.paddingSize
        now = time.localtime()
        hours = now.tm_hour % 12
        minuteList = range(now.tm_min)
        #self.log(now.tm_sec)

        drm = Drundle(color=self.config['primarycolor'], draw=draw)
        drd = Drundle(color=self.config['primarycolor'], draw=draw)
        drH = Drundle(color=self.config['primarycolor'], draw=draw)
        drM = Drundle(color=self.config['secondarycolor'], draw=draw)
        drS = Drundle(color=self.config['tertiarycolor'], draw=draw)

        for h in range(12):
            if h < hours:
                x,y =self.hourPositions[h]
                drH.square(x+self.hourOffset,y+self.hourOffset, self.hourSize, centered=False)
            minuteCount = len(minuteList[:5])
            minuteList = minuteList[5:]
            for m in range(1,minuteCount+1):
                minutePositionList = self.minutePositions[m-1]
                for position in minutePositionList:
                    hx,hy=self.hourPositions[h]
                    x,y=position
                    drM.square(x+hx,y+hy,self.minuteSize,centered=False)

        for s in range(now.tm_sec):
            ss = self.secondSize
            o = self.secondsOffset
            drS.square(self.secondsGrid[s][0]*ss+o,self.secondsGrid[s][1]*ss+o,
                    ss,centered=False)

    def drawWeather(self,draw):
        pass


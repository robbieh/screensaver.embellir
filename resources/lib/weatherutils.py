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
import xbmcgui
import os
import math
import time
import re

TEMP = xbmc.translatePath("special://temp")
WEATHER_WINDOW=xbmcgui.Window(12600)

def cleanInt(s):
    """return int after stripping all non-numerics from a string"""
    try:
        return int(re.sub("[^0-9]","",s))
    except ValueError:
        xbmc.log("could not parse " + s)
        return None

def mapOutlook(s):
    """Guess at precipitation percent based on condition name"""
    s=s.lower()
    if re.match("isolated",s):
        return 15
    if re.match("scattered",s):
        return 25
    elif re.match("showers",s):
        return 75
    elif re.match("light.*showers",s):
        return 25
    elif re.match("flurries",s):
        return 15
    elif re.match("thunderstorms",s):
        return 75
    elif re.match("severe thunderstorms",s):
        return 75
    elif re.match("heavy",s):
        return 75
    return 0

def getHourlyWeatherInfo(h):
    return {
        'temperature': cleanInt(WEATHER_WINDOW.getProperty('Hourly.%i.Temperature'  % h)),
        'precipitation': cleanInt(WEATHER_WINDOW.getProperty('Hourly.%i.Precipitation'  % h))
        }

def getDailyWeatherInfo(d):
    return {
            'high': cleanInt(WEATHER_WINDOW.getProperty('Day%i.HighTemp' %d)),
            'low': cleanInt(WEATHER_WINDOW.getProperty('Day%i.LowTemp' %d)),
            'outlook': mapOutlook(WEATHER_WINDOW.getProperty('Day%i.Outlook' %d)),
            }

def getWeatherInfo():
    return {
            'temperature': WEATHER_WINDOW.getProperty('Current.Temperature'),
            'condition': WEATHER_WINDOW.getProperty('Current.Condition'),
            'condition': WEATHER_WINDOW.getProperty('Current.Temperature'),
            'hourly': {1: getHourlyWeatherInfo(1),
                2: getHourlyWeatherInfo(2),
                3: getHourlyWeatherInfo(3),
                4: getHourlyWeatherInfo(4),
                5: getHourlyWeatherInfo(5),
                6: getHourlyWeatherInfo(6),
                7: getHourlyWeatherInfo(7),
                8: getHourlyWeatherInfo(8),
                9: getHourlyWeatherInfo(9),
                10: getHourlyWeatherInfo(10),
                },
            'daily': {1: getDailyWeatherInfo(1),
                2: getDailyWeatherInfo(2),
                3: getDailyWeatherInfo(3),
                4: getDailyWeatherInfo(4),
                5: getDailyWeatherInfo(5),
                6: getDailyWeatherInfo(6),
                7: getDailyWeatherInfo(7),
                8: getDailyWeatherInfo(8),
                9: getDailyWeatherInfo(9),
                10: getDailyWeatherInfo(10),
                }
            }

class WeatherInfo:

    weather = getWeatherInfo()

    def update():
        self.weather = getWeatherInfo()


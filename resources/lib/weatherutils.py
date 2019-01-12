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
    return int(re.sub("[^0-9]","",s))

def getHourlyWeatherInfo(h):
    return {
        'temperature': cleanInt(WEATHER_WINDOW.getProperty('Hourly.%i.Temperature'  % h)),
        'precipitation': cleanInt(WEATHER_WINDOW.getProperty('Hourly.%i.Precipitation'  % h))
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
                }
            }

class WeatherInfo:

    weather = getWeatherInfo()

    def update():
        self.weather = getWeatherInfo()


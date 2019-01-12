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
import math
import json
import requests
import xbmcgui
import xbmcaddon
import xbmcvfs
from . import kodiutils
from random import randint, shuffle
from .screensaverutils import ScreenSaverUtils
from PIL import Image, ImageDraw
import time
import controller

TEMP = xbmc.translatePath("special://temp")

class Drundle():

    def __init__(self, *args, **kwargs):
        self.ref_x = 0
        self.ref_y = 0
        self.translation_stack = []
        self.color = kwargs['color']
        self.draw = kwargs['draw']

    def set_color(self,color):
        self.color = color

    def stack(self):
        return [self.translation_stack, self.ref_x, self.ref_y]

    def translate(self,x,y):
        self.translation_stack.append((self.ref_x,self.ref_y))
        self.ref_x = self.ref_x + x
        self.ref_y = self.ref_y + y

    def detranslate(self):
        self.ref_x, self.ref_y = self.translation_stack.pop()

    def square(self,x,y,size,centered=True):
        s=self
        if centered:
            half=size*0.5
            self.draw.rectangle([s.ref_x+x-half,s.ref_y+y-half, s.ref_x+x+half,s.ref_y+y+half], fill=self.color)
        else:
            self.draw.rectangle([s.ref_x+x,s.ref_y+y, s.ref_x+x+size,s.ref_y+y+size],fill=self.color)

    #very helpful:
    #https://stackoverflow.com/questions/7070912/creating-an-arc-with-a-given-thickness-using-pils-imagedraw
    def arc(self, bbox, start, end, fill, width=1, segments=100):
        """
        Hack that looks similar to PIL's draw.arc(), but can specify a line width.
        """
        segments=int(segments)
        # radians
        #xbmc.log(str(start), level=xbmc.LOGNOTICE)
        start *= math.pi * 1/180
        end *= math.pi * 1/180

        # angle step
        if segments > 0:
            da = (end - start) / segments
        else:
            return

        # shift end points with half a segment angle
        start -= da / 2
        end -= da / 2

        # ellips radii
        rx = (bbox[2] - bbox[0]) / 2
        ry = (bbox[3] - bbox[1]) / 2

        # box centre
        cx = bbox[0] + rx
        cy = bbox[1] + ry

        # segment length
        l = (rx+ry) * da / 2.0

        for i in range(segments):

          # angle centre
          a = start + (i+0.5) * da

          # x,y centre
          x = cx + math.cos(a) * rx
          y = cy + math.sin(a) * ry

          # derivatives
          dx = -math.sin(a) * rx / (rx+ry)
          dy = math.cos(a) * ry / (rx+ry)

          self.draw.line([(x-dx*l,y-dy*l), (x+dx*l, y+dy*l)], fill=fill, width=width)

    def circleArc(self,x,y,size,start,end,width=10,centered=True):
        start -= 90
        end -= 90
        s=self
        if centered:
            half=size*0.5
            self.arc([s.ref_x+x-half,s.ref_y+y-half, s.ref_x+x+half,s.ref_y+y+half], start, end, self.color, width, abs(start-end))
        else:
            self.arc([s.ref_x+x,s.ref_y+y,
                s.ref_x+x+s,s.ref_y+y+s], start, end, width, fill=self.color)

    def circleChord(self,x,y,size,start,end,width=10,centered=True):
        start -= 90
        end -= 90
        s=self
        if centered:
            half=size*0.5
            self.draw.chord([s.ref_x+x-half,s.ref_y+y-half, s.ref_x+x+half,s.ref_y+y+half], start, end, fill=self.color)
        else:
            self.draw.chord([s.ref_x+x,s.ref_y+y,
                s.ref_x+x+s,s.ref_y+y+s], start, end, fill=self.color)


    def calcCircle(self,degrees,radius):
        """return coordinate on cirle of size 'radius',
        corrected such that degree 0 is up"""
        angle = math.radians(degrees-90)
        return(math.cos(angle) * radius,
                math.sin(angle) * radius)

    def pointDistance(self,p1,p2):
        x1,y1=p1
        x2,y2=p2
        return math.hypot(abs(x1 - x2), abs(y1 - y2))

    def log(self,msg):
                xbmc.log(str(msg), level=xbmc.LOGNOTICE)



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
from random import randint, shuffle
from .screensaverutils import ScreenSaverUtils
from PIL import Image, ImageDraw
import viz
import time
import controller

PATH = xbmcaddon.Addon().getAddonInfo("path")
IMAGE_FILE = os.path.join(PATH, "resources", "images", "chromecast.json")
TEMP = xbmc.translatePath("special://temp")

class Embellir(xbmcgui.WindowXMLDialog):

    class ExitMonitor(xbmc.Monitor):

        def __init__(self, exit_callback):
            self.exit_callback = exit_callback

        def onScreensaverDeactivated(self):
            try:
                self.exit_callback()
            except AttributeError:
                xbmc.log(
                    msg="exit_callback method not yet available",
                    level=xbmc.LOGWARNING
                )


    def __init__(self, *args, **kwargs):
        self.exit_monitor = None
        self.images = []
        self.set_property()
        self.utils = ScreenSaverUtils()

    def log(self,msg):
        xbmc.log(str(msg), level=xbmc.LOGNOTICE)

    def setClockImage(self, config):
        filename=os.path.join(TEMP, "tmpkodi-" + str(int(time.time())) + ".png")
        size=config['size']
        im = Image.new("RGBA",(size,size), (0,0,0,0))
        draw = ImageDraw.Draw(im)
        self.viz.drawTime(draw)
        self.viz.drawWeather(draw)
        im.save(filename)
        del draw
        del im
        self.logo.setImage(filename, useCache=False)
        xbmc.sleep(200)
        os.remove(filename)

    def drawVisualizations(self, config):
        #if clock...
        self.setClockImage(config)

    def onInit(self):
        self._isactive = True
        # Register screensaver deactivate callback function
        self.exit_monitor = self.ExitMonitor(self.exit)
        # Init controls
        self.backgroud = self.getControl(32500)
        self.metadata_line2 = self.getControl(32503)
        self.metadata_line3 = self.getControl(32504)

        self.logo = self.getControl(32505)

        config={'size': 900}
        config.update({
            'primarycolor': (
                kodiutils.get_setting_as_int("primary-red"),
                kodiutils.get_setting_as_int("primary-green"),
                kodiutils.get_setting_as_int("primary-blue"),
                kodiutils.get_setting_as_int("primary-alpha")),
            'secondarycolor': (
                kodiutils.get_setting_as_int("secondary-red"),
                kodiutils.get_setting_as_int("secondary-green"),
                kodiutils.get_setting_as_int("secondary-blue"),
                kodiutils.get_setting_as_int("secondary-alpha")),
            'tertiarycolor': (
                kodiutils.get_setting_as_int("tertiary-red"),
                kodiutils.get_setting_as_int("tertiary-green"),
                kodiutils.get_setting_as_int("tertiary-blue"),
                kodiutils.get_setting_as_int("tertiary-alpha"))
            })

        # Grab images
        self.get_images()

        # Instantiate desired viz class
        # if setting is square...
        mode=kodiutils.get_setting_as_int("clock-mode")
        if mode == 0:
            self.viz = viz.EmbellirVizSquare(size=900,x=0,y=0,config=config)
        elif mode == 1:
            self.viz = viz.EmbellirVizRound(size=900,x=0,y=0,config=config)
        if kodiutils.get_setting_as_int("clock-position") == 1:
            self.logo.setWidth(400)
            self.logo.setHeight(400)
            self.logo.setPosition(1920-500,1080-500)

        #start timer controller for clock image redraw
        self.cont = controller.Controller(self.log, self.drawVisualizations, config, 60)
        self.cont.start()

        # Start Image display loop
        if self.images and self.exit_monitor:
            while self._isactive and not self.exit_monitor.abortRequested():
                rand_index = randint(0, len(self.images) - 1)

                # if it is a google image....
                if "private" not in self.images[rand_index]:
                    if requests.head(url=self.images[rand_index]["url"]).status_code != 200:
                        continue

                    # photo metadata
                    if "location" in self.images[rand_index].keys() and "photographer" in self.images[rand_index].keys():
                        self.metadata_line2.setLabel(self.images[rand_index]["location"])
                        self.metadata_line3.setLabel("%s %s" % (kodiutils.get_string(32001),
                                                                self.utils.remove_unknown_author(self.images[rand_index]["photographer"])))
                    elif "location" in self.images[rand_index].keys() and "photographer" not in self.images[rand_index].keys():
                        self.metadata_line2.setLabel(self.images[rand_index]["location"])
                        self.metadata_line3.setLabel("")
                    elif "location" not in self.images[rand_index].keys() and "photographer" in self.images[rand_index].keys():
                        self.metadata_line2.setLabel("%s %s" % (kodiutils.get_string(32001),
                                                                self.utils.remove_unknown_author(self.images[rand_index]["photographer"])))
                        self.metadata_line3.setLabel("")
                    else:
                        self.metadata_line2.setLabel("")
                        self.metadata_line3.setLabel("")
                else:
                    # Logic for user owned photos - custom information
                    if "line1" in self.images[rand_index]:
                        self.metadata_line2.setLabel(self.images[rand_index]["line1"])
                    else:
                        self.metadata_line2.setLabel("")
                    if "line2" in self.images[rand_index]:
                        self.metadata_line3.setLabel(self.images[rand_index]["line2"])
                    else:
                        self.metadata_line2.setLabel("")
                # Insert photo
                self.backgroud.setImage(self.images[rand_index]["url"])
                # Pop image and wait
                del self.images[rand_index]
                # Sleep for a given ammount of time if the window is active abort is not requested
                # note: abort requested is only called after kodi kills the entrypoint and we need to return
                # as soon as possible
                loop_count = (kodiutils.get_setting_as_int("wait-time-before-changing-image") * 1000) / 200
                for _ in range(0, loop_count):
                    if self._isactive and not self.exit_monitor.abortRequested():
                        xbmc.sleep(200)
                # Check if images dict is empty, if so read the file again
                if not self.images:
                    self.get_images()

    def get_images(self, override=False):
        # Read google images from json file
        self.images = []
        if kodiutils.get_setting_as_int("screensaver-mode") == 0 or kodiutils.get_setting_as_int("screensaver-mode") == 2 or override:
            with open(IMAGE_FILE, "r") as f:
                images = f.read()
            self.images = json.loads(images)
        # Check if we have images to append
        if kodiutils.get_setting_as_int("screensaver-mode") == 1 or kodiutils.get_setting_as_int("screensaver-mode") == 2 and not override:
            if kodiutils.get_setting("my-pictures-folder") and xbmcvfs.exists(xbmc.translatePath(kodiutils.get_setting("my-pictures-folder"))):
                for image in self.utils.get_own_pictures(kodiutils.get_setting("my-pictures-folder")):
                    self.images.append(image)
            else:
                return self.get_images(override=True)
        shuffle(self.images)
        return

    def set_property(self):
        # Kodi does not yet allow scripts to ship font definitions
        skin = xbmc.getSkinDir()
        if "estuary" in skin:
            self.setProperty("clockfont", "fontclock")
        elif "zephyr" in skin:
            self.setProperty("clockfont", "fontzephyr")
        elif "eminence" in skin:
            self.setProperty("clockfont", "fonteminence")
        else:
            self.setProperty("clockfont", "fontmainmenu")
        # Set skin properties as settings
        for setting in ["hide-clock-info", "hide-kodi-logo", "hide-weather-info", "hide-pic-info", "hide-overlay", "show-blackbackground"]:
            self.setProperty(setting, kodiutils.get_setting(setting))
        # Set animations
        if kodiutils.get_setting_as_int("animation") == 1:
            self.setProperty("animation","panzoom")
        return


    def exit(self):
        self._isactive = False
        # Delete the monitor from memory so we can gracefully remove
        # the screensaver window from memory too
        if self.exit_monitor:
            del self.exit_monitor
        # Finally call close so doModal returns
        self.close()

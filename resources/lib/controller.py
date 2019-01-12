#!/usr/bin/python

import threading
import datetime

import xbmc

class Controller(threading.Thread):

    def __init__(self, log_callback, draw_callback, config, redrawInterval):
      super(Controller, self).__init__()
      self.log_callback = log_callback
      self.draw_callback = draw_callback
      self.config = config
      self.redrawInterval = redrawInterval
      self.waitCondition = threading.Condition()
      self._stop = False

    def run(self):
        self.waitCondition.acquire()
        while not self.shouldStop():
             self.now = datetime.datetime.today()
             self.draw_callback(self.config)
             #TODO
             #if (self.now.second % self.redrawInterval == 0):
             #   self.drawClock_callback(False)
             #elif (self.showSeconds):
             #   self.drawClock_callback(True)

             self.waitFor =  1000000 - self.now.microsecond
             self.waitCondition.wait(float(self.waitFor) / 1000000)
        self.waitCondition.release()


    def shouldStop(self):
        if (xbmc.abortRequested):
            return True
        return self._stop

    def stop(self):
        self.waitCondition.acquire()
        self._stop = True
        self.waitCondition.notifyAll()
        self.waitCondition.release()

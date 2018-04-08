#!/bin/python

from __future__ import print_function

import time,threading,sys,coloredlogs,logging
from Queue import Queue

import string2time

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger,level='DEBUG')

class assistantTimers(threading.Thread):
    def __init__(self,replyQueue,logLevel='DEBUG'):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.cond  = threading.Condition()
        self.timers = []
        logger.setLevel(logLevel)
        self._queue = replyQueue

    def run(self):
        logger.info("Timer thread started.")
        self.event.set()
        self.cond.acquire()
        delay = self._getDelay()
        while self.event.is_set():
            self.cond.wait(delay)
            if not self.event.is_set():
                break
            delay = self._getDelay()
        logger.info("Timer thread is shutting down.")
        if len(self.timers) is not 0:
            logger.warn("Abandoning {0} timers".format(len(self.timers)))
            for timer in self.timers:
                logger.debug(timer['name'])
        self.cond.release()

    def stopInput(self):
        self.event.clear()
        self.cond.acquire()
        self.cond.notify()
        self.cond.release()

    def _getDelay(self):
        if self.timers and len(self.timers) > 0:
            curTime = int(time.time())
            for timer in list(self.timers):
               if timer['time'] <= curTime:
                  self._queue.put({'origin': 'timer',
                                   'intent': timer['intent'],
                                   'entities': timer['entities']})
                  self.cond.acquire()
                  self.timers.remove(timer)
                  self.cond.release()
            if self.timers and len(self.timers) > 0:
               for timer in self.timers:
                  try:
                     if timer['time'] < shortest:
                        shortest = timer['time']
                  except NameError:
                     shortest = timer['time']
               try:
                  delay = (shortest - curTime) * 1.0
               except NameError:
                  delay = None
            else:
                delay = None
        else:
            delay = None
        return delay


    def addTimer(self,intent,entities):
        self.cond.acquire()
        curTime = int(time.time())
        timeVal = string2time.convert(entities['time'])
        timeVal += curTime
        if not u'task' in entities:
            entities['task'] = ''.join(entities['time'])
        entities.pop('time')
        self.timers.append({'time':timeVal,
                            'intent': intent,
                            'entities': entities})
        logger.info("Added {0} to be triggered in {1} seconds"
                     .format(self.timers[-1]['intent'],(timeVal-curTime)))
        self.cond.notify()
        self.cond.release()

    def getTimers(self):
        return sorted(self.timers, key=lambda k: k['time'])

    def removeTimer(self,timer):
        self.cond.acquire()
        try:
            self.timers.remove(timer)
            # Announce Queue that it has been removed
            logger.info("Timer {0} timer removed".format(timer['name']))
            self.cond.notify()
            return True
        except ValueError:
            # Announce Queue that it cannot be found
            logger.warn("Timer {0} could not be found".format(timer['name']))
            logger.debug(timer)
            return False
        finally:
            self.cond.release()

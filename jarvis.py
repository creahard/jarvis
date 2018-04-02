#!/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import coloredlogs,logging
import warnings

from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter
 
import code,time
from datetime import datetime
import requests,re
from Queue import Queue


from actions import ActionManager
from assistantTimers import assistantTimers

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger,level="INFO")

class JarvisInterface:

    def __init__(self,room,name='Jarvis',nluinternal = True,loglevel='WARN'):
        self.room = room
        self.nluinternal = nluinternal
        self.conversation = []
        logger.setLevel(loglevel)

    def train_nlu(self):
        training_data = load_data('nlu.json')
        trainer = Trainer(RasaNLUConfig("config_spacy.json"))
        trainer.train(training_data)
        model_directory = trainer.persist('models/nlu/',
                                          fixed_model_name="current")


    def run(self,actionLoglevel='ERROR'):
        if self.nluinternal:
            self.nlu = Interpreter.load("models/nlu/default/current",
                                        RasaNLUConfig("config_spacy.json"))
        self.action_mgr = ActionManager(name='Actions',
                                        replyFunction=self.reply,
                                        logLevel=actionLoglevel)
        self._queue = Queue(maxsize = 5)
        self.timers = assistantTimers(replyQueue=self._queue, logLevel=actionLoglevel)
        self.timers.start()

        try:
            while self.timers.isAlive():
                while not self._queue.empty():
                    self.reply(self._queue.get())
                    self._queue.task_done()
                req = raw_input(">> ")
                if req == '':
                    continue
                elif req == "/quit":
                    break
                elif req == "/console":
                    txt = "Enter Ctrl-D to return control to the program"
                    code.interact(banner=txt,local=locals())
                    continue
                self.conversation.append([ time.time(),'Me', req ])
                self.get_intent(req)
        except KeyboardInterrupt:
            logger.warn("Exiting from Keyboard Interrupt!")
        finally:
            fileName = time.strftime("%Y-%m-%d_%H-%M",
                         time.localtime(self.conversation[0][0]))+"-convo.log"
            logger.info("Saving conversation to "+fileName)
            convoLog = open(fileName,"w")
            for line in self.conversation:
                convoLog.write(time.strftime("%Y-%m-%d %H:%M:%S: ",
                           time.localtime(line[0]))+line[1]+": "+line[2]+"\n")
            convoLog.close()
            if not self.timers.isAlive():
                logger.crit("Timer thread died unexpectedly!")
            self.timers.stopInput()
            self.timers.join()

    def get_intent(self,req):
        if nluinternal:
            if isinstance(req, unicode):
                res = self.nlu.parse(req)
            else:
                res = self.nlu.parse(unicode(req,"utf-8"))
        else:
            import requests, json
            response = requests.post("http://localhost:5000/parse",
                                     json={"q":req})
            res = response.json()
            logger.debug("NLU response is"+str(res))
        intent = str(res['intent']['name'])
        logger.info("Intent is "+intent)
        entities = {}
        for entry in res['entities']:
            if entry['entity'] in entities:
                entities[entry['entity']].append(entry['value'])
            else:
                entities[entry['entity']] = [ entry['value'] ]
        if entities:
            logger.info("Entities found: "+str(entities))

        # Make sense of the request
        if intent == 'controlDevice':
            if not entities.has_key('room'):
                entities['room'] = [ self.room ]
            self.handle_device(entities,res['text'])
        elif intent == 'timer':
            logger.debug("Timer called with entities: "+str(entities))
            self.timers.addTimer(entities)
        else:
            try:
                getattr(self, intent)(res)
            except AttributeError as e:
                logger.critical("Intention "+intent+" is defined in NLU but not in the ActionManager module!")
                logger.critical(dir(self.action_mgr))
                self.reply ("I'm sorry, but I cannot support this request at this time.")


    def handle_device(self,entities,request_text):
        if not entities.has_key('command'):
            logger.error("Cannot determine command to send to devices.")
            return -1
        if not entities.has_key('device'):
            logger.error("Cannot identity device to command.")
            return -1

        if entities.has_key('time'):
            logger.critical("Control request for future action! "+str(entities['time']))

        if len(entities['command']) == 1 and len(entities['device']) == 1:
            for r in entities['room']:
                logger.info("MR:Attempting to send {0} to the {1} in the {2}".format(entities['command'][0],entities['device'][0],r))
                self.action_mgr.controlDevice(entities['device'][0],
                                              entities['command'][0],
                                              r)
        elif len(entities['room']) == 1 and len(entities['command']) == 1:
            for d in entities['device']:
                logger.info("MD:Attempting to send {0} to the {1} in the {2}".format(entities['command'][0],d,entities['room'][0]))
                self.action_mgr.controlDevice(d,
                                              entities['command'][0],
                                              entities['room'][0])
        elif len(entities['command']) > 1 and len(entities['device']) == 1:
            logger.info("1-Received multiple commands, and rooms for one device. Attempting to split request.")
            for index,attempt in enumerate(request_text.split(' and ',1)):
                if index > 0:
                    self.get_intent(entities['device'][0]+" "+attempt)
                else:
                    self.get_intent(attempt)
        elif len(entities['command']) > 1:
            logger.info("2-Received multiple commands, rooms, and devices. Attempting to split request.")
            for attempt in request_text.split(' and ',1):
                self.get_intent(attempt)
        elif len(entities['command']) == 1 and len(entities['device']) > 1:
            logger.info("3-Received multiple rooms and devices with one command. Attempting to split request.")
            for index,attempt in enumerate(request_text.split(' and ',1)):
                if index > 0:
                    self.get_intent(entities['command'][0]+" "+attempt)
                else:
                    self.get_intent(attempt)
        else:
            logger.critical("4-Unhandled scenario: "+str(entities)+" from "+request_text)


    def reply(self, msg):
        self.conversation.append([ time.time(), 'Jarvis', msg])
        print (msg)


    def greet(self, res):
        if datetime.now().hour < 12:
            timeframe = "morning"
        elif datetime.now().hour < 19:
            timeframe = "afternoon"
        else:
            timeframe = "evening"
        logger.info("Timeframe determined to be "+timeframe)
        self.reply ("Good "+timeframe+", sir.")


    def goodbye(self, res):
        regex = re.compile(r'thank(s| you)', re.IGNORECASE)
        if regex.search(res['text']):
            logger.debug("Replying with 'You're welcome' due to regex match on "+res['text'])
            self.reply ("You're welcome, sir")
        else:
            self.reply ("Goodbye, sir")


    def time(self, res):
        hour = datetime.now().hour
        if hour < 12:
            timeframe = "morning"
        elif hour < 19:
            timeframe = "afternoon"
        else:
            timeframe = "evening"
        if hour > 13:
            hour %= 12
        elif hour == 0:
            hour = 12
        minute = datetime.now().minute
        if minute == 0:
            minute = "o'clock"
        timeSentence = "{0}:{1:02d} in the {2}".format(hour,minute,timeframe)
        logger.debug("Time determined to be "+timeSentence)
        self.reply ("I have "+timeSentence)

    def weather(self, res):
        self.reply ("Accessing the weather.gov website...")
        response = requests.get("https://api.weather.gov/stations/KDYB/observations/current"
                                ,headers={'Accept':'application/json',
                                          'user-agent':'Python/2.7; CentOS 7'})
        if response.status_code != 200:
            logger.error("Call to weather.gov returned "+response.status_code+":"+response.reason)
            self.reply ("I'm affraid there was a problem accessing the site.");
            return
        weather = response.json()
        logger.debug("Weather.gov returned "+str(weather))
        temperature = weather['properties']['temperature']['value']
        conditions = weather['properties']['textDescription']
        if not isinstance(temperature,float):
            logger.warning("Temperature unavailable from weather.gov...")
            self.reply ("It is currently {0}, but I cannot get the temperature for some reason.".format(conditions))
        else:
            self.reply ("It is currently {0} and {1:.0f} degrees.".format(conditions,temperature*9/5+32))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                       description='Jarvis interface')
    parser.add_argument('task',
            choices=["train","run","both"],
            help="Are we training Jarvis or running him?")

    parser.add_argument('--loglevel', dest='loglevel',
            choices=["DEBUG","INFO","WARN","ERROR","CRITICAL","NONE"],
            default="WARN",
            help="Set the logger level for Jarvis")

    parser.add_argument('--actionloglevel', dest='actionloglevel',
            choices=["DEBUG","INFO","WARN","ERROR","CRITICAL","NONE"],
            default="WARN",
            help="Set the logger level for the Action Manager")

    parser.add_argument('--nluinternal', dest='nluinternal',
            choices=["True","False"], default="False",
            help="Use internal or external NLU")

    loglevel = parser.parse_args().loglevel
    actionloglevel = parser.parse_args().actionloglevel

    task = parser.parse_args().task
    if parser.parse_args().nluinternal == "False":
        nluinternal = False
    else:
        nluinternal = True
    jarvis = JarvisInterface(room="office",
                             nluinternal=nluinternal,
                             loglevel=loglevel)

    if task == "train":
        logger.info("Beginning training process...")
        jarvis.train_nlu()
    elif task == "run":
        logger.info("Loading saved models for execution...")
        jarvis.run(actionLoglevel=actionloglevel)
    elif task == "both":
        logger.info("Beginning training process...")
        jarvis.train_nlu()
        logger.info("Passing built models to execution stack...")
        jarvis.run()
    else:
        print ("Please call with train or run to begin execution")
        exit(1)

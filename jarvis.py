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
 
import code,time,sys,traceback
from datetime import datetime
import requests,re
import Queue


import actions
from assistantTimers import assistantTimers
from nonblockinginput import nonBlockingInput

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger,level="INFO")

class JarvisInterface:

    def __init__(self,room,name='Jarvis',nluinternal = True,loglevel='WARN'):
        self.room = room
        self.name = name
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
        self.action_mgr = actions.ActionManager(name='Actions',
                                        logLevel=actionLoglevel)
        self._queue = Queue.Queue(maxsize = 5)
        self.timers = assistantTimers(replyQueue=self._queue,
                                      logLevel=actionLoglevel)
        self.timers.start()
        self.nbi = nonBlockingInput(self._queue)
        self.nbi.daemon = True
        self.nbi.start()
        print("> ", end='') 
        while self.timers.isAlive() and self.nbi.isAlive():
            try:
                req = self._queue.get(True, 60.0)
                if req['origin'] == 'user':
                    if req['msg'] == "/quit":
                        break
                    elif req['msg'] == '':
                        print("> ", end='')
                        continue
                    elif req['msg'] == "/console":
                        txt = "Enter Ctrl-D to return to the program"
                        code.interact(banner=txt,local=locals())
                        continue
                    self.getIntent(req['msg'])
                    print("> ", end='')
                else:
                    self.handleJob(req)
                    print("> ", end='')
            except Queue.Empty:
                continue
            except KeyboardInterrupt:
                logger.warn("Exiting from Keyboard Interrupt!")
                break
            except:
                logger.critical(traceback.print_exc())
                break
        if not self.timers.isAlive():
            logger.critical("Timer thread is dead!")
        if not self.nbi.isAlive():
            logger.critical("Non blocking input thread is dead!")

        fileName = time.strftime("%Y%m%d-%H%M-convo.log",
                                 time.localtime(self.conversation[0][0]))
        logger.info("Saving conversation to "+fileName)
        convoLog = open(fileName,"w")
        for line in self.conversation:
            convoLog.write(time.strftime("%Y-%m-%d %H:%M:%S: ", time.localtime(line[0]))+line[1]+": "+line[2]+"\n")
        convoLog.close()
        if not self.timers.isAlive():
            logger.critical("Timer thread died unexpectedly!")
        self.timers.stopInput()
        self.timers.join()

    def getIntent(self,req):
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
        intent = res['intent']['name'].encode('ascii')
        logger.info("Intent is "+intent)
        self.conversation.append([ time.time(),'Me', res['text'], intent ])
        entities = {}
        for entry in res['entities']:
            if entry['entity'] in entities:
                entities[entry['entity']].append(entry['value'])
            else:
                entities[entry['entity']] = [ entry['value'] ]
        if not entities.has_key('room'):
            entities['room'] = [ self.room ]
        if entities:
            logger.info("Entities found: "+str(entities))
        job = {'origin': 'user',
               'intent': intent,
               'msg': res['text'].encode('ascii'),
               'entities': entities}
        # Make sense of the request
        self.handleJob(job)


    def reply(self, req):
        self.conversation.append([time.time(),
                                  'Jarvis',
                                  req['msg'],
                                  req['intent']])
        print (req['msg'])


    def greet(self, job):
        if datetime.now().hour < 12:
            timeframe = "morning"
        elif datetime.now().hour < 19:
            timeframe = "afternoon"
        else:
            timeframe = "evening"
        logger.info("Timeframe determined to be "+timeframe)
        self.reply({'intent': job['intent'],
                     'msg': "Good "+timeframe+", sir."})


    def goodbye(self, job):
        regex = re.compile(r'thank(s| you)', re.IGNORECASE)
        if regex.search(job['msg']):
            logger.debug("Replying with 'You're welcome' due to regex match on " + job['msg'])
            self.reply({'msg': "You're welcome, sir",
                         'intent': job['intent']})
        else:
            self.reply({'msg':"Goodbye, sir",
                         'intent': job['intent']})


    def time(self, job):
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
        self.reply({'msg': "I have "+timeSentence,
                     'intent': job['intent']})


    def timer(self, job):
        if job['origin'] == 'user':
            self.timers.addTimer(job['intent'], job['entities'])
        else:
            msg = "Your {0} timer has expired, sir"
            msg = msg.format(''.join(job['entities']['task']).encode('ascii'))
            self.reply({'intent': job['intent'], 'msg': msg})


    def weather(self, job):
        logger.info("Accessing the weather.gov website...")
        response = requests.get("https://api.weather.gov" \
                                "/stations/KDYB/observations/current"
                                ,headers={'Accept':'application/json',
                                      'user-agent':'Python/2.7; CentOS 7'})
        if response.status_code != 200:
            logger.error("Call to weather.gov returned " \
                         +response.status_code \
                         +":"+response.reason)
            msg = "I'm affraid there was a problem accessing the site."
            self.reply({'intent': job['intent']})
            return
        data = response.json()
        logger.debug("Weather.gov returned "+str(data))
        temperature = data['properties']['temperature']['value']
        conditions = data['properties']['textDescription']
        if not isinstance(temperature,float):
            logger.warning("Temperature unavailable from weather.gov...")
            msg = "It is currently {0}, but I cannot get the temperature " \
                  "for some reason."
            msg = msg.format(conditions)
        else:	
            msg = "It is currently {0} and {1:.0f} degrees."
            msg = msg.format(conditions,temperature*9/5+32)
        self.reply({'intent': job['intent'], 'msg': msg})


    def controlDevice(self, job):
        if not job['entities'].has_key('command'):
            logger.error("Cannot determine command to send to devices.")
            return -1
        if not job['entities'].has_key('device'):
            logger.error("Cannot identity device to command.")
            return -1

        laterExecution = False
        if job['entities'].has_key('time'):
            laterExecution = True
            logger.critical("Control request for future action! "+\
                            str(job['entities']['time']))

        try:
            if len(job['entities']['command']) == 1 \
               and len(job['entities']['device']) == 1:
                for r in job['entities']['room']:
                    log = "MR:Attempting to send {0} to the {1} in the {2}"
                    log = log.format(job['entities']['command'][0],
                                     job['entities']['device'][0],r)
                    logger.info(log)
                    self.action_mgr.controlDevice(job['entities']['device'][0],
                                                  job['entities']['command'][0],
                                                  r,laterExecution)
                    if laterExecution:
                        print ("Saving job for the future.")
                        self.timer(job)
            elif len(job['entities']['room']) == 1 and \
                 len(job['entities']['command']) == 1:
                for d in job['entities']['device']:
                    log = "MD:Attempting to send {0} to the {1} in the {2}"
                    log = log.format(job['entities']['command'][0],
                                     d,
                                     job['entities']['room'][0])
                    self.action_mgr.controlDevice(d,
                                                  job['entities']['command'][0],
                                                  job['entities']['room'][0],
                                                  laterExecution)
                    if laterExecution:
                        print ("Saving job for the future.")
                        self.timer(job)
            elif len(job['entities']['command']) > 1 and len(job['entities']['device']) == 1:
                logger.info("1-Received multiple commands, and rooms for one " \
                            "device. Attempting to split request.")
                for index,attempt in enumerate(job['msg'].split(' and ',1)):
                    if index > 0:
                        self.get_intent(job['entities']['device'][0]+" "+attempt)
                    else:
                        self.get_intent(attempt)
            elif len(job['entities']['command']) > 1:
                logger.info("2-Received multiple commands, rooms, and devices." \
                            " Attempting to split request.")
                for attempt in job['msg'].split(' and ',1):
                    self.get_intent(attempt)
            elif len(job['entities']['command']) == 1 and len(job['entities']['device']) > 1:
                logger.info("3-Received multiple rooms and devices with one " \
                            "command. Attempting to split request.")
                for index,attempt in enumerate(job['msg'].split(' and ',1)):
                    if index > 0:
                        self.get_intent(job['entities']['command'][0]+" "+attempt)
                    else:
                        self.get_intent(attempt)
            else:
                logger.critical("4-Unhandled scenario: " \
                                +str(job['entities'])+" from "+job['msg'])
        except actions.InvalidDevice as e:
            self.reply("I do not know how to control the " + e.device + \
                       " in the " + e.room)
        except:
            logger.critical(traceback.print_exc())


    def handleJob(self, job):
        try:
            getattr(self, job['intent'])(job)
        except AttributeError as e:
            logger.critical("Intention " +
                            job['intent'] +
                            " is defined in NLU but not in the" +
                            " ActionManager module!")
            logger.critical(dir(self))
            msg = "I'm sorry, but I cannot support this request at this" \
                  " time."
            self.reply({'intent': job['intent'], 'msg': msg})


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

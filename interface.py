#!/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import coloredlogs,logging
import warnings

valid_devices = ["light", "tv", "fan"]
valid_rooms   = ["living", "dining", "kitchen", "porch", "bedroom", "office",
                 "study", "master bedroom", "family", "mudroom", "foyer",
                 "gym", "back porch", "front porch", "guest", "bathroom"]

class JarvisInterface:

    def __init__(self,room,name='Jarvis',loglevel='WARN'):
        self.room = room
        self.logger = logging.getLogger('Jarvis_Interface')
        coloredlogs.install(level=loglevel,logger=self.logger)

    def run(self,intentLoglevel='DEBUG'):
        import code
        from intents import digitalAssistant

        self.jarvis = digitalAssistant('Jarvis',intentLoglevel)
    
        while True:
            req = raw_input(">> ")
            if req == "/quit":
                exit(0)
            elif req == "/console":
                code.interact(local=locals())
            self.get_intent(req)

    def get_intent(self,req):
        import requests, json
        response = requests.post("http://localhost:5000/parse",json={"q":req})
        res = response.json()
        self.logger.debug("NLU response is"+str(res))
        intent = res['intent']['name']
        self.logger.info("Intent is "+intent)
        entities = {}
        for entry in res['entities']:
            if entry['entity'] in entities:
                entities[entry['entity']].append(entry['value'])
            else:
                entities[entry['entity']] = [ entry['value'] ]
        if entities:
            self.logger.info("Entities found: "+str(entities))

        # Make sense of the request
        if intent == 'controlDevice':
            if not entities.has_key('room'):
                entities['room'] = [ self.room ]
            self.handle_device(entities,res['text'])
        else:
            try:
                getattr(self.jarvis, intent)(res)
            except AttributeError as e:
                self.logger.critical("Intention "+intent+" is defined in NLU but not in the DigitalAssistant module!")
                print ("I'm sorry, but I cannot support this request at this time.")        


    def handle_device(self,entities,request_text):
        if not entities.has_key('command'):
            self.logger.error("Cannot determine command to send to devices.")
            return -1
        if not entities.has_key('device'):
            self.logger.error("Cannot identity device to command.")
            return -1

        if len(entities['command']) == 1 and len(entities['device']) == 1:
            for r in entities['room']:
                self.logger.info("MR:Attempting to send {0} to the {1} in the {2}".format(entities['command'][0],
                                                                                          entities['device'][0],r))
                self.jarvis.controlDevice(entities['device'][0],entities['command'][0],r)
        elif len(entities['room']) == 1 and len(entities['command']) == 1:
            for d in entities['device']:
                self.logger.info("MD:Attempting to send {0} to the {1} in the {2}".format(entities['command'][0],
                                                                                          d,entities['room'][0]))
                self.jarvis.controlDevice(d,entities['command'][0],entities['room'][0])
        elif len(entities['command']) > 1 and len(entities['device']) == 1:
            self.logger.info("1-Received multiple commands, and rooms for one device. Attempting to split request.")
            for index,attempt in enumerate(request_text.split(' and ',1)):
                if index > 0:
                    self.get_intent(entities['device'][0]+" "+attempt)
                else:
                    self.get_intent(attempt)
        elif len(entities['command']) > 1:
            self.logger.info("2-Received multiple commands, rooms, and devices. Attempting to split request.")
            for attempt in request_text.split(' and ',1):
                self.get_intent(attempt)
        elif len(entities['command']) == 1 and len(entities['device']) > 1:
            self.logger.info("3-Received multiple rooms and devices with one command. Attempting to split request.")
            for index,attempt in enumerate(request_text.split(' and ',1)):
                if index > 0:
                    self.get_intent(entities['command'][0]+" "+attempt)
                else:
                    self.get_intent(attempt)
        else:
            self.logger.critical("4-Unhandled scenario: "+str(entities)+" from "+request_text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                       description='Jarvis interface')
    parser.add_argument('task',
            choices=["train","run","both"],
            help="Are we training Jarvis or running him?")

    parser.add_argument('--loglevel', dest='loglevel',
            choices=["DEBUG","INFO","WARN","ERROR","CRITICAL","NONE"],
            default="WARN",
            help="Set the logging level for Jarvis")

    loglevel = parser.parse_args().loglevel
    logger = logging.getLogger('Jarvis_Interface')
    coloredlogs.install(level=loglevel,logger=logger)

    task = parser.parse_args().task

    jarvis = JarvisInterface(room="office",loglevel=loglevel)

    if task == "train":
        logger.info("Beginning training process...")
        jarvis.train_nlu()
    elif task == "run":
        logger.info("Loading saved models for execution...")
        jarvis.run()
    elif task == "both":
        logger.info("Beginning training process...")
        jarvis.train_nlu()
        logger.info("Passing built models to execution stack...")
        jarvis.run()
    else:
        print ("Please call with train or run to begin execution")
        exit(1)

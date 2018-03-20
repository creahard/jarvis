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

logger = logging.getLogger('Jarvis_Interface')
coloredlogs.install(level='INFO',logger=logger)

def run():
    import code
    import requests, json
    from intents import digitalAssistant

    jarvis = digitalAssistant(name='Jarvis',room='study',logLevel='DEBUG')
    
    while True:
        req = raw_input(">> ")
        if req == "/quit":
            exit(0)
        elif req == "/console":
            code.interact(local=locals())
        
        response = requests.post("http://localhost:5000/parse",json={"q":req})
        res = response.json()
        logger.debug("NLU response is"+str(res))
        intent = res['intent']['name']
        logger.info("Intent is "+intent)
        try:
            getattr(jarvis, intent)(res)
        except AttributeError as e:
            logger.critical("Intention "+intent+" is defined in NLU but not in the DigitalAssistant module!")
            print ("I'm sorry, but I cannot support this request at this time.")        

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
    coloredlogs.install(level=loglevel,logger=logger)

    task = parser.parse_args().task

    if task == "train":
        logger.info("Beginning training process...")
        train_nlu()
    elif task == "run":
        logger.info("Loading saved models for execution...")
        run()
    elif task == "both":
        logger.info("Beginning training process...")
        train_nlu()
        logger.info("Passing built models to execution stack...")
        run()
    else:
        print ("Please call with train or run to begin execution")
        exit(1)

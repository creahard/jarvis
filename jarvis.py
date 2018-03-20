#!/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import warnings

from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer
from rasa_nlu.model import Metadata, Interpreter


valid_devices = ["light", "tv", "fan"]
valid_rooms   = ["living", "dining", "kitchen", "porch", "bedroom", "office",
                 "study", "master bedroom", "family", "mudroom", "foyer",
                 "gym", "back porch", "front porch", "guest", "bathroom"]


def train_nlu():
    training_data = load_data('nlu.json')
    trainer = Trainer(RasaNLUConfig("config_spacy.json"))
    trainer.train(training_data)
    model_directory = trainer.persist('models/nlu/', fixed_model_name="current")

    return model_directory


def run():
    import code
    bot = Interpreter.load("models/nlu/default/current", RasaNLUConfig("config_spacy.json"))
    while True:
        req = raw_input(">> ")
        if req == "/quit":
            exit(0)
        elif req == "/console":
            code.interact(local=locals())
        res = bot.parse(unicode(req,"utf-8"))
        print ("Intent is "+res['intent']['name'])
        if len(res['entities']):
            for entity in res['entities']:
                print (entity['entity']+": "+entity['value'])
                if entity['entity'] == "room" and not any(entity['value'] in r for r in valid_rooms):
                    print (entity['value']+" was misidentified as a room in "+res['text'])
                if entity['entity'] == "device" and not any(entity['value'] in d for d in valid_devices):
                    print (entity['value']+" was misidentified as a device in "+res['text'])
                

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                       description='starting Jarvis')
    parser.add_argument('task',
            choices=["train","run","both"],
            help="Are we training Jarvis or running him?")

    task = parser.parse_args().task

    if task == "train":
        train_nlu()
    elif task == "run":
        run()
    elif task == "both":
        train_nlu()
        run()
    else:
        print ("Please call with train or run to begin execution")
        exit(1)

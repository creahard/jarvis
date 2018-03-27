#!/bin/python
"""Attempt to convert strings into actual times.
Timer intents will have relative times to be converted into actual Notification times
Notification times will refer to the next day if the specified time has already passed
"""
import time
from word2number import w2n

listing = ["ninety seconds", "when an hour", "when a minute", "ten minutes", "three hours", "half an hour", "sixteen thirty", "seven pm", "ten minutes and thirty seconds", "seven thirty am", "five thirty pm"]


def getTime(string):
    tokens = []
    event = 0
    for inx,w in enumerate(string.split( )):
        try:
            tokens.append(w2n.word_to_num(w))

        except ValueError as e:
            if w.find('hour') == 0:
                if len(tokens) == 0:
                    if string.find('half') != -1:
                        tokens.append(3600/2)
                    else:
                        tokens.append(3600)
                elif isinstance(tokens[-1],int):
                    tokens[-1] *= 3600
            elif w.find('minute') == 0:
                if len(tokens) == 0:
                    tokens.append(60)
                elif isinstance(tokens[-1],int):
                    tokens[-1] *= 60
            elif w.find('pm') == 0:
                if isinstance(tokens[0],int):
                    tokens[0] += 12
            else:
                pass

    if string.find('minute') > -1 or string.find('hour') > -1 or string.find('second') > 1:
        value = 0
        for i in tokens:
            value += i
        return value
    elif len(tokens) == 1:
        return "{0}:00".format(tokens[0])
    elif len(tokens) == 2:
        return "{0}:{1}".format(tokens[0],tokens[1])
    elif len(tokens) == 3:
        return "{0}:{1}:{2}".format(tokens[0],tokens[1],tokens[2])


for l in listing:
    print (l+" "+str(getTime(l)))

#!/bin/python
"""Attempt to convert strings into actual times.
Timer intents will return relative times in integer seconds.
Notification times will refer to the next day if the specified time has already passed
"""
import time,code
from word2number import w2n

class InvalidTime(Exception):
    def __init__(self,msg):
        Exception.__init__(self,msg)

def convert(string):
    if isinstance(string,list):
        string = ''.join(string)
    if isinstance(string,unicode):
        string = string.encode('ascii')
    tokens = []
    for inx,w in enumerate(string.split( )):
        try:
            tokens.append(w2n.word_to_num(w))

        except ValueError as e:
            if w.find('hour') == 0:
                if string.find('half') != -1:
                    tokens.append(1800)
                if len(tokens) == 0:
                    tokens.append(3600)
                else:
                    for i in range(0,inx):
                        if tokens[i] < 1800:
                            tokens[i] *= 3600
            elif w.find('minute') == 0:
                if len(tokens) == 0:
                    tokens.append(60)
                elif len(tokens) > 0:
                    for i in range(0,len(tokens)):
                        if isinstance(tokens[i],int) and tokens[i] < 1800:
                            tokens[i] *= 60
            elif w.find('pm') == 0:
                if isinstance(tokens[0],int) and tokens[0] < 12:
                    tokens[0] += 12
                    if tokens[0] == 24:
                        tokens[0] = 0
            elif w.find('am') == 0 and tokens[0] == 12:
                tokens[0] = 0
            else:
                pass

                
    if string.find('minute') > -1 or string.find('hour') > -1 or string.find('second') > 1:
        value = 0
        for i in tokens:
            value += i
        return value
    elif len(tokens) == 1:
        return "{:02d}:00".format(tokens[0])
    elif len(tokens) == 2:
        if string.find('oh') > -1:
            return "{:02d}:{:02d}".format(tokens[0],tokens[1])
        elif tokens[0] == 20 and tokens[1] < 4:
            return("{0}:00".format(tokens[0] + tokens[1]))
        else:
            return "{:02d}:{:02d}".format(tokens[0],tokens[1])
    elif len(tokens) == 4:
        tokens[0] += tokens[1]
        tokens[2] += tokens[3]
        del tokens[3]
        del tokens[1]
        return "{:02d}:{:02d}".format(tokens[0],tokens[1])
    elif len(tokens) == 3:
        if tokens[1] < 10 and tokens[0] > tokens[1]:
            tokens[0] += tokens[1]
            del tokens[1]
            return "{:02d}:{:02d}".format(tokens[0],tokens[1])
        elif tokens[1] > tokens[2]:
            tokens[1] += tokens[2]
            del tokens[2]
            return "{:02d}:{:02d}".format(tokens[0],tokens[1])
    else:
        raise InvalidTime(string)


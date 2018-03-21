# Jarvis

This is my attempt at making my own Digital Assistant with two main requirements:

1. No cloud interface required
  * I want him to be able to function w/out being connected to the Internet
2. Context aware
  * When I get to speech recognition I will have microphones in most rooms and saying "Jarvis turn off the lights" should be understood as affecting the room of the source.

## What I've found so far

Natural Language Understanding (NLU) exists as a python module in Rasa_NLU. Conveniently the same group produces Rasa_Core which adds Machine Learning to train conversations and triggerable actions that I can write handlers for. Rasa_Core can keep track of a conversations path and "remember" details as the exchange goes on providing some significant contextual awareness, but unless I want to run "Jarvis" instances for each room I haven't quite figured out a good way to pass such metadata through to its agent, so for now I'm using Rasa_NLU and working on my own Core. Another issue I have is I don't see a good way to force Core into a particular state where one action continues to receive all "spoken" words and phrases until a goodbye intent is received (think verbal tv remote, taking a note, calling out items to populate a list, etc).

As I build out functions to handle what Rasa_NLU as decided was my "intent" I will revisit Rasa_Core and may very well switch back to it.

## Sub-Requirements

Since I don't want to use existing cloud services I have to find and integrate existing services for
* Speech to text
  * Found CMU Sphinx
* Text to Speech
  * Bonus points for British accent short of hiring Paul Bettany
* Speaker Recognition
  * This will be integrated with Insteon and Z-Wave devices, but I will not allow it to send an Unlock command to a deadbolt if it doesn't recognize the speaker
* Facial recognition
  * Combined with speaker recognition for the above scenario, unprompted greeting and notifications, etc. Not planning on arm or body gesturing to control the TVs or computers, but someone else can. 

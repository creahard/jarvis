#!/bin/python
### Build a conversaional training file for Rasa NLU from a set of lists

import json,re

training_data = {
    "rasa_nlu_data": {
        "common_examples": [
            {
                "entities": [],
                "intent": "affirm",
                "text": "yes"
            },
            {
                "entities": [],
                "intent": "affirm",
                "text": "please"
            },
            {
                "entities": [],
                "intent": "affirm",
                "text": "yes please"
            },
            {
                "entities": [],
                "intent": "affirm",
                "text": "yeah"
            },
            {
                "entities": [],
                "intent": "affirm",
                "text": "correct"
            },
            {
                "entities": [],
                "intent": "affirm",
                "text": "affirmative"
            },
            {
                "entities": [],
                "intent": "affirm",
                "text": "please do"
            },
            {
                "entities": [],
                "intent": "deny",
                "text": "no"
            },
            {
                "entities": [],
                "intent": "deny",
                "text": "incorrect"
            },
            {
                "entities": [],
                "intent": "deny",
                "text": "that's not correct"
            },
            {
                "entities": [],
                "intent": "deny",
                "text": "that is incorrect"
            },
            {
                "entities": [],
                "intent": "deny",
                "text": "negative"
            }
        ],
        "entity_synonyms": [
            {
                "synonyms": [
                    "television",
                    "television set",
                    "telly",
                    "boob tube",
                    "tube",
                    "baby sitter",
                    "tv set",
                    "idiot box"
                ],
                "value": "tv"
            }
        ],
        "regex_features": [
            {
                "name": "light",
                "pattern": "light[s]?"
            },
            {
                "name": "rooms",
                "pattern": "(dining|family|living)( room)?"
            }
        ]
    }
}

# Items are {0} in formatted strings
items = ["light", "lights", "fan", "tv", "radio", "cable box", "dvd player", "bluray player"]
# Rooms are {1} in formatted strings
rooms = ["kitchen", "dining room", "living room", "bedroom", "bathroom", "family room", "master bedroom", "guest bedroom", "guest bathroom", "back porch", "front porch", "porch", "foyer", "hall", "hallway", "garage", "office", "study", "library"]

greet = [
["hello"],
["hey"],
["hi"],
["good morning",{'timeframe':'morning'}],
["good afternoon",{'timeframe':'afternoon'}],
["good evening",{'timeframe':'evening'}],
]

goodbye = [
"goodbye",
"bye",
"later",
"thank you"
]

weather = [
"how is it outside",
"what is the weather",
"what does it look like today",
"will I need an umbrella",
"is it nice outside",
"how hot is it now",
"how cold is it now"
]

intent_time = [
"what time is it",
"do you have the time",
"what does the clock say now"
]

lines = [
"please turn on the {0} in the {1}",
"turn on the {0} in the {1} please",
"please turn on the {0}",
"turn on the {0} please",
"turn on the {0}",
"can you turn on the {0} please",
"can you please turn on the {0} in the {1}",
"please turn off the {0} in the {1}",
"turn off the {0} in the {1} please",
"please turn off the {0}",
"turn off the {0} please",
"turn off the {0}",
"can you turn off the {0} please",
"can you please turn off the {0} in the {1}",
"flip on the {0} in the {1}",
"please flip on the {0}",
"flip on the {0} in the {1} please",
"flip off the {0} in the {1}",
"please flip off the {0}",
"flip off the {0} in the {1} please",
"cut on the {0} in the {1}",
"please cut on the {0}",
"cut on the {0} in the {1} please",
"cut off the {0} in the {1}",
"please cut off the {0}",
"cut off the {0} in the {1} please",
"kill the {0}",
"kill the {0} in the {1}",
"kill the {0} please",
"please kill the {0} in the {1}"]

queries = [
"who turned on the {0}",
"who turned on the {0} in the {1}",
"when was the {0} turned on",
"when was the {0} turned on in the {1}",
"why is the {0} on",
"why is the {0} on in the {1}",
"how did the {0} get turned on",
"how did the {0} get turned on in the {1}",
"how did the {0} in the {1} get turned on",
"who turned off the {0}",
"who turned off the {0} in the {1}",
"when was the {0} turned on",
"when was the {0} turned off in the {1}",
"why is the {0} on",
"why is the {0} off in the {1}",
"how did the {0} get turned on",
"how did the {0} get turned off in the {1}",
"how did the {0} in the {1} get turned on"]

schedules = [
"{2} turn on the {0}",
"{2} turn on the {0} in the {1}",
"{2} turn on the {0} please",
"please turn on the {0} {2}",
"please turn on the {0} in the {1} {2}",
"turn on the {0} {2} please",
"{2} turn off the {0}",
"{2} turn off the {0} in the {1}",
"{2} turn off the {0} please",
"please turn off the {0} {2}",
"please turn off the {0} in the {1} {2}",
"turn off the {0} {2} please",
"please kill the {0} {2}",
"{2} kill the {0} in the {1}"]

intent_timers = [
"give me a {0} timer for {1}",
"give me an {0} timer for {1}",
"give me a timer for {1}",
"let me know when {1} have past",
"tell me when it's been {1}",
"tell me when {1} have past",
"I need a {1} timer for {0}",
"I need an {1} timer for {0}"]

notices = [
"let me know when it is {0}",
"tell me when it is {0}",
]

# Start and End - Just return the start and end of item in string
def sne(string,item):
    start = string.find(item)
    end   = len(item) + start
    return [start,end]

def buildEntity(line,room="",item="",time=""):
    hasOn = re.compile(r'\b(on)\b')
    hasOff = re.compile(r'\b(off)\b')
    hasKill = re.compile(r'\b(kill)\b')
    entity = {}
    entity['entities'] = []
    clock = ""
    if not time == "":
        if any(trig in time for trig in ['minute', 'hour', 'second','day']):
            clock = "in "+time
        else:
            clock = "at "+time
    entity['text'] = line.format(item,room,clock)
    if line.find('{1}') > -1:
        [start, end] = sne(entity['text'],room)
        entity['entities'].append({
                'start': start, 'end': end,
                'value': room, 'entity': 'room'})
    if line.find('{0}') > -1:
        [start, end] = sne(entity['text'],item)
        entity['entities'].append({
                'start': start, 'end': end,
                'value': item, 'entity': 'device'})
        _on   = hasOn.search(entity['text'])
        _off  = hasOff.search(entity['text'])
        _kill = hasKill.search(entity['text'])
        if _on:
            [start, end] = _on.span()
            entity['entities'].append({
                    'start': start, 'end': end,
                    'value': 'on', 'entity': 'command'})
        elif _off:
            [start, end] = _off.span()
            entity['entities'].append({
                    'start': start, 'end': end,
                    'value': 'off', 'entity': 'command'})
        elif _kill:
            [start, end] = _kill.span()
            entity['entities'].append({
                    'start': start, 'end': end,
                    'value': 'off', 'entity': 'command'})
    if line.find('{2}') > -1:
        [start, end] = sne(entity['text'],time)
        entity['entities'].append({
                'start': start, 'end': end,
                'value': time, 'entity': 'time'})

    return entity

for g in greet:
    entry = {}
    entry['text']   = g[0]
    entry['intent'] = 'greet'
    entry['entities'] = []
    if len(g) > 1:
        for entity,value in g[1].iteritems():
            p = re.compile(r'\b'+value+r'\b')
            [start,end] = p.search(g[0]).span()
            entry['entities'].append({'start':start,'end':end,'value':value,'entity':entity})
    training_data['rasa_nlu_data']['common_examples'].append(entry)

for g in goodbye:
    training_data['rasa_nlu_data']['common_examples'].append({'intent':'goodbye','text':g,'entities': []})

for w in weather:
    training_data['rasa_nlu_data']['common_examples'].append({'intent':'weather','text':w,'entities': []})

for t in intent_time:
    training_data['rasa_nlu_data']['common_examples'].append({'intent':'time','text':t,'entities': []})

for line in lines:
   for i in items:
       for r in rooms:
           entity = buildEntity(line=line,item=i,room=r)
           entity['intent'] = 'controlDevice'
           training_data['rasa_nlu_data']['common_examples'].append(entity)
           if line.find('{1}') == -1:
               break

for line in queries:
   for i in items:
       for r in rooms:
           entity = buildEntity(line=line,item=i,room=r)
           entity['intent'] = 'queryDevice'
           if entity['text'].find('who') != -1:
              query = 'who'
              end   = 3
           elif entity['text'].find('how') != -1:
              query = 'how'
              end   = 3
           elif entity['text'].find('why') != -1:
              query = 'why'
              end   = 3
           else:
              query = 'when'
              end   = 4
           entity['entities'].append({
                   'start': 0, 'end': end,
                   'value': query, 'entity': 'cognitive'})
           training_data['rasa_nlu_data']['common_examples'].append(entity)
           if line.find('{1}') == -1:
               break

times = ["five minutes", "ten pm", "one hour", "four hours", "eight am", "sixteen thirty", "noon", "midnight", "a half hour", "half an hour", "eleven o'clock"]
for l in schedules:
   for i in items:
       for r in rooms:
           for t in times:
               entity = buildEntity(line=l,item=i,room=r,time=t)
               entity['intent'] = 'controlDevice'
               training_data['rasa_nlu_data']['common_examples'].append(entity)
           if l.find('{1}') == -1:
               break

timers = ["five minutes", "one hour", "four hours", "three minutes fourty five seconds", "one minute", "sixty seconds", "three minutes and thirty seconds", "a half hour", "half an hour"]
for l in intent_timers:
   for t in timers:
       for task in ["egg","laundry","cooking","nap","exersize","break"]:
          entry = {}
          entry['text']   = l.format(task,t)
          entry['intent'] = 'timer'
          entry['entities'] = []
          p = re.compile(r'\b'+t+r'\b')
          [start,end] = p.search(entry['text']).span()
          entry['entities'].append({'start':start,'end':end,'value':t,'entity':'time'})
          if l.find('{0}') > -1:
              p = re.compile(r'\b'+task+r'\b')
              [start,end] = p.search(entry['text']).span()
              entry['entities'].append({'start':start,'end':end,'value':task,'entity':'task'})
          training_data['rasa_nlu_data']['common_examples'].append(entry)
          if l.find('{0}') == -1:
              break

times = ["five o'clock", "ten pm", "one am", "fourteen hundred", "eight am", "sixteen thirty", "noon", "midnight", "eleven o'clock"]
for l in notices:
   for t in times:
      entry = {}
      entry['text']   = l.format(t)
      entry['intent'] = 'notify'
      entry['entities'] = []
      p = re.compile(r'\b'+t+r'\b')
      [start,end] = p.search(entry['text']).span()
      entry['entities'].append({'start':start,'end':end,'value':t,'entity':'time'})
      training_data['rasa_nlu_data']['common_examples'].append(entry)

print (json.dumps(training_data))


#!/bin/python
### Build a conversaional training file for Rasa NLU from a set of lists

import json, re

training_data = {
    "rasa_nlu_data": {
        "common_examples": [
            {
                "entities": [],
                "intent": "greet",
                "text": "hello"
            },
            {
                "entities": [],
                "intent": "greet",
                "text": "hi"
            },
            {
                "entities": [],
                "intent": "greet",
                "text": "hey"
            },
            {
                "entities": [
                    {
                        "end": 12,
                        "entity": "timeframe",
                        "start": 5,
                        "value": "morning"
                    }
                ],
                "intent": "greet",
                "text": "good morning"
            },
            {
                "entities": [
                    {
                        "end": 14,
                        "entity": "timeframe",
                        "start": 5,
                        "value": "afternoon"
                    }
                ],
                "intent": "greet",
                "text": "good afternoon"
            },
            {
                "entities": [
                    {
                        "end": 12,
                        "entity": "timeframe",
                        "start": 5,
                        "value": "evening"
                    }
                ],
                "intent": "greet",
                "text": "good evening"
            },
            {
                "entities": [],
                "intent": "goodbye",
                "text": "goodbye"
            },
            {
                "entities": [],
                "intent": "goodbye",
                "text": "bye"
            },
            {
                "entities": [],
                "intent": "goodbye",
                "text": "later"
            },
            {
                "entities": [],
                "intent": "goodbye",
                "text": "thank you"
            },
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
            },
            {
                "entities": [
                    {
                        "end": 17,
                        "entity": "location",
                        "start": 10,
                        "value": "outside"
                    }
                ],
                "intent": "weather",
                "text": "how is it outside"
            },
            {
                "entities": [
                    {
                        "end": 29,
                        "entity": "location",
                        "start": 25,
                        "value": "here"
                    }
                ],
                "intent": "weather",
                "text": "what is the weather like here"
            },
            {
                "entities": [
                    {
                        "end": 28,
                        "entity": "timeframe",
                        "start": 23,
                        "value": "today"
                    }
                ],
                "intent": "weather",
                "text": "what does it look like today"
            },
            {
                "entities": [],
                "intent": "weather",
                "text": "will I need an umbrella"
            },
            {
                "entities": [
                    {
                        "end": 9,
                        "entity": "clock",
                        "start": 5,
                        "value": "time"
                    }
                ],
                "intent": "time",
                "text": "what time is it"
            },
            {
                "entities": [
                    {
                        "end": 20,
                        "entity": "clock",
                        "start": 16,
                        "value": "time"
                    }
                ],
                "intent": "time",
                "text": "do you have the time"
            },
            {
                "entities": [
                    {
                        "end": 27,
                        "entity": "timeframe",
                        "start": 24,
                        "value": "now"
                    }
                ],
                "intent": "time",
                "text": "what does the clock say now"
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

lines = [
"please turn on the {0} in the {1}",
"turn on the {0} in the {1} please",
"please turn on the {0}",
"turn on the {0} please",
"can you turn on the {0} please",
"can you please turn on the {0} in the {1}",
"please turn off the {0} in the {1}",
"turn off the {0} in the {1} please",
"please turn off the {0}",
"turn off the {0} please",
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
]

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

data = {'common_examples': []}

hasItem = re.compile(r'\{0\}')
hasRoom = re.compile(r'\{1\}')

# Start and End - Just return the start and end of item in string
def sne(string,item):
    start = string.find(item)
    end   = len(item) + start
    return [start,end]

def buildEntity(line,room=None,item=None):
    entity = {}
    entity['entities'] = []
    if hasItem.search(line) and hasRoom.search(line):
        entity['text'] = line.format(item,room)
        [start, end] = sne(entity['text'],room)
        entity['entities'].append({
                'start': start, 'end': end,
                'value': room, 'entity': 'room'})
    elif hasItem.search(line):
        entity['text'] = line.format(item)
    [start, end] = sne(entity['text'],item)
    entity['entities'].append({
            'start': start, 'end': end,
            'value': item, 'entity': 'device'})

    if entity['text'].find(' on') > -1:
        [start, end] = sne(entity['text'],' on')
        entity['entities'].append({
                'start': start+1, 'end': end,
                'value': 'on', 'entity': 'command'})
    else:
        [start, end] = sne(entity['text'],' off')
        entity['entities'].append({
                'start': start+1, 'end': end,
                'value': 'off', 'entity': 'command'})
    return entity

for line in lines:
   for i in items:
       for r in rooms:
           entity = buildEntity(line=line,item=i,room=r)
           entity['intent'] = 'controlDevice'
           training_data['rasa_nlu_data']['common_examples'].append(entity)
           if not hasRoom.search(line):
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
           if not hasRoom.search(line):
               break

print (json.dumps(training_data))

       

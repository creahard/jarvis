#!/bin/python
### Build a conversaional training file for Rasa NLU from a set of lists

import json,re

rooms = ["kitchen", "dining room", "living room", "bedroom", "bathroom", "family room", "master bedroom", "guest bedroom", "guest bathroom", "back porch", "front porch", "porch", "foyer", "hall", "hallway", "garage", "office", "study", "library"]
insteon = ["light", "lights", "fan"]
irdevices = ["tv", "radio", "cable box", "dvd player", "bluray player"]

lines = ["Please turn on the {0} in the {1}",
"Turn on the {0} in the {1} please",
"Please turn on the {0}",
"Turn on the {0} please",
"Can you turn on the {0} please",
"Can you please turn on the {0} in the {1}",
"Please turn off the {0} in the {1}",
"Turn off the {0} in the {1} please",
"Please turn off the {0}",
"Turn off the {0} please",
"Can you turn off the {0} please",
"Can you please turn off the {0} in the {1}"]

queries = ["Who turned on the {0}",
"Who turned on the {0} in the {1}",
"When was the {0} turned on",
"When was the {0} turned on in the {1}",
"Why is the {0} on",
"Why is the {0} on in the {1}",
"How did the {0} get turned on",
"How did the {0} get turned on in the {1}",
"How did the {0} in the {1} get turned on",
"Who turned off the {0}",
"Who turned off the {0} in the {1}",
"When was the {0} turned on",
"When was the {0} turned off in the {1}",
"Why is the {0} on",
"Why is the {0} off in the {1}",
"How did the {0} get turned on",
"How did the {0} get turned off in the {1}",
"How did the {0} in the {1} get turned on"]

data = {'common_examples': []}

hasItem = re.compile(r'0')
hasRoom = re.compile(r'1')

def sne(string,item):
    start = string.find(item)
    end   = len(item) + start
    return [start,end]

def buildEntity(line,room=None,item=None):
    entity = {}
    entity['entities'] = []
    if hasItem.search(line) and hasRoom.search(line):
        entity['text'] = line.format(item,room)
        [start, end] = sne(entity['text'],item)
        keyword = {'start': start, 'end': end, 'value': item, 'entity': 'device'}
        entity['entities'].append(keyword)
        [start, end] = sne(entity['text'],room)
        keyword = {'start': start, 'end': end, 'value': room, 'entity': 'room'}
        entity['entities'].append(keyword)
    elif hasItem.search(line):
        entity['text'] = line.format(item)
        [start, end] = sne(entity['text'],i)
        keyword = {'start': start, 'end': end, 'value': item, 'entity': 'device'}
        entity['entities'].append(keyword)
    return entity

for line in lines:
   for i in insteon:
       for r in rooms:
           entity = buildEntity(line=line,item=i,room=r)
           if line.find(' on ') != -1:
              setting = 'on'
              start = line.find(' on ') + 1
              end   = start + 2
           else:
              setting = 'off'
              start   = line.find(' off ') + 1
              end     = start + 3
           entity['entities'].append({'start': start, 'end': end, 'value': setting, 'entity': 'set'})
           entity['intent'] = 'insteon'
           data['common_examples'].append(entity)
           del (start,end,setting)
           if not hasRoom.search(line):
               break
   for i in irdevices:
       for r in rooms:
           entity = buildEntity(line=line,item=i,room=r)
           if line.find(' on ') != -1:
              setting = 'on'
              start = line.find(' on ') + 1
              end   = start + 2
           else:
              setting = 'off'
              start   = line.find(' off ') + 1
              end     = start + 3
           entity['entities'].append({'start': start, 'end': end, 'value': setting, 'entity': 'set'})
           entity['intent'] = 'infrared'
           data['common_examples'].append(entity)
           del (start,end,setting)
           if not hasRoom.search(line):
               break

for line in queries:
   for i in insteon:
       for r in rooms:
           entity = buildEntity(line=line,item=i,room=r)
           if entity['text'].find(' on ') != -1:
              setting = 'on'
              start = entity['text'].find(' on') + 1
              end   = start + 2
           else:
              setting = 'off'
              start   = entity['text'].find(' off') + 1
              end     = start + 3
           entity['entities'].append({'start': start, 'end': end, 'value': setting, 'entity': 'set'})
           entity['intent'] = 'queryInsteon'
           if entity['text'].find('Who') != -1:
              query = 'Who'
              end   = 3
           elif entity['text'].find('How') != -1:
              query = 'How'
              end   = 3
           elif entity['text'].find('Why') != -1:
              query = 'Why'
              end   = 3
           else:
              query = 'When'
              end   = 4
           entity['entities'].append({'start': 0, 'end': end, 'value': query, 'entity': 'type'})
           data['common_examples'].append(entity)
           del (start,end,setting,query)
           if not hasRoom.search(line):
               break
   for i in irdevices:
       for r in rooms:
           entity = buildEntity(line=line,item=i,room=r)
           if entity['text'].find(' on') != -1:
              setting = 'on'
              start = entity['text'].find(' on') + 1
              end   = start + 2
           else:
              setting = 'off'
              start   = entity['text'].find(' off') + 1
              end     = start + 3
           entity['entities'].append({'start': start, 'end': end, 'value': setting, 'entity': 'set'})
           entity['intent'] = 'queryInfrared'
           if entity['text'].find('Who') != -1:
              query = 'Who'
              end   = 3
           elif entity['text'].find('How') != -1:
              query = 'How'
              end   = 3
           elif entity['text'].find('Why') != -1:
              query = 'Why'
              end   = 3
           else:
              query = 'When'
              end   = 4
           entity['entities'].append({'start': 0, 'end': end, 'value': query, 'entity': 'type'})
           data['common_examples'].append(entity)
           del (start,end,setting)
           if not hasRoom.search(line):
               break

print (json.dumps({'rasa_nlu_data': data}))

#print (data)
       

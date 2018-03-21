import coloredlogs, logging
from datetime import datetime
import re,requests

class digitalAssistant():
    validDevices = ['light', 'lights', 'fan']
    irDevices = ['tv', 'cable box', 'bluray player','radio']
    validRooms = ['office', 'study', 'living room', 'dining room', 'family room', 'kitchen',
                  'master', 'front porch', 'back porch', 'foyer', 'mudroom',
                  'guest', 'utility', 'bathroom', 'hall', 'hallway', 'counter']

    def __init__(self,room,name='Jarvis',logLevel='WARN'):
        self.room = room
        self.name = name
        self.logger = logging.getLogger(self.name)
        coloredlogs.install(level=logLevel,logger=self.logger)

    def greet(self, res):
        if datetime.now().hour < 12:
            timeframe = "morning"
        elif datetime.now().hour < 19:
            timeframe = "afternoon"
        else:
            timeframe = "evening"
        self.logger.info("Timeframe determined to be "+timeframe)    
        print ("Good "+timeframe+", sir.")
    
    
    def goodbye(self, res):
        regex = re.compile(r'thank(s| you)', re.IGNORECASE)
        if regex.search(res['text']):
            self.logger.debug("Replying with 'You're welcome' due to regex match on "+res['text'])
            print ("You're welcome, sir")
        else:
            print ("Goodbye, sir")
    
    
    def time(self, res):
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
        self.logger.debug("Time determined to be "+timeSentence)
        print ("I have "+timeSentence)
    
    
    def weather(self, res):
        print ("Accessing the weather.gov website...")
        response = requests.get("https://api.weather.gov/stations/KDYB/observations/current"
                                ,headers={'Accept':'application/json',
                                          'user-agent':'Python/2.7; CentOS 7'})
        if response.status_code != 200:
            self.logger.error("Call to weather.gov returned "+response.status_code+":"+response.reason)
            print ("I'm affraid there was a problem accessing the site.");
            return
        weather = response.json()
        self.logger.debug("Weather.gov returned "+str(weather))
        temperature = weather['properties']['temperature']['value']
        conditions = weather['properties']['textDescription']
        if temperature == "None":
            self.logger.warning("Temperature unavailable from weather.gov...")
            print ("It is currently {0}, but I cannot get the temperature for some reason.".format(conditions))
        else:
            print ("It is currently {0} and {1:.0f} degrees.".format(conditions,temperature*9/5+32))

    
    def controlDevice(self, res):
        if len(res['entities']):
            for entity in res['entities']:
                if entity['entity'] == 'room':
                    if not any(entity['value'] in r for r in self.validRooms):
                        self.logger.warn(entity['value']+" was identified as a room in \""+res['text']+"\"")
                    elif 'room' in locals():
                        self.logger.warn(entity['value']+" tagged as room but room is already determined in \""+res['text']+"\"")
                    else:
                        room = entity['value']
                elif entity['entity'] == 'command':
                    if 'command' in locals():
                        self.logger.warn("Command "+entity['value']+" found but command "+device+" already found!")
                    command = entity['value']
                elif entity['entity'] == 'device':
                    if 'device' in locals():
                        self.logger.warn("Device "+entity['value']+" found but device "+device['name']+" already found!")
                    elif any(entity['value'] in d for d in self.validDevices) or any(entity['value'] in ir for ir in self.irDevices):
                        if any(entity['value'] in d for d in self.validDevices):
                            device = {'name': entity['value'], 'control': 'insteon'}
                        else:
                            device = {'name': entity['value'], 'control': 'infrared'}
                        self.logger.warn(entity['value']+" was identified as a device in \""+res['text']+"\"")
                    else:
                        self.logger.warn("Device "+entity['value']+" is unknown!")
                        print ("I do not know how to control a "+entity['value'])
                        return -1
        if 'room' not in locals():
            self.logger.info("Room determined by message source.")
            room = self.room
        if 'device' not in locals():
            self.logger.critical("No device identified in \""+res['text']+"\"")
            print ("I'm sorry, I don't believe I can control that device.")
            return -1
        print ("Using "+device['control']+" to turn "+command+" the "+device['name']+" in the "+room)
                

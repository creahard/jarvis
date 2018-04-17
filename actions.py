import coloredlogs, logging, time
import re,requests

logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger,level="INFO")

class InvalidDevice(Exception):
    def __init__(self,device,room):
        self.device = device
        self.room = room

class ActionManager():
    validDevices = ['light', 'lights', 'fan']
    irDevices = ['tv', 'cable box', 'bluray player','radio']
    validRooms = ['office', 'study', 'living room', 'dining room',
                  'family room', 'kitchen', 'master', 'front porch',
                  'back porch', 'foyer', 'mudroom', 'guest', 'utility',
                  'bathroom', 'hall', 'hallway', 'counter']

    def __init__(self,name='Actions',logLevel='WARN'):
        self.name = name
        logger.setLevel(logLevel)


    def controlDevice(self, device, command, room, validateOnly=False):
        if any(device in d for d in self.validDevices):
            method = 'insteon'
        elif any(device in ir for ir in self.irDevices):
            method = 'infrared'
        else:
            logger.warn("Device "+device+" is unknown!")
            raise InvalidDevice(device,room)
        if not validateOnly:
            logger.info("Using "+method+" to turn "+command+" the "+device+\
                        " in the "+room)
        else:
            logger.info("Will use "+method+" to turn "+command+" the "+\
                        device+ " in the "+room)
        return 0


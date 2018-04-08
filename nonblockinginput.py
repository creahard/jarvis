#!/bin/python
"""Provide non-blocking input as a thread. Expects a Queue to send inputs back"""

import coloredlogs,logging,threading,Queue,sys


logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger,level='DEBUG')


class nonBlockingInput(threading.Thread):
    def __init__(self,queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.running = threading.Event()

    def shutdown(self):
        self.running.clear()

    def run(self):
        logger.info("Thread is starting.")
        self.running.set()
        while self.running.is_set():
            try:
                req = raw_input()
                data = {'origin': 'user', 'msg': req}
                self.queue.put(data)
            except EOFError:
                print ("Standby while the application shuts down...")
                break
            except:
                print (sys.exc_info())
                break
        logging.info("Thread is shutting down.")


#!/bin/python
"""Provide non-blocking input as a thread. Expects a Queue to send inputs back"""

import coloredlogs,logging,threading,Queue,sys,traceback


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
                logger.info("Standby while the application shuts down...")
                break
            except:
                logger.critical(traceback.print_exc())
                break
        logging.info("Thread is shutting down.")
        self.queue.put({'origin': 'user', 'msg': '/quit'})


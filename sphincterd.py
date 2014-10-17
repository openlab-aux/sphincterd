#!/usr/bin/env python2

import logging
from time import sleep

from os import path

from sphincter.serial_connection import SphincterSerialHandler
from sphincter.requestqueue import SphincterRequestQueue, SphincterRequestHandler
from sphincter.httpserver import SphincterHTTPServerRunner
from sphincter.authentication import UserManager

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)8s - %(threadName)s/%(funcName)s - %(message)s',
                        datefmt="%Y-%m-%d %H:%M")
    logging.info("ohai, this is sphincterd")
    s = SphincterSerialHandler(device='/dev/ttyACM0')
    s.connect()
    
    q = SphincterRequestQueue()
    r = SphincterRequestHandler(q, s)
    r.start()
    
    um = UserManager(dbpath="sqlite:///"+path.join(path.abspath(path.dirname(__file__)), "sphincter.sqlite"))
    
    SphincterHTTPServerRunner.start_thread(('localhost', 1337), q, s, um)
    
    
    # sleep until CTRL-C, then quit.
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        s.disconnect()
        logging.info("shutting down sphincterd, kthxbai")

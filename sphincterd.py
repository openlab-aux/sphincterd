#!/usr/bin/env python2

import logging
from time import sleep

from os import path
from sys import exit

from argparse import ArgumentParser

from sphincter.serial_connection import SphincterSerialHandler
from sphincter.requestqueue import SphincterRequestQueue, SphincterRequestHandler
from sphincter.httpserver import SphincterHTTPServerRunner
from sphincter.authentication import UserManager
from sphincter.config import SphincterConfig

if __name__ == "__main__":
    aparser = ArgumentParser(prog="sphincterd",
                             description="Spincter control daemon")
    aparser.add_argument("--configfile", action="store", 
                         default=path.join(path.abspath(path.dirname(__file__)), "sphincterd.conf"),
                         help="Path to configuration file")
    aparser.add_argument("--initdb", action="store_true", help="create database")

    args = aparser.parse_args()

    conf = SphincterConfig(args.configfile)
    config_params = conf.__dict__.keys()

    if "device" not in config_params:
        logging.critical("device parameter not in config file")
        exit(1)
        
    if "loglevel" not in config_params:
        logging.critical("loglevel parameter not in config file")
        exit(1)

    # parse loglevel
    if conf.loglevel == "DEBUG":
        loglevel = logging.DEBUG
    elif conf.loglevel == "INFO":
        loglevel = logging.INFO
    elif conf.loglevel == "WARNING":
        loglevel = logging.WARNING
    elif conf.loglevel == "ERROR":
        loglevel = logging.ERROR
    elif conf.loglevel == "CRITICAL":
        loglevel = logging.CRITICAL
    else:
        logging.critical("Unknown loglevel %s" % conf.loglevel)
        exit(1)

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

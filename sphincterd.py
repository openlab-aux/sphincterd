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
    aparser.add_argument("--test-hook", action="store", help="test hooks")

    args = aparser.parse_args()
    
    if args.test_hook is not None:
        import hooks
        if args.test_hook == "open":
            hooks.open_hook()
        elif args.test_hook == "closed":
            hooks.closed_hook()
        elif args.test_hook == "failure":
            hooks.failure_hook()
        else:
            print("unknown hook!")
            exit(1)
        exit(0)

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
    
    if "address" not in config_params:
        logging.critical("address parameter not in config file")
        exit(1)

    listen_address = conf.address

    if "portnumber" not in config_params:
        logging.critical("portnumber parameter not in config file")
        exit(1)
    
    try:
        listen_port = int(conf.portnumber)
    except ValueError:
        logging.critical("couldn't parse port number parameter")
        exit(1)

    try:
        s = SphincterSerialHandler(device=conf.device)
        s.connect()
    except (OSError, IOError), e:
        logging.critical("could not open device: %s" % str(e))
        exit(1)
        
    um = UserManager(dbpath="sqlite:///"+path.join(path.abspath(path.dirname(__file__)), "sphincter.sqlite"))
    
    q = SphincterRequestQueue()
    r = SphincterRequestHandler(q, s)
    r.start()
    
    SphincterHTTPServerRunner.start_thread((listen_address, listen_port), q, s, um)
    
    # sleep until CTRL-C, then quit.
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        s.disconnect()
        logging.info("shutting down sphincterd, kthxbai")

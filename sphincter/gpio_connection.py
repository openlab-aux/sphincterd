import logging
from threading import Thread, Event
from time import sleep

from RPi import GPIO

import hooks

class SphincterReader:
    """
    Read Sphincter state forever
    """
    def __init__(self, open_event, close_event, status_pins):
        self.open_event = open_event
        self.close_event = close_event
        self._status_pins = status_pins
        self.state = "UNKNOWN"

    def __call__(self):
        logging.info("starting reader thread")
        while True:
            # read GPIO Pins
            status = (GPIO.input(self._status_pins[0]),
                      GPIO.input(self._status_pins[1]))

            # parse status according to
            #   http://wiki.openlab-augsburg.de/openwiki:projekte:schliessanlage
            newstate = self.state

            if status[0] == 1 and status[1] == 1:
                newstate = "FAILURE"
                self.open_event.set()
                self.open_event.clear()
                self.close_event.set()
                self.close_event.clear()

            if status[0] == 1 and status[1] == 0:
                newstate = "UNLOCKED"
                self.open_event.set()
                self.open_event.clear()

            if status[0] == 0 and status[1] == 1:
                newstate = "LOCKED"
                self.close_event.set()
                self.close_event.clear()

            if newstate != self.state:
                # run hooks if state has changed
                if newstate== "UNLOCKED":
                    Thread(target=hooks.open_hook).start()
                if newstate == "LOCKED":
                    Thread(target=hooks.closed_hook).start()

                # After a failure sphincter always goes into LOCKED,
                # no matter which command is sent.
                if self.state == "FAILURE" and newstate == "LOCKED":
                    self.open_event.set()
                    self.open_event.clear()

                # if new state is FAILURE, continue both OPEN and CLOSE requests
                if newstate == "FAILURE":
                    self.open_event.set()
                    self.open_event.clear()
                    self.close_event.set()
                    self.close_event.clear()

                self.state = newstate
                logging.info("Sphincter state is now %s: Pins are %i/%i" % (self.state, status[0], status[1]))

            sleep(0.2)


class SphincterGPIOHandler:
    """
    Encapsulate Sphincter's Serial connection.
    """
    def __init__(self, status_pins=(7,11), lock_pin=13, unlock_pin=15):
        # init events
        self.closed_event = Event()
        self.open_event = Event()
        self._status_pins = status_pins
        self._lock_pin = lock_pin
        self._unlock_pin = unlock_pin

        # init GPIO Pins
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._status_pins[0], GPIO.IN)
        GPIO.setup(self._status_pins[1], GPIO.IN)
        GPIO.setup(self._lock_pin, GPIO.OUT)
        GPIO.setup(self._unlock_pin, GPIO.OUT)

        # start reader thread
        self._reader = SphincterReader(self.open_event, self.closed_event, self._status_pins)
        self._reader_thread = Thread(target=self._reader, name="ReaderThread")
        self._reader_thread.daemon = True
        self._reader_thread.start()

    def open(self):
        """
        send open command to sphincter
        """
        GPIO.output(self._unlock_pin, GPIO.HIGH)
        logging.info("opening sphincter")
        sleep(0.01)
        GPIO.output(self._unlock_pin, GPIO.LOW)

    def close(self):
        """
        send close command to sphincter
        """
        logging.info("closing sphincter")
        GPIO.output(self._lock_pin, GPIO.HIGH)
        sleep(0.01)
        GPIO.output(self._lock_pin, GPIO.LOW)

    @property
    def state(self):
        return self._reader.state

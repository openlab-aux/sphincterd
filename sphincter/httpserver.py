import logging
from threading import Thread
from urlparse import urlparse, parse_qs

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

class SphincterHTTPRequestHandler(BaseHTTPRequestHandler):
    def respond(self, code, message):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(message)
    
    def do_GET(self):
        params = self.get_params
        
        if "action" not in params.keys():
            self.send_error(400, "ACTION NOT SPECIFIED")
            return
            
        if params["action"] not in ["open", "close", "state"]:
            self.send_error(400, "INVALID ACTION")
            return
            
        if params["action"] == "open":
            self.server._serialhandler.open()
            self.respond(200, "success")
            return
        elif params["action"] == "close":
            self.server._serialhandler.close()
            self.respond(200, "success")
            return
        elif params["action"] == "state":
            # TODO: fix that
            self.respond(200, "dunno lol")
            return
       
    @property
    def get_params(self):
        parse_res = parse_qs(urlparse(self.path).query) 
        params = {}
        for k in parse_res:
            params[k] = parse_res[k][0]
        return params

    def log_message(self, format, *args):
        logging.info("HTTP Request" + format % tuple(args))

class SphincterHTTPServer(HTTPServer):
    def __init__(self, address, serialhandler):
        self._serialhandler = serialhandler
        HTTPServer.__init__(self, address, SphincterHTTPRequestHandler)
        
class SphincterHTTPServerRunner(object):
    def __init__(self, address, serialhandler):
        self._address = address
        self._serialhandler = serialhandler

    def __call__(self):
        s = SphincterHTTPServer(self._address, self._serialhandler)
        logging.info("HTTP Server starting up")
        s.serve_forever()
        
    @classmethod
    def start_thread(cls, address, serial_connection):
        t = Thread(name="HTTPThread",
                   target=cls(address, serial_connection))
        t.daemon = True
        t.start()

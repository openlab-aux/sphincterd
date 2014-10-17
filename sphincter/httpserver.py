import logging
from threading import Thread
from urlparse import urlparse, parse_qs
from sphincter.requestqueue import SphincterRequest, REQUEST_OPEN, REQUEST_CLOSE

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
            r = SphincterRequest(REQUEST_OPEN)
            self.server._request_queue.append(r)
            r.event.wait()
            self.respond(200, "success")
            return
        elif params["action"] == "close":
            r = SphincterRequest(REQUEST_CLOSE)
            self.server._request_queue.append(r)
            r.event.wait()
            self.respond(200, "success")
            return
        elif params["action"] == "state":
            self.respond(200, self.server.serial_handler.state)
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
    def __init__(self, address, request_queue, serial_handler):
        self._request_queue = request_queue
        self.serial_handler = serial_handler
        HTTPServer.__init__(self, address, SphincterHTTPRequestHandler)
        
class SphincterHTTPServerRunner(object):
    def __init__(self, address, request_queue, serial_handler):
        self._address = address
        self._request_queue = request_queue
        self._serial_handler = serial_handler

    def __call__(self):
        s = SphincterHTTPServer(self._address, self._request_queue, self._serial_handler)
        logging.info("HTTP Server starting up")
        s.serve_forever()
        
    @classmethod
    def start_thread(cls, address, request_queue, serial_handler):
        t = Thread(name="HTTPThread",
                   target=cls(address, request_queue, serial_handler))
        t.daemon = True
        t.start()

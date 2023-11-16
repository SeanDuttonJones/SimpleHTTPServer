# Include Python's Socket Library
from socket import *
from threading import Thread
import datetime
from email.utils import formatdate
from typing import Any

class HttpStatus():
    OK                  = 200
    Not_Modified        = 304
    Bad_Request         = 400
    Forbidden           = 403
    Not_Found           = 404
    Length_Required     = 411

    CODES = [
        200,
        304,
        400,
        403,
        404,
        411
    ]

    _messages = {
        OK: "OK",
        Not_Modified: "Not Modified",
        Bad_Request: "Bad Request",
        Forbidden: "Forbidden",
        Not_Found: "Not Found",
        Length_Required: "Length Required"
    }

    @classmethod
    def message(HttpStatus, code):
        if code not in HttpStatus._messages.keys():
            raise ValueError("Unknown status code: " + code)
        
        return HttpStatus._messages[code]

class ConsoleLogger():
    def __init__(self):
        pass

    def server(self, message):
        log = f"[Server]: {message}"
        print(log)

    def http_connection(self, message, status_code):
        """
        params
        message: HTTPMessage object
        status_code: HTTP response code
        """
        method = message.get_method()
        resource = message.get_resource()
        version = message.get_version()
        headers = message.get_headers()

        now = datetime.datetime.now()

        log = f"[Http]: {headers['Host']} - - [{now}] \"{method} {resource} {version}\" {status_code} {HttpStatus.message(status_code)}"
        print(log)

class HttpRequest():
    def __init__(self, message):
        self.message = message
        
        decode = message.split("\r\n")
        
        request_line = decode[0]
        method, resource, version = request_line.split(" ")
        self.method = method.strip()
        self.resource = resource.strip()
        self.version = version.strip()
        
        self.headers = {}
        for item in decode[1:]:
            if item == "":
                continue

            key, value = item.split(": ")
            key = key.strip()
            value = value.strip()
            self.headers[key] = value

    def get_method(self):
        return self.method
    
    def get_resource(self):
        return self.resource
    
    def get_version(self):
        return self.version

    def get_headers(self):
        return self.headers
    
class HttpResponse():
    def __init__(self, status_code):
        self._version = "HTTP/1.1"
        self._status_code = status_code
        
        self._headers = {
            "Date": formatdate(timeval=None, localtime=False, usegmt=True),
            "Server": "SimpleHTTPServer/1.0"
        }

        self._data = None
    
    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, value):
        if value != "HTTP/1.1":
            raise ValueError("Unsupported HTTP version: " + value + ". Only HTTP/1.1 is supported")
        
        self._version = value

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value):
        if value not in HttpStatus.CODES:
            raise ValueError("Unknown status code: " + value)
        
        self._status_code = value

    @property
    def headers(self):
        return self._headers
    
    @headers.setter
    def headers(self, value, overwrite=False):
        if overwrite:
            self.headers = value
        
        self._headers.update(value)

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def _generate_response(self):
        line_break = "\r\n"
        
        # set status line
        response = f"{self._version} {self.status_code} {HttpStatus.message(self.status_code)}" + line_break
        
        # set headers
        for _, (key, value) in enumerate(self.headers.items()):
            response += f"{key.lower().capitalize()}: {value}" + line_break
        
        # add additional line break to indicate next section is the data
        response += line_break

        # set data
        if self.data is not None:
            response += self.data

        return response
    
    @property
    def response(self):
        return self._generate_response().encode()
    
    def __repr__(self):
        return self._generate_response()

class HttpServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.routes = {}


    def route(self, endpoint):
        def add_rule(view_func=None):
            if view_func is None:
                raise ValueError("view_func cannot be None")
        
            self.routes[endpoint] = view_func

            return view_func
        
        return add_rule
    
    def run(self):
        # Specify Server Port
        port = 80
        # Create TCP welcoming socket
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        # Bind the server port to the socket
        tcp_socket.bind(("", port))
        # Server begins listening for incoming TCP connections
        tcp_socket.listen(1)

        logger = ConsoleLogger()
        logger.server("running...")

        while True: # Loop forever
            # Server waits on accept for incoming requests.
            # New socket created on return
            connection, addr = tcp_socket.accept()

            # Read from socket (but not address as in UDP)
            request = connection.recv(1024).decode()

            # print(request)
            message = HttpRequest(request)
            # print("METHOD:", message.get_method())
            # print("RESOURCE:", message.get_resource())
            # print("VERSION:", message.get_version())
            # print("HEADERS:", message.get_headers())


            # Send the reply
            resource = message.get_resource()
            response = None
            
            if resource in self.routes.keys():
                response = HttpResponse(HttpStatus.OK)
                response.data = self.routes[resource]()

            else:
                response = HttpResponse(HttpStatus.Not_Found)
            
            connection.send(response.response)
            logger.http_connection(message, response.status_code)

            # Close connection too client (but not welcoming socket)
            connection.close()

server = HttpServer()

@server.route("/")
def index():
    with open("test.html") as f:
        data = f.read()

    return data

server.start()
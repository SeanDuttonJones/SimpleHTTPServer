# Include Python's Socket Library
from socket import *
from threading import Thread
import datetime
from email.utils import formatdate
from typing import Any

class ConsoleLogger():
    def __init__(self):
        pass

    def server(self, message):
        log = f"Server: {message}"
        print(log)

    def http_connection(self, message, response_code):
        """
        params
        message: HTTPMessage object
        response_code: HTTP response code
        """
        method = message.get_method()
        resource = message.get_resource()
        version = message.get_version()
        headers = message.get_headers()

        now = datetime.datetime.now()

        log = f"{headers['Host']} - - [{now}] \"{method} {resource} {version}\" {response_code}"
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
    def __init__(self):
        self.version = "HTTP/1.1"
        self.status_code = 200
        
        self.headers = {
            "Date: ": formatdate(timeval=None, localtime=False, usegmt=True),
            "Server: ": "SimpleHTTPServer/1.0"
        }

        self.data = None
        
    def set_version(self, version):
        """
        params
        version: HTTP version. e.g., HTTP/1.1
        """
        self.version = version

    def set_status_code(self, status_code):
        """
        params
        status_code: HTTP response code. e.g., 200

        The corresponding response message will be added.
        """
        self.status_code = status_code

    def set_headers(self, headers, overwrite=False):
        """
        params
        headers: dict of http headers
        overwrite: indicates if the headers should be exactly as specified in the parameters. Otherwise
                    the headers will be added to the defaults
        """
        if overwrite:
            self.headers = headers
            return headers
        
        self.headers.update(headers)
        return headers

    def set_data(self, data):
        """
        params
        data: requested data
        """
        self.data = data

    def get_response(self):
        """
        Generates HTTP response
        """
        line_break = "\r\n"
        
        # set status line
        response = f"{self.version} {self.status_code}" + line_break
        
        # set headers
        for _, (key, value) in enumerate(self.headers.items()):
            response += f"{key.lower().capitalize()} {value}" + line_break
        
        # add additional line break to indicate next section is the data
        response += line_break

        # set data
        if self.data is not None:
            response += self.data

        return response.encode()

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
            response = HttpResponse()
            status_code = 200
            
            if resource in self.routes.keys():
                response.set_data(self.routes[resource]())

            else:
                status_code = 403
            
            response.set_status_code(status_code)
            connection.send(response.get_response())
            logger.http_connection(message, status_code)

            # Close connection too client (but not welcoming socket)
            connection.close()

server = HttpServer()

@server.route("/")
def index():
    with open("test.html") as f:
        data = f.read()

    return data

server.start()
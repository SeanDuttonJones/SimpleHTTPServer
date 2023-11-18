# Include Python's Socket Library
from socket import *
from threading import Thread
import datetime
from email.utils import formatdate
from inspect import getfullargspec
from os import isatty

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

    @staticmethod
    def message(code):
        if code not in HttpStatus._messages.keys():
            raise ValueError("Unknown status code: " + code)
        
        return HttpStatus._messages[code]
    
class HttpMethod():
    GET         = "GET"
    POST        = "POST"
    HEAD        = "HEAD"
    PUT         = "PUT"
    DELETE      = "DELETE"

    METHODS = [
        GET,
        POST,
        HEAD,
        PUT,
        DELETE
    ]

class ConsoleLogger():
    def __init__(self):
        pass

    def server(self, message):
        color_code = ""
        if self._is_color_capable():
            color_code = "\033[0;35m" # purple
        
        log = f"{color_code}[Server]: {message}"
        print(log)

    def http_connection(self, status_code, request=None):
        """
        params
        message: HttpRequest object
        status_code: Http status code
        """
        color_code = ""
        if self._is_color_capable():
            if status_code == HttpStatus.OK:
                color_code = "\033[1;32m" # light green
            else:
                color_code = "\033[0;33m" # brown
        
        now = datetime.datetime.now()
        
        if request is None:
            log = f"{color_code}[Http]: [{now}] {status_code} {HttpStatus.message(status_code)}"

        else:
            method = request.method
            resource = request.url
            version = request.version
            headers = request.headers

            log = f"{color_code}[Http]: {headers['Host']} - - [{now}] \"{method} {resource} {version}\" {status_code} {HttpStatus.message(status_code)}"
        
        print(log)

    def _is_color_capable(self):
        return isatty(0)

class HttpRequestParser():
    
    def parse(self, message):
        split = message.split("\r\n")
        method, url, version = map(str.strip, split[0].split(" "))

        headers = {}
        for header in split[1:]:
            if header == "": # signals double \r\n \r\n. This means we have reached the end of the headers
                break

            key, value = map(str.strip, header.split(": "))
            headers[key] = value

        data = split[-1]

        request = HttpRequest()
        request.method = method
        request.url = url
        request.version = version
        request.headers = headers
        request.data = data

        return request

class HttpException(Exception):
    """ Raised when an Http exception occurs """
    def __init__(self, status_code, *args):
        super().__init__(*args)
        self.status_code = status_code

class HttpRequestHandler():
    
    def __init__(self):
        self.logger = ConsoleLogger()

    def handle(self, message, routes):
        parser = HttpRequestParser()
        request = None
        response = None
        
        try:
            request = parser.parse(message)
        except Exception:
            response = HttpResponse(HttpStatus.Bad_Request)
            self.logger.http_connection(response.status_code, request)
            return response
        
        if request.method in ["POST", "PUT"] and "Content-Length" not in request.headers.keys():
            response = HttpResponse(HttpStatus.Length_Required)
            self.logger.http_connection(response.status_code, request)
            return response

        # Can eventually be replaced with a routing system which would handle url variables, methods, etc.
        # --------------------------------------------
        url = request.url
        if url in routes.keys():
            try:
                response = HttpResponse(HttpStatus.OK)
                if len(routes[url]["args"]) > 0:
                    self._set_response_data(response, routes[url]["view_func"](request))
                else:
                    self._set_response_data(response, routes[url]["view_func"]())
            except HttpException as e:
                response = HttpResponse(e.status_code)

        else:
            response = HttpResponse(HttpStatus.Not_Found)
        # --------------------------------------------

        self.logger.http_connection(response.status_code, request)
        return response
    
    def _set_response_data(self, response, data):
        d = ""
        if data is not None:
            d = data

        response.data = d
            
        
class HttpRequest():
    def __init__(self):
        self._method = None
        self._url = None
        self._version = None
        self._headers = {}
        self._data = None

    @property
    def method(self):
        return self._method
    
    @method.setter
    def method(self, value):
        if value not in HttpMethod.METHODS:
            raise ValueError("Unknown method: " + value)
        
        self._method = value

    @property
    def url(self):
        return self._url
    
    @url.setter
    def url(self, value):
        self._url = value

    @property
    def version(self):
        return self._version
    
    @version.setter
    def version(self, value):
        if value != "HTTP/1.1":
            raise ValueError("Unsupported HTTP version: " + value + " .Only HTTP/1.1 is supported")
        
        self._version = value

    @property
    def headers(self):
        return self._headers
    
    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value

    def __repr__(self):
        line_break = "\r\n"
        status_line = f"{self._method} {self._url} {self._version}" + line_break
        response = status_line
        
        for _, (key, value) in enumerate(self._headers.items()):
            response += f"{key}: {value}" + line_break

        response += line_break

        if self._data is not None:
            response += self._data

        return response

class HttpResponse():
    def __init__(self, status_code):
        self._version = "HTTP/1.1"
        self._status_code = status_code
        
        self._headers = {
            "Date": formatdate(timeval=None, localtime=False, usegmt=True),
            "Server": "SimpleHTTPServer/1.0",
            "Content-Type": "text/html; charset=utf-8"
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
        response = f"{self._version} {self._status_code} {HttpStatus.message(self._status_code)}" + line_break
        
        # set headers
        for _, (key, value) in enumerate(self._headers.items()):
            response += f"{key.lower().capitalize()}: {value}" + line_break
        
        # add additional line break to indicate next section is the data
        response += line_break
        response = response.encode()

        # set data
        if self._data is not None:
            if isinstance(self._data, str):
                data = self._data.encode()
                content_length = len(data) // 2
                response += data
                self._headers["Content-Length"] = content_length

        return response
    
    @property
    def response(self):
        return self._generate_response()

class HttpServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.routes = {}

    def route(self, endpoint):
        def add_rule(view_func=None):
            if view_func is None:
                raise ValueError("view_func cannot be None")
            
            args = getfullargspec(view_func)[0] # accesses 'args'
            self.routes[endpoint] = {"view_func": view_func, "args": args}

            return view_func
        
        return add_rule
    
    def abort(self, status_code):
        raise HttpException(status_code)
    
    def run(self):
        port = 80
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.bind(("", port))
        tcp_socket.listen(1)

        logger = ConsoleLogger()
        logger.server("running...")

        while True:
            connection, addr = tcp_socket.accept()

            message = connection.recv(1024).decode()

            # Handle HTTP request
            handler = HttpRequestHandler()
            response = handler.handle(message, self.routes)

            connection.send(response.response)

            connection.close()

server = HttpServer()

# perhaps pass in the http request object as a parameter in index. It is then the job of the routing function to
# check if the required headers are present, since there are no mandatory headers in a general http request.
# then provide a function to throw an "http error". Flask uses abort, so something like this would work.
@server.route("/")
def index(request):
    with open("test.html") as f:
        data = f.read()

    return data

@server.route("/forbidden")
def forbidden(request):
    server.abort(403)

server.start()
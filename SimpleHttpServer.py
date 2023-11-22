from socket import *
from threading import Thread
import datetime
import time
from email.utils import formatdate, parsedate_to_datetime
from inspect import getfullargspec
import os

class HttpStatus():
    OK                      = 200
    Not_Modified            = 304
    Bad_Request             = 400
    Forbidden               = 403
    Not_Found               = 404
    Length_Required         = 411
    Internal_Server_Error   = 500

    CODES = [
        200,
        304,
        400,
        403,
        404,
        411,
        500
    ]

    _messages = {
        OK: "OK",
        Not_Modified: "Not Modified",
        Bad_Request: "Bad Request",
        Forbidden: "Forbidden",
        Not_Found: "Not Found",
        Length_Required: "Length Required",
        Internal_Server_Error: "Internal Server Error"
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

    def proxy_connection(self, request):
        color_code = ""
        if self._is_color_capable():
            color_code = "\033[1;32m" # light green

        now = datetime.datetime.now()

        method = request.method
        resource = request.url
        version = request.version
        headers = request.headers

        log = f"{color_code}[Http]: {headers['Host']} - - [{now}] \"{method} {resource} {version}\""
        
        print(log)

    def _is_color_capable(self):
        return os.isatty(0)

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

class HttpResponseParser():
    
    def parse(self, message):
        split = message.split("\r\n")
        version, status = map(str.strip, split[0].split(" ", 1))

        status_code, message = map(str.strip, status.split(" ", 1))
        status_code = int(status_code)

        headers = {}
        for header in split[1:]:
            if header == "": # signals double \r\n \r\n. This means we have reached the end of the headers
                break

            key, value = map(str.strip, header.split(": "))
            headers[key] = value

        data = split[-1]

        response = HttpResponse(status_code)
        response.version = version
        response.headers = headers
        response.data = data

        return response

class HttpException(Exception):
    """ Raised when an Http exception occurs """
    def __init__(self, status_code, *args):
        super().__init__(*args)
        self.status_code = status_code

class HttpRequestHandler():
    
    def __init__(self):
        self.RESOURCE_DIR = "./resources"
        
        self.logger = ConsoleLogger()
        self.resources = []

        for (dirpath, dirnames, filenames) in os.walk(self.RESOURCE_DIR):
            dirpath = dirpath.replace(self.RESOURCE_DIR, "")

            for filename in filenames:
                path = os.path.join(dirpath, filename).replace("\\", "/")
                path = path.removeprefix("/")
                path = "/" + path
                self.resources.append(path)

    def handle(self, message, routes):
        parser = HttpRequestParser()
        request = None
        response = None
        
        try:
            request = parser.parse(message)
        except Exception as e:
            print(e)
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
                print(e)
                response = HttpResponse(e.status_code)

        elif url in self.resources:
            if "If-Modified-Since" in request.headers.keys():
                header_value = request.headers["If-Modified-Since"]
                date = parsedate_to_datetime(header_value)
                if not self._if_modified_since(self.RESOURCE_DIR + url, date):
                    response = HttpResponse(HttpStatus.Not_Modified)
                else:
                    response = self._create_static_resource_response(self.RESOURCE_DIR + url)
            else:
                response = self._create_static_resource_response(self.RESOURCE_DIR + url)
                
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

    def _if_modified_since(self, path, datetime):
        modified_date = os.path.getmtime(path) # already in unix time
        unixtime = time.mktime(datetime.timetuple()) # convert datetime obj to unix time
        return modified_date > unixtime

    def _load_resource(self, path):
        with open(path) as f:
            data = f.read()

        return data
    
    def _create_static_resource_response(self, resource_path):
        response = None
        try:
            response = HttpResponse(HttpStatus.OK)
            data = self._load_resource(resource_path)
            self._set_response_data(response, data)
        except:
            response = HttpResponse(HttpStatus.Internal_Server_Error)

        return response
            
class HttpProxyRequestHandler():
    def __init__(self):
        self.logger = ConsoleLogger()

    def handle(self, message, connection):
        request_parser = HttpRequestParser()
        request = None
        response = None
        
        try:
            request = request_parser.parse(message)
        except Exception:
            response = HttpResponse(HttpStatus.Bad_Request)
            self.logger.http_connection(response.status_code, request)
            return response

        if request.method in ["POST", "PUT"] and "Content-Length" not in request.headers.keys():
            response = HttpResponse(HttpStatus.Length_Required)
            self.logger.http_connection(response.status_code, request)
            return response

        host = request.headers["Host"]

        # Modify request
        index = request.url.find(host)
        new_url = request.url[index + len(host):]
        request.url = new_url

        # Make request to destination webserver
        port = 80

        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((host, port))
        sock.send(str(request).encode())

        self.logger.proxy_connection(request)

        # Wait for response from destination webserver
        headers = sock.recv(1024)
        response_parser = HttpResponseParser()
        response = response_parser.parse(headers.decode())

        if "Content-Length" not in response.headers.keys():
            response = HttpResponse(HttpStatus.Length_Required)
            self.logger.http_connection(response.status_code, request)
            return response
        
        content_length = int(response.headers["Content-Length"])
        
        connection.send(headers)
        data_recv = 0
        while data_recv < content_length:
            data = sock.recv(1024)
            connection.send(data)
            data_recv += len(data)

        sock.close()

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
            
class ProxyServer(Thread):
    def __init__(self):
        Thread.__init__(self)
    
    def run(self):
        port = 8888
        tcp_socket = socket(AF_INET, SOCK_STREAM)
        tcp_socket.bind(("", port))
        tcp_socket.listen(1)

        logger = ConsoleLogger()
        logger.server("running...")

        while True:
            connection, addr = tcp_socket.accept()

            message = connection.recv(1024).decode()

            # Handle HTTP request
            handler = HttpProxyRequestHandler()
            handler.handle(message, connection)

            # connection.send(response.response)

            connection.close()
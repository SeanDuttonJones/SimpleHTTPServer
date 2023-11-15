# Include Python's Socket Library
from socket import *
from threading import Thread
import datetime
from email.utils import formatdate

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

class HTTPRequest():
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
    
class HTTPResponse():
    def __init__(self):
        self.version = "HTTP/1.1"
        self.code = 200
        self.status_line = f"{self.version} {self.code}"
        self.headers = {
            "Date: ": formatdate(timeval=None, localtime=False, usegmt=True),
            "Server: ": "SimpleHTTPServer/1.0"
        }

    def set_version(version):
        """
        params
        version: HTTP version. e.g., HTTP/1.1
        """
        pass

    def set_status_code(status_code):
        """
        params
        status_code: HTTP response code. e.g., 200

        The corresponding response message will be added.
        """
        pass

    def set_headers(headers):
        """
        params
        headers: dict of http headers
        """
        pass

    def set_data(data):
        """
        params
        data: requested data
        """
        pass

    def get_response():
        """
        Generates HTTP response
        """
        pass

class HTTPServer(Thread):
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
            message = HTTPRequest(request)
            # print("METHOD:", message.get_method())
            # print("RESOURCE:", message.get_resource())
            # print("VERSION:", message.get_version())
            # print("HEADERS:", message.get_headers())


            # Send the reply
            if message.get_resource() == "/":
                with open("test.html") as f:
                    data = f.read()
                    connection.send(data.encode())

            logger.http_connection(message, 200)

            # Close connection too client (but not welcoming socket)
            connection.close()

s = HTTPServer()
s.start()
from SimpleHttpServer import HttpServer

server = HttpServer(port=80)

@server.route("/")
def index(request):
    with open("./resources/test.html") as f:
        data = f.read()

    return data

@server.route("/forbidden")
def forbidden(request):
    server.abort(403)

server.start()
import http.server


def new_http_mux():
    return HTTPMux()


class HTTPMux:
    def __init__(self):
        self.serve_mux = http.server.HTTPServer()

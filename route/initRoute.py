import http.server
import socketserver
from flask import Flask, request


class HTTPMux:
    def __init__(self):
        self.handlers = []

    def use(self, middleware):
        self.handlers.append(middleware)

    def handle_func(self, route):
        def decorator(func):
            self.handlers.append((route, func))
            return func

        return decorator


app = Flask(__name__)
mux = HTTPMux()


def auth(handler):
    def wrapper(*args, **kwargs):
        # 进行身份验证的逻辑
        return handler(*args, **kwargs)

    return wrapper


def args_filter(handler):
    def wrapper(*args, **kwargs):
        # 进行参数过滤的逻辑
        return handler(*args, **kwargs)

    return wrapper


def init_route(mux, ipc):
    mux.use(auth)
    mux.use(args_filter)

    @mux.handle_func("/version")
    def version_handler():
        v, err = ipc.version()
        utils.output(request, err, v)

    # 定义其他路由处理函数...


# 初始化路由
init_route(mux, ipc)

# 注册路由到 Flask 应用
for route, handler in mux.handlers:
    app.route(route)(handler)


class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="restricted", charset="UTF-8"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.headers.get('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write(b'Unauthorized')
        elif self.headers.get('Authorization') == 'Basic ' + (username + ':' + password).encode('utf-8').b64encode():
            super().do_GET()
        else:
            self.do_AUTHHEAD()
            self.wfile.write(b'Unauthorized')

    def do_POST(self):
        if self.headers.get('Authorization') is None:
            self.do_AUTHHEAD()
            self.wfile.write(b'Unauthorized')
        elif self.headers.get('Authorization') == 'Basic ' + (username + ':' + password).encode('utf-8').b64encode():
            super().do_POST()
        else:
            self.do_AUTHHEAD()
            self.wfile.write(b'Unauthorized')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Allow', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()

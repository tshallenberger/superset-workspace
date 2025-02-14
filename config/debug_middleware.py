from werkzeug.wrappers import Request
import pprint


class DebugMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # not Flask request - from werkzeug.wrappers import Request
        request = Request(environ)
        if "login" in request.path:
            print("[DEBUG] path: %s, url: %s" % (request.path, request.url))
            pprint.pprint(request)
            pprint.pprint(environ)
        elif request.path == "/oauth-authorized/okta":
            print("[DEBUG] path: %s, url: %s" % (request.path, request.url))
            pprint.pprint(request)
            pprint.pprint(environ)
        return self.app(environ, start_response)

from http.server import BaseHTTPRequestHandler, HTTPServer # python3
from datetime import datetime
import urlparse

host = ''
port = 80
instance_cache = dict()

def get_live_nodes():
#     TODO - implement
    return []

def redirect_request(request_type, ip):
#     TODO - implement
    pass

def write_request_handler(str_key, data, expiration_date):
    instance_cache[str_key] = [data, expiration_date]
    return

def read_request_handler(str_key):
    tup = instance_cache.get(str_key)
    cur_date = datetime.strptime(tup[1], '%d-%m-%Y')
    
    if tup:
        if cur_date <= datetime.now():
            return tup[0]
        else:
            instance_cache.pop(str_key)
        
    return None
        


class HandleRequests(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        par = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        self.wfile.write("get request {}".format(par).encode('utf-8'))
#         if self.path == "/get":
# #             read_request_handler(self.reqe)
#             self.wfile.write("get request".format(self).encode('utf-8'))
#         elif self.path == "/healthcheck":
#             self.wfile.write("Ok".format().encode('utf-8'))
        
    def do_POST(self):
        '''Reads post request body'''
        self._set_headers()
        if self.path =="/put":
#             content_len = int(self.headers.getheader('content-length', 0))
#             post_body = self.rfile.read(content_len)
#             self.wfile.write("received post request:<br>{}".format(post_body))
            self.wfile.write("put request".format().encode('utf-8'))

HTTPServer((host, port), HandleRequests).serve_forever()


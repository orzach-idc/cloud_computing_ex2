from http.server import BaseHTTPRequestHandler, HTTPServer # python3
from datetime import datetime
from furl import furl

host = ''
port = 80
instance_cache = dict()
instance_cache['test'] = ('orhilla', "22-06-2021")

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
    tup = instance_cache.get(str_key, None)
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
        f = furl(self.path)
        if f.path == "/get":
            response = read_request_handler(f.args['str_key'])
            self.wfile.write("get request = {}".format(response).encode('utf-8'))
        elif self.path == "/healthcheck":
            self.wfile.write("Ok".format().encode('utf-8'))
        
    def do_POST(self):
        '''Reads post request body'''
        self._set_headers()
        if self.path =="/put":
#             content_len = int(self.headers.getheader('content-length', 0))
#             post_body = self.rfile.read(content_len)
#             self.wfile.write("received post request:<br>{}".format(post_body))
            self.wfile.write("put request".format().encode('utf-8'))

HTTPServer((host, port), HandleRequests).serve_forever()


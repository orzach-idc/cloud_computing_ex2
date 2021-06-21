from http.server import BaseHTTPRequestHandler, HTTPServer # python3
from datetime import datetime
from furl import furl

host = ''
port = 80
instance_cache = dict()

def get_live_nodes():
#     TODO - implement
    pass

def hash_func():
#     TODO - implement
    pass

def redirect_request(request_type, ip, request_args):
#     TODO - implement
    pass

def create_http_request_template(request_type):
    pass
    
def write_request_handler(str_key, data, expiration_date):
    instance_cache[str_key] = [data, expiration_date]
    return "succeeded"

def read_request_handler(str_key):
    tup = instance_cache.get(str_key, None)
    tup_expiration_date = datetime.strptime(tup[1], '%d-%m-%Y')
    if tup != None:
        if tup_expiration_date >= datetime.now():
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
        
        if f.path == "/read":
            response = read_request_handler(f.args['str_key'])
            self.wfile.write("read request response: {}".format(response).encode('utf-8'))
            
#         elif f.path == "/get":
# #             send read request to 2 ec2 by getting ip from hash func
#             live_nodes = get_live_nodes()
#             node_ip = hash_func(f.args['str_key']) % len(live_nodes)
#             response = redirect_request('read', node_ip, f.args)
#             self.wfile.write("get request response: {} ".format(response).encode('utf-8'))
    
        elif self.path == "/healthcheck":
            self.wfile.write("Ok".format().encode('utf-8'))
        
    def do_POST(self):
        self._set_headers()
        f = furl(self.path)
        
        if f.path =="/write":
            response = write_request_handler(f.args['str_key'], f.args['data'], f.args['expiration_date'])
            self.wfile.write("write request response: {}".format(response).encode('utf-8'))
            
#         elif f.path == "/put":
#             send write request to 2 ec2 by getting ip from hash func
#             live_nodes = get_live_nodes()
#             node_ip = hash_func(f.args['str_key']) % len(live_nodes)
#             response = redirect_request('write', node_ip, f.args)
#             while not response:
#                 wait(10)
#             self.wfile.write("put request response: {}".format(response).encode('utf-8'))
HTTPServer((host, port), HandleRequests).serve_forever()


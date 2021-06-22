from http.server import BaseHTTPRequestHandler, HTTPServer # python3
from datetime import datetime
from furl import furl
import jump
import xxhash
import elb

host = ''
port = 80
instance_cache = dict()

def get_live_nodes():
    return elb.get_targets_status()

def hash_func(str_key, node_count):
    vnode_id = xxhash.xxh64(str_key).intdigest() % 1024
    return jump.hash(vnode_id, node_count)

def put_request_handler(ip1, ip2, request_args):
    request1 = f"http://{ip1}/write"
    request2 = f"http://{ip2}/write"
    response1 = request.post(request1, request_args)
    response2 = request.post(request2, request_args)
    
    return reponse1.status_code, response2.status_code

def get_request_handler(ip1, ip2, request_args):
    response1 = None
#     response2 = None
    request1 = f"http://{ip1}/read"
#     request2 = f"http://{ip2}/read"
    response1 = request.get(request1, request_args)
#     response2 = request.get(request2, request_args)
    
    return response1

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
            
        elif f.path == "/get":
#             send read request to 2 ec2 by getting ip from hash func
            live_nodes, sick = get_live_nodes()
            node_id = hash_func(f.args['str_key'], len(live_nodes))
            response = get_request_handler(live_nodes[node_id], live_nodes[node_id], f.args['str_key'])
            
            self.wfile.write("get request response: {} ".format(node_id).encode('utf-8'))
    
        elif self.path == "/healthcheck":
            self.wfile.write("Ok".format().encode('utf-8'))
        
    def do_POST(self):
        self._set_headers()
        f = furl(self.path)
        
        if f.path =="/write":
            response = write_request_handler(f.args['str_key'], f.args['data'], f.args['expiration_date'])
            self.wfile.write("write request response: {}".format(response).encode('utf-8'))
            
        elif f.path == "/put":
#             send write request to 2 ec2 by getting ip from hash func
            live_nodes = get_live_nodes()
            node_id = hash_func(f.args['str_key'], len(live_nodes))
#             response = put_request_handler(live_nodes[node_id], live_nodes[node_id + 1], f.args)
            self.wfile.write("put request response: {}".format(node_id).encode('utf-8'))
HTTPServer((host, port), HandleRequests).serve_forever()


from http.server import BaseHTTPRequestHandler, HTTPServer # python3
from datetime import datetime
from furl import furl
import jump
import xxhash
import elb
import requests

host = ''
port = 80
instance_cache = dict()
my_ip = (requests.get("http://169.254.169.254/latest/meta-data/public-ipv4").content).decode()
current_live_node_count = len(elb.get_live_nodes())

def get_live_nodes():
    return elb.get_targets_status()

def is_node_count_changed(node_count):
    return current_live_node_count == node_count

def hash_func(str_key, node_count):
    vnode_id = xxhash.xxh64(str_key).intdigest() % 1024
    return jump.hash(vnode_id, node_count)

def put_request_handler(ip1, ip2, request_args):
    response1 = None
    response2 = None
    if ip1 != my_ip:
        request1 = f"http://{ip1}/write"
        response1 = requests.post(request1, params = request_args)
    else:
        response1 = write_request_handler(request_args['str_key'])
    
    if ip2 != my_ip:
        request2 = f"http://{ip2}/write"
        response2 = requests.post(request2, params = request_args)
    else:
        response2 = write_request_handler(request_args['str_key'])
    
    return if response1 != None response1.text else response2.text

def get_request_handler(ip1, ip2, request_args):
    response1 = None
    response2 = None
    if ip1 != my_ip:
        request1 = f"http://{ip1}/read"
        response1 = requests.get(request1, params = request_args)
    else:
        read_request_handler(request_args['str_key'])
    
    if ip2 != my_ip:
        request2 = f"http://{ip2}/read"
        response2 = requests.get(request2, params = request_args)
    else:
        read_request_handler(request_args['str_key'])
        
    return if response1 != None response1.text.split(': ')[1] else response2.text.split(': ')[1] 

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
            ip1 = elb.get_instance_public_dns_name(live_nodes[node_id]['Id'])
            response = get_request_handler(ip1 , ip1, f.args)
            
            self.wfile.write("get request response: {} ".format(response).encode('utf-8'))
    
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


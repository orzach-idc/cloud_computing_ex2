from http.server import BaseHTTPRequestHandler, HTTPServer # python3
from datetime import datetime
from furl import furl
import jump
import xxhash
import elb
import requests
import threading
import time

host = ''
port = 80
instance_cache = dict()
my_ip = (requests.get("http://169.254.169.254/latest/meta-data/public-ipv4").content).decode()

def get_live_nodes():
    return elb.get_targets_status()

def check_for_update(node_count):
    global flag
    flag = True
    while flag:
        print('thread created')
        if current_live_node_count != node_count:
            update_all_instances()
        time.sleep(30)
        if !flag:
            print('killed')

def update_all_instances():
    for item in instance_cache.items():
#         delete expired item from cache
        item_expiration_date = datetime.strptime(item[1][1], '%d-%m-%Y')
        if item_expiration_date < datetime.now():
            instance_cache.pop(item[0])
#         check if instance update required
        else:
            live_nodes, sick = get_live_nodes()
            node_id1 = hash_func(item[0], len(live_nodes))
            node_id2 = (node_id1 + 1) % len(live_nodes)
            ip1 = elb.get_instance_public_ip(live_nodes[node_id1]['Id'])
            ip2 = elb.get_instance_public_ip(live_nodes[node_id2]['Id'])
            request_args = {
                'str_key': item[0],
                'data': item[1][0],
                'expiration_date': item[1][1]
            }
            redirect_request(ip1, request_args, 'write') 
            redirect_request(ip2, request_args, 'write') 
            

def hash_func(str_key, node_count):
    vnode_id = xxhash.xxh64(str_key).intdigest() % 1024
    return jump.hash(vnode_id, node_count)

def redirect_request(ip, request_args, request_path):
    response = None
    if ip != my_ip:
        request = f"http://{ip}/{request_path}"
        if request_path == 'write':
            response = requests.post(request, params = request_args)
#             response = requests.post(request)
            if response != None:
               response = response.text 
        else:
            response = requests.get(request, params = request_args)
            if response != None:
               response = response.text.split(': ')[1]
    else:
        if request_path == 'write':
            response = write_request_handler(request_args['str_key'], request_args['data'], request_args['expiration_date'])
        else:
            response = read_request_handler(request_args['str_key'])
        
    return response
    
def put_request_handler(ip1, ip2, request_args):
    response1 = redirect_request(ip1, request_args, 'write')
    response2 = redirect_request(ip2, request_args, 'write')
  
    return response1 if response1 != None else response2

def get_request_handler(ip1, ip2, request_args):
    response1 = redirect_request(ip1, request_args, 'read')
    response2 = redirect_request(ip2, request_args, 'read')
  
    return response1 if response1 != None else response2

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
        
        if f.path == "/update":
            update_all_instances()
        if f.path == "/read":
            response = read_request_handler(f.args['str_key'])
            self.wfile.write("read request response: {}".format(response).encode('utf-8'))
            
        elif f.path == "/get":
#             send read request to 2 ec2 by getting ip from hash func
            live_nodes, sick = get_live_nodes()
            node_id1 = hash_func(f.args['str_key'], len(live_nodes))
            node_id2 = (node_id1 + 1) % len(live_nodes)
            ip1 = elb.get_instance_public_ip(live_nodes[node_id1]['Id'])
            ip2 = elb.get_instance_public_ip(live_nodes[node_id2]['Id'])
            response = get_request_handler(ip1 , ip2, f.args)
            
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
            live_nodes, sick = get_live_nodes()
            node_id1 = hash_func(f.args['str_key'], len(live_nodes))
            node_id2 = (node_id1 + 1) % len(live_nodes)
            ip1 = elb.get_instance_public_ip(live_nodes[node_id1]['Id'])
            ip2 = elb.get_instance_public_ip(live_nodes[node_id2]['Id'])
            response = put_request_handler(ip1 , ip2, f.args)
            self.wfile.write("put request response: {}".format(response).encode('utf-8'))
if __name__ == "__main__":
    try:
        current_live_node_count = len(get_live_nodes())
        update_thread = threading.Thread(target=check_for_update) 
        HTTPServer((host, port), HandleRequests).serve_forever()
    finally:
        flag = False



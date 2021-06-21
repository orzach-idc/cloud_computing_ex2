from http.server import BaseHTTPRequestHandler, HTTPServer # python3

class HandleRequests(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
#         self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
#         print(f"self = {self}") 
        self._set_headers()
        elif self.path == "/get":
            self.wfile.write("get request".format().encode('utf-8'))
        elif self.path == "/healthcheck":
            self.wfile.write("Ok".format().encode('utf-8'))
        
    def do_POST(self):
        '''Reads post request body'''
        self._set_headers()
        if self.path =="/put":
            content_len = int(self.headers.getheader('content-length', 0))
            post_body = self.rfile.read(content_len)
            self.wfile.write("received post request:<br>{}".format(post_body))

host = ''
port = 80
HTTPServer((host, port), HandleRequests).serve_forever()

from http.server import BaseHTTPRequestHandler, HTTPServer
import time, sys

# HOST = 'localhost'
# PUERTO = 8000

class MiHandler(BaseHTTPRequestHandler):
    def do_POST(self):
    
        content_len = int(self.headers['Content-Length'])
        print(content_len)
        post_body = self.rfile.read(content_len)
        print(post_body.decode('utf-8'))
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

def print_usage():
    print('USAGE:\n\tserver.py [host] [port]\n')

if __name__ == '__main__':

    try:
        HOST = sys.argv[1]
        PUERTO = int(sys.argv[2])
    except:
        print_usage()
        sys.exit()

    httpd = HTTPServer((HOST, PUERTO), MiHandler)
    print(time.asctime(), 'Server started at %s:%s' % (HOST, PUERTO))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server stopped - %s:%s' % (HOST, PUERTO))



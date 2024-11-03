import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

class ThreadedHTTPServer(HTTPServer):
    def process_request(self, request, client_address):
        thread = threading.Thread(target=self.__new_connection, args=(request, client_address))
        thread.start()
        thread.join() 

    def __new_connection(self, request, client_address):
        self.finish_request(request, client_address)
        self.shutdown_request(request)

class MyRequestHandler(BaseHTTPRequestHandler):

    def _send_response(self, response, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/hello':
            self._send_response({'message': 'Hello, world!'})
        elif parsed_path.path == '/items':
            query_params = parse_qs(parsed_path.query)
            item = query_params.get('item', [''])[0]
            response = {'requested_item': item}
            self._send_response(response)
        else:
            self._send_response({'error': 'Not found'}, 404)

def run_server(server_class=ThreadedHTTPServer, handler_class=MyRequestHandler, port=3002):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

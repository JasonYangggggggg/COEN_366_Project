import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://admin:w5HI4gOqP1a3QHC4@cluster0.rpi2b.mongodb.net/p2p_shopping?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["p2p_shopping"]  
peers_collection = db["registered_peers"]  

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

    def do_POST(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            peer_info = json.loads(post_data)

            name = peer_info.get("name")
            ip_address = peer_info.get("ip_address")
            udp_socket = peer_info.get("udp_socket")
            tcp_socket = peer_info.get("tcp_socket")

            # check if the user's name is already registeredd
            if peers_collection.find_one({"name": name}):
                response = {"error": "Name already in use."}
                self._send_response(response, 400)
            else:
                peers_collection.insert_one({
                    "name": name,
                    "ip_address": ip_address,
                    "udp_socket": udp_socket,
                    "tcp_socket": tcp_socket
                })
                response = {"message": "REGISTERED", "name": name}
                self._send_response(response, 201)

        # deregister the peer IF he exists
        elif parsed_path.path == '/deregister':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            peer_info = json.loads(post_data)

            name = peer_info.get("name")

            # Remove peer from MongoDB if it exists
            if peers_collection.find_one({"name": name}):
                peers_collection.delete_one({"name": name})
                response = {"message": "DE-REGISTERED", "name": name}
                self._send_response(response, 200)
            else:
                # if not found just ignore
                response = {"error": "Name not registered."}
                self._send_response(response, 400)
        else:
            self._send_response({"error": "Not found"}, 404)

def run_server(server_class=ThreadedHTTPServer, handler_class=MyRequestHandler, port=3002):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

import socket
import json
import threading
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://admin:w5HI4gOqP1a3QHC4@cluster0.rpi2b.mongodb.net/p2p_shopping?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client["p2p_shopping"]
peers_collection = db["registered_peers"]

# UDP SETTINGS
UDP_IP = "0.0.0.0"  
UDP_PORT = 5000 

#UDP SOCKET SETUP 
#WE ARE NOT USING TCP HERE ( YET )
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"UDP server listening on port {UDP_PORT}")

def handle_register(data, addr):
    name = data.get("name")
    ip_address = addr[0]
    udp_socket = data.get("udp_socket")
    tcp_socket = data.get("tcp_socket")

    # Check if the USERNAME is taken
    if peers_collection.find_one({"name": name}):
        response = {"error": "REGISTER-DENIED: Name already in use."} 
        # ERROR MESSAGE ACCORDING TO PROJECT GUIDELINES
    else:
        peers_collection.insert_one({
            "name": name,
            "ip_address": ip_address,
            "udp_socket": udp_socket,
            "tcp_socket": tcp_socket
        })
        response = {"message": "REGISTERED", "name": name}
    
    sock.sendto(json.dumps(response).encode(), addr)

def handle_deregister(data, addr):
    name = data.get("name")
    
    #DELETE USER IF FOUND
    if peers_collection.find_one({"name": name}):
        peers_collection.delete_one({"name": name})
        response = {"message": "DE-REGISTERED", "name": name}
    else:
        response = {"error": "Name not registered."}

    sock.sendto(json.dumps(response).encode(), addr)

#keep listening all the timeee
while True:
    message, client_address = sock.recvfrom(4096)
    data = json.loads(message.decode())

    if data.get("action") == "register":
        handle_register(data, client_address)
    elif data.get("action") == "deregister":
        handle_deregister(data, client_address)

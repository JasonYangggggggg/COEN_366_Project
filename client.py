import socket
import json

# CLIENT CODE 
# LOCAL HOSTTTT
SERVER_IP = "127.0.0.1"  
SERVER_PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def register(name, udp_socket=6000, tcp_socket=7000):
    request = {
        "action": "register",
        "name": name,
        "udp_socket": udp_socket,
        "tcp_socket": tcp_socket
    }
    client_socket.sendto(json.dumps(request).encode(), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(4096)
    print("Register Response:", json.loads(response.decode()))

def deregister(name):
    request = {
        "action": "deregister",
        "name": name
    }
    client_socket.sendto(json.dumps(request).encode(), (SERVER_IP, SERVER_PORT))
    response, _ = client_socket.recvfrom(4096)
    print("Deregister Response:", json.loads(response.decode()))

if __name__ == "__main__":
    register("peer1")
    #deregister("peer1")

client_socket.close()

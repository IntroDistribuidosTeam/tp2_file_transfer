from socket import *
from time import sleep

SIZE = 1024
IP = ''
PORT = 11000

def main():
    skt = socket(AF_INET, SOCK_DGRAM)

    addr = (IP, PORT)

    skt.bind(addr)

    while True:
        msg, client_addr = skt.recvfrom(SIZE)
        response = msg.decode().upper()
        skt.sendto(response.encode(), client_addr)

if __name__ == "__main__":
    main()
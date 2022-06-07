from socket import *
from common.constants import SIZE,IP,PORT

def main():
    skt = socket(AF_INET, SOCK_DGRAM)
    skt.settimeout(1.0)
    addr = (IP, PORT)

    message = 'Hola'

    skt.sendto(message.encode(), addr)

    data, server_addr = skt.recvfrom(SIZE)

if __name__ == "__main__":
    main()

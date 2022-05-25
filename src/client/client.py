from socket import *

SIZE = 1024
IP = '127.0.0.1'
PORT = 11000

def main():
    skt = socket(AF_INET, SOCK_DGRAM)
    skt.settimeout(1.0)
    addr = (IP, PORT)

    message = 'Hola'

    skt.sendto(message.encode(), addr)

    data, server_addr = skt.recvfrom(SIZE)
    print('Msg: {data.decode()} | from: {server_addr}')

if __name__ == "__main__":
    main()

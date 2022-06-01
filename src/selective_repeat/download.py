import logging
import socket
from receiver import Receiver
from handshake import Handshake
from common.parser import parse_client_download_arguments


def main():
    args = parse_client_download_arguments()

    addr = (args.server_host, args.server_port)
    
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")


    print(args)
    #RUN CLIENT
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    reciver = Receiver(addr, args.dts, args.name, client)
    handshake = Handshake('U', args.name, client, addr)
    handshake.init_handshake()
    reciver.receive()
    client.close()

if __name__ == "__main__":
    main()
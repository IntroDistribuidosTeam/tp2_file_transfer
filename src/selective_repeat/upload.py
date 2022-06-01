import logging
import socket
from handshake import Handshake
from sender import Sender
from common.parser import parse_client_upload_arguments


def main():
    args = parse_client_upload_arguments()

    addr = (args.server_host, args.server_port)
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")

    print(args)
    # RUN CLIENT
    client_skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender = Sender(addr, args.src, args.name, client_skt)
    handshake = Handshake('U', args.name, client_skt, addr)
    handshake.init_handshake()
    sender.start_sender()
    client_skt.close()

if __name__ == "__main__":
    main()
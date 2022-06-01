import logging
import socket
from common.parser import parse_client_upload_arguments
#from client.client_upload import upload_file
from selective_repeat.sender import Sender
from selective_repeat.handshake import Handshake

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
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #result = upload_file(client, addr, args.src, args.name, logger)
    sender = Sender(addr, args.src, args.name, client)
    handshake = Handshake('U', args.name, client, addr)
    handshake.init_handshake()
    sender.start_sender_slow_start()
    client.close()

if __name__ == "__main__":
    main()
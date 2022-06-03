import logging
import socket
from common.constants import TIMEOUT
from common.parser import parse_client_upload_arguments
from common.sender import Sender
from common.handshake import Handshake

def main():
    args = parse_client_upload_arguments()

    addr = (args.server_host, args.server_port)
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format="%(message)s")

    print(args)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT)
    handshake = Handshake(client, addr)
    
    msg = 'U'.encode() + args.name.encode()
    
    new_addr = handshake.client_handshake(msg)
    if new_addr != addr:
        sender = Sender(new_addr, args.src, args.name, client)
        sender.start_sender_stop_and_wait()
    client.close()

if __name__ == "__main__":
    main()
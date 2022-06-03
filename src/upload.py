import logging
import socket
from common.constants import TIMEOUT,UPLOAD_CODE
from common.parser import parse_client_upload_arguments
from common.sender import Sender
from common.handshake import Handshake

def make_upload_package(file_name):
    msg = UPLOAD_CODE.encode() + file_name.encode()
    return msg

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
    
    msg = make_upload_package(args.name)
    
    new_addr = handshake.client_handshake(msg)
    if new_addr != addr:
        print ('se instancia el sender')
        sender = Sender(new_addr, args.src, args.name, client)
        sender.start_sender_selective_repeat()
    client.close()

if __name__ == "__main__":
    main()
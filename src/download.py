import logging
import socket
import os
from common.constants import TIMEOUT,DONWLOAD_CODE,LOG_FORMAT
from common.parser import parse_client_download_arguments
from common.receiver import Receiver
from common.handshake import Handshake

def make_download_packet(file_name):
    msg = DONWLOAD_CODE.encode() + file_name.encode()
    return msg

def main():
    args = parse_client_download_arguments()

    addr = (args.server_host, args.server_port)
    
    if args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format=LOG_FORMAT)


    print(args)
    if os.path.exists(args.dst):
        logging.error("Destination for file expected to be downloaded already exists.")
        return
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT)
    handshake = Handshake(client, addr)

    msg = make_download_packet(args.name)
    if os.path.exists(args.dst):
        logging.error("File dest already exists. Cancelling download.")
    else:
        new_addr = handshake.client_handshake(msg)
        logging.info("Handshake successfully finished")
        if new_addr != addr:
            receiver = Receiver(new_addr, args.dst, args.name, client)
            receiver.start_receiver_selective_repeat()
    client.close()


if __name__ == "__main__":
    main()

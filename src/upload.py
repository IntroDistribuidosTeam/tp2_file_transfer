import logging
import socket
import os
from common.constants import ACK, NACK, TIMEOUT,UPLOAD_CODE,LOG_FORMAT
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
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format=LOG_FORMAT)

    if not os.path.exists(args.src):
        logging.error("File expected to be uploaded does not exist.")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(TIMEOUT)
    handshake = Handshake(client, addr)
    
    msg = make_upload_package(args.name)
    
    ack,addr = handshake.client_handshake_dos(msg)
    
    if int.from_bytes(ack[2:],'big') != NACK:
        logging.error('Error, try again')
        client.close()
    else:
        sender = Sender(addr, args.src, args.name, client)
        sender.start_sender_selective_repeat()
        logging.info('closing socket')
    
        client.close()
        logging.info('socket closed')

if __name__ == "__main__":
    main()
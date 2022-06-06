from audioop import add
import logging
import socket
import os
from common.constants import NACK, TIMEOUT,DONWLOAD_CODE,LOG_FORMAT
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
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.basicConfig(level=log_level, format=LOG_FORMAT)


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
        ack,addr = handshake.client_handshake_dos(msg)
        
        if int.from_bytes(ack[2:],'big') != NACK:
            logging.error('Handshake fail, try again')
        else:
            receiver = Receiver(addr, args.dst, args.name, client)
            receiver.start_receiver_selective_repeat()
            logging.info('Receiver finished, cllosing socket')
    client.close()
    logging.info('Socket closed')


if __name__ == "__main__":
    main()

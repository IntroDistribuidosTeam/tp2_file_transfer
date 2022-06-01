import logging
import socket
from common.parser import parse_client_download_arguments
from client.client_download import download_file
from selective_repeat.receiver import Receiver
from selective_repeat.handshake import Handshake

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
    #download_file(client ,args.name,args.dst ,addr)
    reciver = Receiver(addr, args.dts, args.name, client)
    handshake = Handshake('U', args.name, client, addr)
    handshake.init_handshake()
    reciver.start_receiver_stop_and_wait()
    client.close()

if __name__ == "__main__":
    main()

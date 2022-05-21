from socket import *
from time import sleep
import signal
import logging
import sys
from common.protocol import parse_request, UPLOAD_CODE

SIZE = 1024

def start_server(addr):

    skt = socket(AF_INET, SOCK_DGRAM)

    skt.bind(addr)

    def signal_handler(sig, frame):
            logging.info("Closing server socket")
            skt.close()
            sys.exit()
    signal.signal(signal.SIGINT, signal_handler)


    while True:
        msg, client_addr = skt.recvfrom(SIZE)
        
        request = parse_request(msg)
        if (request['command'] == UPLOAD_CODE):
            logging.info('Upload')
            # Call upload  upload(request['filename], client_addr)
        else:
            logging.info('Upload')
            # Call download download(request['filename], client_addr)
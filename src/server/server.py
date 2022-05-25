from socket import *
from time import sleep
import signal
import logging
import sys
from common.protocol import parse_request, UPLOAD_CODE
import server_download
import server_upload
from constants import *
SIZE = 1024


def start_server(addr, storage_dir):

    skt = socket(AF_INET, SOCK_DGRAM)
    
    skt.bind(addr)

    def signal_handler(sig, frame):
        logging.info("Closing server socket")
        skt.close()
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)

    # TODO Checkear si el archivo existe
    while True:
        msg, client_addr = skt.recvfrom(SIZE)

        request = parse_request(msg)
        full_path = storage_dir + '/' + request['filename']
        if storage_dir[-1] == '/':
            full_path = storage_dir + request['filename']
        
        if (request['command'] == UPLOAD_CODE):
            logging.info('Upload')
            server_upload.upload(full_path, client_addr)

        else:
            logging.info('Upload')
            server_download.download(full_path, client_addr)

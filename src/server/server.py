import signal
import logging
import sys
import socket
from ..common import protocol,constants
import server_download
import server_upload

SIZE = 1024


def start_server(addr, storage_dir):

    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    skt.bind(addr)

    def signal_handler(sig, frame):
        logging.info("Signal %s in frame %s",sig,frame)
        logging.info("Closing server socket")
        skt.close()
        sys.exit()
   
    signal.signal(signal.SIGINT, signal_handler)

    # TODO Checkear si el archivo existe
    while True:
        msg, client_addr = skt.recvfrom(SIZE)

        request = protocol.parse_request(msg)
        full_path = storage_dir + '/' + request['filename']
        if storage_dir[-1] == '/':
            full_path = storage_dir + request['filename']

        if (request['command'] == constants.UPLOAD_CODE):
            logging.info('Upload')
            server_upload.upload(full_path, client_addr)

        else:
            logging.info('Upload')
            server_download.download(full_path, client_addr)

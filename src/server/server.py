import signal
import logging
import sys
import socket
import server.server_download as server_download
import server.server_upload as server_upload
from common import protocol,constants

def start_server(addr, storage_dir):

    skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    skt.bind(addr)
    print("Socket escuchando")

    def signal_handler(sig, frame):
        logging.info("Signal %s in frame %s",sig,frame)
        logging.info("Closing server socket")
        skt.close()
        sys.exit()
   
    signal.signal(signal.SIGINT, signal_handler)


    while True:
        msg, client_addr = skt.recvfrom(constants.BUFF_SIZE)

        print("se recibió %s de %s",msg.decode(),client_addr)
        
        request = protocol.parse_request(msg)
        full_path = storage_dir + '/' + request['filename']
        if storage_dir[-1] == '/':
            full_path = storage_dir + request['filename']

        if (request['command'] == constants.UPLOAD_CODE):
            logging.info('Upload')
            server_upload.upload(full_path, client_addr)

        else:
            print(" entro al download mode")
            logging.info('Upload')
            server_download.download(full_path, client_addr)

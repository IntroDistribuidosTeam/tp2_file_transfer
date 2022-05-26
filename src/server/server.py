import signal
import logging
import sys
import socket
import os.path
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

        print("se recibió %s de por parte del cliente %s",msg.decode(),client_addr)
        
        request = protocol.parse_request(msg)
        full_path = storage_dir + constants.DELIMETER + request['filename']

        if storage_dir[-1] == constants.DELIMETER:
            full_path = storage_dir + request['filename']

        if (request['command'] == constants.UPLOAD_CODE):
            if os.path.exists(full_path):
                logging.info("File %s uploaded by client %s already exists",request['filename'], client_addr)
                skt.sendto(str(constants.FILE_EXISTS).encode(), client_addr)

            else:
                logging.info('Upload')
                server_upload.upload(full_path,request['filename'], client_addr)

        else:
            print(" entro al download mode")
            logging.info('Upload')
            server_download.download(full_path, client_addr)

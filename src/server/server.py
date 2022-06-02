import signal
import logging
import sys
import socket
import os.path
import server.server_upload as server_upload
from common import constants


class Server:
    def __init__(self, addr, storage_dir):
        self.addr = addr
        self.storage_dir = storage_dir

    def start_server(self):
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        skt.bind(self.addr)
        print("Socket escuchando")

        def signal_handler(sig, frame):
            logging.info("Signal %s in frame %s", sig, frame)
            logging.info("Closing server socket")
            skt.close()
            sys.exit()
    
        signal.signal(signal.SIGINT, signal_handler)


        while True:
            msg, client_addr = skt.recvfrom(constants.MAX_RECV_BYTES)

            print("se recibió %s de por parte del cliente %s", msg.decode(), client_addr)
            
            request = msg.decode()[0]
            filename = msg.decode()[1:]

            full_path = self.storage_dir + '/' + filename
            if self.storage_dir[-1] == '/':
                full_path = self.storage_dir + request['filename']


            if (request == constants.UPLOAD_CODE):
                if os.path.exists(full_path):
                    logging.info("File %s uploaded by client %s already exists", filename, client_addr)
                    skt.sendto((constants.FILE_EXISTS).to_bytes(2, 'big'), client_addr)

                else:
                    logging.info('Upload')
                    server_upload.upload(full_path, filename, client_addr)

            else:
                print(" entro al download mode")
                logging.info('Upload')

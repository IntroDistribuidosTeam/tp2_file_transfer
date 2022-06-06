import signal
import logging
import sys
import socket
import os.path
from threading import Thread
import time
import server.server_upload as server_upload
import server.server_download as server_download
from common import constants


class Server:
    def __init__(self, addr, storage_dir):
        self.addr = addr
        self.storage_dir = storage_dir

    def start_server(self):
        skt = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        skt.bind(self.addr)

        threads = []

        def signal_handler(sig, frame):
            logging.info("Signal %s in frame %s", sig, frame)
            logging.info("Closing server socket")
            for t in threads:
                t.join()
            skt.close()
            sys.exit()
    
        signal.signal(signal.SIGINT, signal_handler)

        cont = 0
        while True:
            threads = [t for t in threads if t.isAlive()]

            msg, client_addr = skt.recvfrom(constants.BUFF_SIZE)

            request = msg.decode()[0]
            filename = msg.decode()[1:]

            full_path = self.storage_dir + '/' + filename
            if self.storage_dir[-1] == '/':
                full_path = self.storage_dir + filename

            if (request == constants.UPLOAD_CODE):
                if os.path.exists(full_path):
                    logging.error("File %s expected to be uploaded by client %s already exists", filename, client_addr)
                    msg = (4).to_bytes(2, 'big') + (constants.FILE_PROBLEM).to_bytes(2, 'big')
                    skt.sendto(msg, client_addr)

                else:
                    if cont == 0:
                        time.sleep(6)
                        cont +=1
                    logging.info('Upload')
                    t = Thread(target = server_upload.upload, args = (full_path, filename, client_addr))
                    t.start()
                    threads.append(t)

            else:
                if not os.path.exists(full_path):
                    logging.error("File %s expected to be downloaded by client %s does no exist", filename, client_addr)
                    msg = (constants.ACK_LEN).to_bytes(2, 'big') + (constants.FILE_PROBLEM).to_bytes(2, 'big')
                    skt.sendto(msg, client_addr)

                else:
                    logging.info('Download')
                    t = Thread(target = server_download.download, args = (full_path, filename, client_addr))
                    t.start()
                    threads.append(t)

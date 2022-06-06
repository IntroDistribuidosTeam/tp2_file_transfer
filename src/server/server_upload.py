import socket
import logging

from common.constants import TIMEOUT,UPLOAD_CODE
from common.handshake import Handshake
from common.receiver import Receiver


def upload(path, file_name, client_addr: tuple):

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(TIMEOUT)
    udp_socket.bind(('localhost', 0))

    handshake = Handshake(udp_socket, client_addr)
    if handshake.server_handshake(UPLOAD_CODE) > -1:
        logging.info('hanshake bien hecho')
        receiver = Receiver(client_addr, path, file_name, udp_socket)
        receiver.start_receiver_selective_repeat()
    else:
        logging.info('timeout in socket, closing.') 

    udp_socket.close()
    logging.info('udp socket closed')
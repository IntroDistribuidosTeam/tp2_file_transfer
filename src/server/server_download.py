import socket
import logging
from common.constants import TIMEOUT, DONWLOAD_CODE
from common.handshake import Handshake
from common.sender import Sender


def download(path, file_name, client_addr: tuple):
    ''' Download server function '''
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.settimeout(TIMEOUT)
    udp_socket.bind(('localhost', 0))
    handshake = Handshake(udp_socket, client_addr)

    if handshake.server_handshake(DONWLOAD_CODE) > -1:
        logging.info('Handshake done successfuly')
        sender = Sender(client_addr, path, file_name, udp_socket)
        sender.start_sender_selective_repeat()
    else:
        logging.info('Timeout in private socket, closing.')

    udp_socket.close()

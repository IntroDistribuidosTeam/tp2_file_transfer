import socket

from common.constants import TIMEOUT
from common.handshake import Handshake
from common.receiver import Receiver


def upload(path, file_name, client_addr: tuple):

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp_socket.settimeout(TIMEOUT)
    udp_socket.bind(('localhost', 0))
    handshake = Handshake(udp_socket, client_addr)
    handshake.server_handshake()

    receiver = Receiver(client_addr, path, file_name, udp_socket)
    receiver.start_receiver_selective_repeat()

    udp_socket.close()
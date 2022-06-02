import socket
import logging
import os.path
from selective_repeat.handshake import Handshake
from selective_repeat.receiver import Receiver
from common.constants import BUFF_SIZE,ACK,DELIMETER, NOT_EOF, MAX_NACK, NACK
import server.file as file
import server.server_download as server_download


def upload(path,file_name,client_addr:tuple):

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    handshake = Handshake(udp_socket,client_addr)
    handshake.server_handshake()

    receiver = Receiver(client_addr,path,udp_socket)
    receiver.start_receiver_stop_and_wait()

    udp_socket.close()
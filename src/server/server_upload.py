import socket
import logging
import os.path
from common.constants import BUFF_SIZE,ACK, DELIMETER, NOT_EOF, MAX_NACK,NACK
import server.file as file
import server.server_download as server_download

def recv_package(socket: socket):
    bytes_recv, _ = socket.recvfrom(BUFF_SIZE)
    packet = bytes_recv.decode()
    packet_parts = packet.split(DELIMETER, 1)
    return packet_parts


def upload(path,file_name,address):
    udp_socket:socket = server_download.start_new_connection(address)

    eof = NOT_EOF
    nack_counter = 0

    while not eof and nack_counter < MAX_NACK:
        try:
            package_parts = recv_package(udp_socket)
            eof = int(package_parts[0])
            file.append_file(path, package_parts[1])
            udp_socket.sendto(str(ACK).encode(), address)
        except TimeoutError as timeout:
            udp_socket.sendto(str(NACK).encode(), address)
            nack_counter += 1

    if nack_counter == MAX_NACK:
        os.remove(path)
        logging.info("Stopped uploading after repeated sequence of nacks")
        return
    logging.info("Finished uploading file %s from client %s",file_name, address)
    udp_socket.close()


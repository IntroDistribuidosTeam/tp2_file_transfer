import socket
import logging
import os.path
from common.constants import BUFF_SIZE,ACK, DELIMETER, NOT_EOF, MAX_NACK,NACK
import server.file as file
import server.server_download as server_download

def recv_packet(socket: socket,client_addr):
    nack_counter = 0
    error_list = [-1,0]

    while nack_counter < MAX_NACK:
        try: 
            bytes_recv, _ = socket.recvfrom(BUFF_SIZE)
        except TimeoutError as _:
            socket.sendto(str(NACK).encode(), client_addr)
            nack_counter += 1

    if (nack_counter == MAX_NACK):
        return error_list

    packet = bytes_recv.decode()
    packet_parts = packet.split(DELIMETER, 1)
    return packet_parts

def is_error(packet_parts):
    return (packet_parts[0] == -1)


def upload(path,file_name,client_addr):
    udp_socket:socket = server_download.start_new_connection(client_addr)

    eof = NOT_EOF
    error = False

    while eof == NOT_EOF and not error:
        packet_parts = recv_packet(udp_socket,client_addr)
        if is_error(packet_parts):
            error = True
            os.remove(path)
        else:
            eof = int(packet_parts[0])
            file.append_file(path, packet_parts[1])
            udp_socket.sendto(str(ACK).encode(), client_addr)

    if error:
        logging.info("Stopped uploading after repeated sequence of nacks")
        return   
    logging.info("Finished uploading file %s from client %s",file_name, client_addr)
    udp_socket.close()


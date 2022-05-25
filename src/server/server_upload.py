import socket
import logging
from common.constants import FILE_EXISTS,BUFF_SIZE,ACK
import server.file as file
import server.server_download as server_download



def upload(file_name, address):
    udp_socket:socket = server_download.start_new_connection(address)

    eof = False

    if file.file_already_exists(file_name):
        logging.info("File %s uploaded by client %s already exists",file_name, address)
        udp_socket.sendto(str(FILE_EXISTS).encode(), address)
        return

    while not eof:  
        (bytes_recv, address) = udp_socket.recvfrom(BUFF_SIZE)
        payload = bytes_recv.decode()
        playload_parts = payload.split('/', 1)

        eof = int(playload_parts[0])
        file.append_file(file_name, playload_parts[1])
        udp_socket.sendto(str(ACK).encode(), address)

    logging.info("Finished uploading file %s from client %s",file_name, address)
    udp_socket.close()


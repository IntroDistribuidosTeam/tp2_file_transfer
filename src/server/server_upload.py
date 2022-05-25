import socket
import logging
from file import file_already_exists, append_file
from server_download import start_new_connection
from constants import FILE_EXISTS,BUFF_SIZE,ACK



def upload(file_name, address):
    udp_socket = start_new_connection(address)

    eof = False

    if file_already_exists(file_name):
        logging.info("File {} uploaded by client {} already exists".format(
            file_name, address))
        udp_socket.sendto(str(FILE_EXISTS).encode(), address)
        return

    while not eof:  # TODO:Se cuelga si nunca manda el eof
        (bytes_recv, address) = udp_socket.recvfrom(BUFF_SIZE)
        payload = bytes_recv.decode()
        playload_parts = payload.split('/', 1)

        eof = int(playload_parts[0])
        append_file(file_name, playload_parts[1])
        udp_socket.sendto(str(ACK).encode(), address)

    logging.info("Finished uploading file {} from client {}".format(
        file_name, address))
    udp_socket.close()


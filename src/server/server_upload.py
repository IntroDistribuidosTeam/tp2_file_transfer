import socket

BUFF_SIZE = 1024
ACK = 1

def append_file(file_name,chunk):
    with open(file_name, 'w', encoding="utf8") as file:
        file.write(chunk)
        file.close()


def file_already_exists(file_name):
    try:
        file = open(file_name, encoding="utf8")
    except Exception:
        return False
    else:
        file.close()
        return True


def upload(udp_socket: socket, file_name):

    eof = False

    if file_already_exists(file_name):
        send_file_exists_message() #TODO: no hay un tipo de mensaje para los archivos repetidos

    while not eof: #TODO:Se cuelga si nunca manda el eof
        (bytes_recv, address) = udp_socket.recvfrom(BUFF_SIZE)
        payload = bytes_recv.decode()
        playload_parts = payload.split ('/' , 1)
        #TODO: aca faltaria el checksum
        eof = int (playload_parts[0])
        append_file(file_name,playload_parts[1])
        udp_socket.sendto(str(ACK).encode(), address)

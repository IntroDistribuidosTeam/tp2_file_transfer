import logging
import os.path
import socket
from common.parser import parse_client_upload_arguments
from common.constants import FILE_EXISTS, UPLOAD_CODE, DELIMETER, EOF, NOT_EOF, FILE_SIZE, ACK, NACK, MAX_NACK


def send_first_msg(client, file_name, addr):
    msg = UPLOAD_CODE + DELIMETER + file_name
    client.sendto(msg.encode(), addr)
    # espero ack
    data, address = client.recvfrom(1)
    return data.decode(), address

def read_file(file, file_len):
    end = NOT_EOF
    line = file.read(FILE_SIZE)
    if file.tell() == file_len :
        end = EOF
    msg = str(end) + DELIMETER
    return msg + line

def upload_file(client, addr, file_src, file_name , logger):
    if not os.path.exists(file_src):
        logger.error(f"The file {file_src} does not exist")
        return
    logger.info("Sending file")
    file = open(file_src, "r", encoding="utf8")

    file_len = os.path.getsize(file_src)

    nack_counter = 0

    # envio el primer mensaje solo con el nombre hasta que tenga un ack = 1
    response = NACK
    while response == NACK and nack_counter < MAX_NACK:
        try:
            response, addr = send_first_msg(client, file_name, addr) #TODO: meter el try catch en send_first_msg
        except TimeoutError as timeout:
            nack_counter += 1

    if nack_counter == MAX_NACK:
        file.close()
        return

    if int(response) == FILE_EXISTS:
        logger.info("A file with name %s already exists",file_name)
        file.close()
        print("llega un file Exists")
        return FILE_EXISTS

    # envio resto mensajes
    msg_send = read_file(file, file_len)
    while len(msg_send) != 2:
        response = NACK
        while response == NACK and nack_counter < MAX_NACK:
            try:
                client.sendto(msg_send.encode(), addr)
                response, _ = client.recvfrom(ACK)
                ## mensaje llego bien mando otro
                msg_send = read_file(file, file_len)
            except TimeoutError as timeout:
                nack_counter += 1

    logger.info("File uploaded")
    file.close()
   
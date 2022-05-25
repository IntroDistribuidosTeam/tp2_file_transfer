from logging import *
import logging
from socket import *
from common.constants import BUFF_SIZE, ACK, NACK, EOF, NOT_EOF, MODE_WRITE, MODE_ADD, DONWLOAD_CODE, DELIMETER
from common.protocol import set_up_logger


def send_request(client, file_name, addr: tuple):
    request = DONWLOAD_CODE + DELIMETER + file_name
    ack, addr = send_message(client, request, addr)

    while ack == NACK:
        ack, addr = send_message(client, request, addr)

def write_piece(file_name, mode, piece):
    try:
        with open(file_name, mode) as file:
            s = file.write(piece)
            print("escribio: %i bytes", s)
    except FileNotFoundError as error:

        logging.error("Error: Could not write in file")


def send_message(client_socket, msg, addr: tuple):
    bytes_sended = client_socket.sendto(msg.encode(), addr)
    if bytes_sended == len(msg):

        bytes_recibed, addr = client_socket.recvfrom(BUFF_SIZE)
        return bytes_recibed.decode(), addr

    else:
        logging.error("Error: Could not send all the bytes of the message: %s", msg)

def get_payload(bytes_read):

    payload = bytes_read.decode()
    eof = EOF if int(payload[0]) == EOF else NOT_EOF
    
    print(eof)
    return eof,payload[2:]



def send_ack(client, addr):
    bytes_sent = client.sendto(str(ACK).encode(), addr)

    while bytes_sent != ACK:
        bytes_sent = client.sendto(str(ACK).encode(), addr)


def download_file(client, file_name, path, addr: tuple):
    set_up_logger()

    send_request(client, file_name, addr)

    count_pieces = 0
    bytes_recibed, addr = client.recvfrom(BUFF_SIZE)
    eof, payload = get_payload(bytes_recibed)

    write_piece(path, MODE_WRITE, payload)
    logging.info("Success: Piece %s of the file downloaded", count_pieces)
    count_pieces += 1

    while eof == NOT_EOF:
        

        send_ack(client, addr)
        bytes_recibed, addr = client.recvfrom(BUFF_SIZE)

        eof, payload = get_payload(bytes_recibed)
        write_piece(path, MODE_ADD,payload)
        logging.info("Success: Piece %s of the file downloaded", count_pieces)

    
    send_ack(client, addr)

    client.close()

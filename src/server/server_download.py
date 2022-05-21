
import logging
import socket


BUFF_SIZE = 1024
FILE_SIZE = 1022
ACK = 1
NACK = 0


def set_up_logger():
    LOG_FORMAT = "%(asctime)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def is_ack(payload):

    if len(payload) > ACK or int(payload) != ACK:
        return False

    return True


def file_data(last_seek_send: int, file_name: str, end_of_file: bool):
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            # Muevo hasta el seek donde termine la ultima vez
            file.seek(last_seek_send)
            file_payload = file.read(FILE_SIZE).strip()
            last_seek_send = file.tell()

            if len(file_payload) <= FILE_SIZE:
                end_of_file = True

            return file_payload, last_seek_send, end_of_file

    except FileNotFoundError as e:
        logging.error("Exception: {}".format(e))


def is_nack(payload):
    if len(payload) > ACK or int(payload) != NACK:
        return False

    return True


def download(udp_socket: socket, file_name):
    set_up_logger()

    last_seek_send = 0
    end_of_file = False
    eof_ack = False

    while not end_of_file and not eof_ack:

        (bytes_read, address) = udp_socket.recvfrom(BUFF_SIZE)
        payload = bytes_read.decode()

        # Primero me fijo si es ACK
        if is_ack(payload):

            if end_of_file:
                logging.info("Last ACK recieved from {}".format(address))
                eof_ack = True
            else:

                logging.info("ACK recieved from {}".format(address))

                # encerrar esto en un try/catch
                data,last_seek_send,end_of_file = file_data(last_seek_send, file_name, end_of_file)

                #TODO make_response
                response = make_response(data, cheksum)
                udp_socket.send(response.encode())

        elif is_nack(payload):
            logging.info("NACK recieved from {}".format(address))
            #TODO terminar el nack
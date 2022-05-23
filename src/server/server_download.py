
from email.policy import default
import logging
import socket
from urllib import response


BUFF_SIZE = 1024
FILE_SIZE = 1023
ACK = 1
NACK = 0


def set_up_logger():
    LOG_FORMAT = "%(asctime)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def start_new_connection(address):

    s = socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('localhost',))  # asi me da un port nuevo cualquiera
    logging.info("New socket listing at: {}".format(s.getsocketname()))

    ack_package = str(1).encode()
    res = s.sendto(address)

    while res != ACK:
        logging.error("Coudn't sent ACK to: {} ".format(address))
        s.sendto(ack_package, address)
    return s


def is_ack(payload):

    if int(payload) != ACK:
        return False

    return True


def get_file_data(last_seek_send: int, file_name: str, end_of_file: bool):
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
        str(e),0,False
        


# NOTE Mirar lo del checksum
def make_response(payload: str, end_of_file: bool):

    eof = 1 if end_of_file else 0
    response = str(eof) + "," + payload

    return response.encode()


def default_response():
    return "0"


def is_nack(payload):
    if int(payload) != NACK:
        return False

    return True


def download(file_name, address):
    set_up_logger()
    udp_socket = start_new_connection(address)

    last_seek_send = 0
    end_of_file = False
    eof_ack = False
    last_response = default_response()

    while not end_of_file and not eof_ack:

        (bytes_read, address) = udp_socket.recvfrom(BUFF_SIZE)
        payload = bytes_read.decode()

        if is_ack(payload):

            if end_of_file:
                logging.info("Last ACK recieved from {}".format(address))
                eof_ack = True
            else:

                logging.info("ACK recieved from {}".format(address))

                data, last_seek_send, end_of_file = get_file_data(
                    last_seek_send, file_name, end_of_file)

                response = make_response(data, end_of_file)
                last_response = response
                res = udp_socket.sendto(response, address)

                if res != len(response):
                    logging.info("Cound not sent all bytes")
                    last_seek_send -= res
                else:
                    logging.info("PACKET sent to {}".format(address))

        elif is_nack(payload):

            logging.info("NACK recieved from {}".format(address))
            res = udp_socket.sendto(last_response, address)

            if res != len(last_response):
                logging.info("Cound not sent all bytes")
                last_seek_send -= res
            else:
                logging.info("PACKET sent to {}".format(address))

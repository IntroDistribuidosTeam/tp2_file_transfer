import socket
import logging
from common.constants import ACK,BUFF_SIZE,FILE_SIZE,NACK,DELIMETER, TIMEOUT, MAX_NACK

LOG_FORMAT = "%(asctime)s - %(message)s"
ERROR = -1

def set_up_logger():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def start_new_connection(address:tuple):

    initial_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    initial_socket.settimeout(TIMEOUT)
    initial_socket.bind(('localhost',0))
    logging.info("New socket listing at: %s",initial_socket.getsockname())

    ack_package = str(1).encode()
    res = initial_socket.sendto(ack_package,address)

    while res != ACK:
        logging.error("Coudn't sent ACK to: %s ",address)
        initial_socket.sendto(ack_package, address)
    return initial_socket

def is_error(payload):
    if int(payload) != ERROR:
        return False

    return True

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

    except FileNotFoundError as file_not_found_e:
        logging.error("Exception: %s ",file_not_found_e)
        return str(file_not_found_e), 0, True


def read_from_socket(udp_socket):
    max_timeouts = 0
    while max_timeouts < MAX_NACK:
        try:
            (bytes_read, address) = udp_socket.recvfrom(BUFF_SIZE)
            payload = bytes_read.decode()
            max_timeouts = MAX_NACK
        except TimeoutError as _:
            max_timeouts += 1
            payload = ERROR
            address = (str(ERROR),str(ERROR))

    return payload,address


def make_response(payload: str, end_of_file: bool):

    eof = 1 if end_of_file else 0
    response = str(eof) + DELIMETER + payload

    return response.encode()


def make_package(last_seek_send, file_name, end_of_file):
    data, last_seek_send, end_of_file = get_file_data(last_seek_send, file_name, end_of_file)
    return make_response(data, end_of_file)


def send_package(udp_socket,response,address):
    max_timeouts = 0
    while max_timeouts < MAX_NACK:
        try:
            res = udp_socket.sendto(response, address)
            max_timeouts = MAX_NACK
        except TimeoutError as _:
            max_timeouts += 1
            res = -1

    return res





def default_response():
    return "0"




def is_nack(payload):
    if (payload) != NACK:
        return False

    return True


def download(file_name, address):
    set_up_logger()
    udp_socket = start_new_connection(address)

    nack_counter = 0
    last_seek_send = 0
    end_of_file = False
    eof_ack = False
    last_response = default_response()
    

    
    response = make_package(last_seek_send, file_name, end_of_file)
    res = send_package(udp_socket,response,address)
    last_response = response
      
    while not end_of_file or not eof_ack:
        # si salta el timeout por parte de la lectura cierro socket
        # porque es responsabilidad del cliente de reenviarmelo por timeout
        payload, address = read_from_socket(udp_socket) 
        
        if is_error(payload):
            logging.error("TIMEOUT on reading, closing socket %s",address)
            end_of_file = True
            eof_ack = True
        elif is_ack(payload):
                
            if end_of_file:
                logging.info("Last ACK recieved from %s",address)
                eof_ack = True
            else:
                logging.info("ACK recieved from %s",address)
                res = send_package(udp_socket,last_response,address)

                if res == ERROR: 
                    end_of_file = True
                    eof_ack = True
                elif res != len(last_response):
                    logging.info("Cound not sent all bytes")
                    last_seek_send -= res
                else:
                    logging.info("PACKET re-sent to %s",address)
            

    udp_socket.close()
    logging.info("Socket closed.")
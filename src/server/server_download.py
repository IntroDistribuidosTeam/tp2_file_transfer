import socket
import logging
from common.constants import ACK,BUFF_SIZE,FILE_SIZE,NACK, DELIMETER
LOG_FORMAT = "%(asctime)s - %(message)s"


def set_up_logger():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def start_new_connection(address:tuple):

    initial_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    initial_socket.bind(('localhost',0))
    logging.info("New socket listing at: %s",initial_socket.getsockname())

    ack_package = str(1).encode()
    res = initial_socket.sendto(ack_package,address)

    while res != ACK:
        logging.error("Coudn't sent ACK to: %s ",address)
        initial_socket.sendto(ack_package, address)
    return initial_socket


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


# NOTE Mirar lo del checksum

def make_response(payload: str, end_of_file: bool):

    eof = 1 if end_of_file else 0
    response = str(eof) + DELIMETER + payload

    return response.encode()


def default_response():
    return "0"




def is_nack(payload):
    if (payload) != NACK:
        return False

    return True


def download(file_name, address):
    set_up_logger()
    udp_socket = start_new_connection(address)

    last_seek_send = 0
    end_of_file = False
    eof_ack = False
    last_response = default_response()
    
    #FIXME -> refactorizar esto
    data, last_seek_send, end_of_file = get_file_data(last_seek_send, file_name, end_of_file)

    response = make_response(data, end_of_file)
    last_response = response
    res = udp_socket.sendto(response, address)

      
    while not end_of_file or not eof_ack:

        (bytes_read, address) = udp_socket.recvfrom(BUFF_SIZE)
        payload = bytes_read.decode()

        if is_ack(payload):
            
            
            if end_of_file:
                logging.info("Last ACK recieved from %s",address)
                eof_ack = True
                
            else:

                logging.info("ACK recieved from %s",address)

                data, last_seek_send, end_of_file = get_file_data(
                    last_seek_send, file_name, end_of_file)

                response = make_response(data, end_of_file)
                last_response = response
                res = udp_socket.sendto(response, address)

                if res != len(response):
                    logging.info("Cound not sent all bytes")
                    last_seek_send -= res
                else:
                    logging.info("PACKET sent to %s",address)

        elif is_nack(payload):

            logging.info("NACK recieved from %s",address)
            res = udp_socket.sendto(last_response, address)

            if res != len(last_response):
                logging.info("Cound not sent all bytes")
                last_seek_send -= res
            else:
                logging.info("PACKET sent to %s",address)

    logging.info("Download finished.")
    udp_socket.close()

if __name__ == "__main__":
    print("anda")
from operator import imod
import threading
import time
import socket
import logging

from file_reader import FileReader

from common.constants import ACK,BUFF_SIZE,DELIMETER,MAX_NACK
WIN_SIZE = 4
SEC_BASE = 1
DELIMETER = '/'
MAX_RECV_BYTES = 2
TIME = 10
PAYLOAD_SIZE = 1021
LOG_FORMAT = "%(asctime)s - %(message)s"
ERROR = -1

# Sender
# Recibe los acks con numero de secuencia
# NOTE
# Ahora, nuestro ACK tiene un tam de 2 bytes
# Asi podremos tener hasta un sequence number de 65k

def default_response():
    return "0"

def is_error(payload):
    if int(payload) != ERROR:
        return False

    return True

def is_ack(payload):
    if int(payload) != ACK:
        return False

    return True
def make_response(payload: str, end_of_file: bool):

    eof = 1 if end_of_file else 0
    response = str(eof) + DELIMETER + payload

    return response.encode()

def set_up_logger():
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

class Sender:

    def __init__(self, socket_address: tuple, file_path, file_name, socket):
        self.socket = socket
        self.window_size = WIN_SIZE
        self.base_num = SEC_BASE
        self.window_threads = {}
        self.socket_addr = socket_address
        self.file_reader = FileReader(file_path,file_name)


    def recieve_ack(self):
        data, address = self.socket.recvfrom(MAX_RECV_BYTES)

        if self.socket_addr != address:
            self.socket_addr = address

        return data.decode()

    def repeat(self, socket: socket, addr, packet):
        byte = 0
        while byte != len(packet):
            time.sleep(TIME)
            byte += socket.sendto(packet[byte:].encode(), addr)

    def init_thread_pool(self, packets):
        threads = {}
        for i in range(self.base_num, self.window_size + 1):
            threads[i] += threading.Thread(target=self.repeat,
                                           args=[self.socket, self.socket_addr, packets[i]])
        return threads


    def get_new_base_num(self, buffer):
        i = 1
        keep = True
        while keep and i < len(buffer):
            if buffer[i] > (buffer[i-1]+1):
                keep = False

        self.base_num = (buffer[i-1]+1)
        return (i-1)

    def start_sender_selective_repeat(self):
        self.file_reader.file_exist()
        
        buffer = []
        packets = self.file_reader.get_packets(self.window_size, self.base_num)
        self.window_threads = self.init_thread_pool(packets=packets)

        while not self.file_reader.end_of_file():

            seq_num = int(self.recieve_ack())
            buffer.append(seq_num)

            self.window_threads[seq_num].cancel()
            self.window_threads.pop(seq_num)

            if seq_num == self.base_num:
                buffer.sort()
                move_foward = self.get_new_base_num(buffer=buffer)
                packets = self.file_reader.get_packets(move_foward, buffer[-1])

                for i in range(1, len(packets + 1)):
                    self.window_threads[buffer[-1] + i] += threading.Thread(
                        target=self.repeat, args=[self.socket, self.socket_addr, packets[i-1]])

        while len(buffer) != 4:
            seq_num = int(self.recieve_ack())
            buffer.append(seq_num)
            self.window_threads[seq_num].cancel()

        self.window_threads.clear()


    def make_package(self, end_of_file):
        data, end_of_file = self.file_reader.get_file_data(end_of_file)
        payload = make_response(data, end_of_file)
        return payload,end_of_file

    def send_package(self, response):
        max_timeouts = 0
        while max_timeouts < MAX_NACK:
            try:
                res = self.socket.sendto(response, self.socket_addr)
                max_timeouts = MAX_NACK
            except TimeoutError as _:
                max_timeouts += 1
                res = -1

        return res

    def read_from_socket(self):
        max_timeouts = 0
        while max_timeouts < MAX_NACK:
            try:
                (bytes_read, address) = self.socket.recvfrom(BUFF_SIZE)
                payload = bytes_read.decode()
                max_timeouts = MAX_NACK
            except TimeoutError as _:
                max_timeouts += 1
                payload = ERROR
                address = (str(ERROR),str(ERROR))
        self.socket_addr = address
        return payload
      
    def start_sender_slow_start(self):
        set_up_logger()
        ## esta logica se tendria que pasar a una clase server
    ## udp_socket = start_new_connection(address)

        end_of_file = False
        eof_ack = False
        last_response = default_response()
      
        response,end_of_file = self.make_package(end_of_file)
        res = self.send_package(response)
        last_response = response
        
        while not end_of_file or not eof_ack:
            # si salta el timeout por parte de la lectura cierro socket
            # porque es responsabilidad del cliente de reenviarmelo por timeout
            payload = self.read_from_socket()
            
            if is_error(payload):
                logging.error("TIMEOUT on reading, closing socket %s",self.socket_addr)
                end_of_file = True
                eof_ack = True
            elif is_ack(payload):
                  
                if end_of_file:
                    logging.info("Last ACK recieved from %s",self.socket_addr)
                    eof_ack = True
                    print("LLEGO ultimo ACK")
                else:
                    logging.info("ACK recieved from %s",self.socket_addr)
                  
                    response,end_of_file = self.make_package(end_of_file)
                    res = self.send_package(last_response)

                    if res == ERROR:
                        end_of_file = True
                        eof_ack = True
                    elif res != len(last_response):
                        logging.info("Cound not sent all bytes")
                        self.file_reader.update_seek(res)
                    else:
                        logging.info("PACKET sent to %s",self.socket_addr)

        logging.info("Socket closed.")
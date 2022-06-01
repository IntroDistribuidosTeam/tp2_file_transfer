import logging
import socket
from common.constants import NOT_EOF, MAX_WINDOW, MAX_NACK, BUFF_SIZE, DELIMETER
from file_writer import FileWriter


class Receiver:

    def __init__(self, sender_addr: tuple, file_path, file_name, socket):
        self.socket = socket
        self.window_size = MAX_WINDOW
        self.recv_base = 1
        self.recv_buff = {}
        self.sender_addr = sender_addr
        self.file_writer = FileWriter(file_path, file_name)

    def recv_payload(self):
        timeout_counter = 0
        error_list = [-1, 0, 0]

        while timeout_counter < MAX_NACK:
            try:
                bytes_recv, _ = self.socket.recvfrom(BUFF_SIZE)
            except socket.timeout as _:
                timeout_counter += 1

        if (timeout_counter == MAX_NACK):
            return error_list

        return bytes_recv.decode().split(DELIMETER, 2)


    def write_file(self, payload):
        chunk = payload
        self.recv_base += 1

        while self.recv_buff[self.recv_base] is not None:
            chunk += self.recv_buff[self.recv_base]
            self.recv_buff.pop(self.recv_base, None)
            self.recv_base += 1

        self.file_writer.write(chunk)

    def is_error(self, sequence_number):
        return (sequence_number == -1)

    def send_ack(self, sequence_number):
        bytes_sent = self.socket.sendto(
            str(sequence_number).encode(), self.sender_addr)

        while bytes_sent is not sequence_number and timeout_counter < MAX_NACK:
            try:
                bytes_sent, _ = self.socket.sendto(
                str(sequence_number).encode(), self.sender_addr)
            except socket.timeout as _:
                timeout_counter += 1

        
            bytes_sent = 

    def start_receiver(self):
        eof = NOT_EOF
        error = False
        #payload =[seq/eof/payload]

        while eof == NOT_EOF and not error:

            sequence_number,eof,payload = self.recv_payload()
            
            if self.is_error(sequence_number):
                self.file_writer.remove_path()
                error = True
            else:
            
                error = self.send_ack(sequence_number)
                if not error and sequence_number == self.recv_base:
                    self.write_file(payload)
                    
                    if (self.recv_base > int(1 << 16)):
                        self.recv_base = 0
                elif not error:
                    self.recv_buff[sequence_number] = payload

        if error:
            logging.info("Stopped receiving after repeated sequence of nacks")
            return
        logging.info("Finished uploading file %s from client %s",
                     self.file_writer.get_filepath(), self.sender_addr)

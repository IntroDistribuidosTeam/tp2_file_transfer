import logging
import socket
from common.constants import NOT_EOF, MAX_WINDOW, MAX_NACK, BUFF_SIZE, DELIMETER,ACK
from file_writer import FileWriter


class Receiver:

    def __init__(self, sender_addr: tuple, file_path, file_name, socket):
        self.socket = socket
        self.window_size = MAX_WINDOW
        self.recv_base = 1
        self.recv_buff = {}
        self.sender_addr = sender_addr
        self.file_writer = FileWriter(file_path, file_name)

    def recv_payload(self,total_payload_fields):
        timeout_counter = 0

        while timeout_counter < MAX_NACK:
            try:
                bytes_recv, _ = self.socket.recvfrom(BUFF_SIZE)
            except socket.timeout as _:
                timeout_counter += 1

        if (timeout_counter == MAX_NACK):
            return [-1] * total_payload_fields

        return bytes_recv.decode().split(DELIMETER, total_payload_fields-1)


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
        timeout_counter = 0

        while bytes_sent is not sequence_number and timeout_counter < MAX_NACK:
            try:
                bytes_sent, _ = self.socket.sendto(
                str(sequence_number).encode(), self.sender_addr)
            except socket.timeout as _:
                timeout_counter += 1

        if timeout_counter == MAX_NACK:
            return True
        return False


    def start_receiver_selective_repeat(self):
        eof = NOT_EOF
        error = False

        while eof == NOT_EOF and not error:

            sequence_number,eof,payload = self.recv_payload(total_payload_fields=3)
            
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
            logging.info("Stopped receiving packets due to error")
            return
        logging.info("Finished uploading file %s from client %s",
                     self.file_writer.get_filename(), self.sender_addr)


    def start_receiver_stop_and_wait(self):
        eof = NOT_EOF
        error = False

        while eof == NOT_EOF and not error:
            eof,payload = self.recv_payload(total_payload_fields=2)
            if self.is_error(eof):
                error = True
                self.file_writer.remove_path()
            else:
                eof = int(eof)
                self.file_writer.write(payload)
                error = self.send_ack(ACK)

        if error:
            logging.info("Stopped receiving packets due to error")
            return   
        logging.info("Finished receiving file %s from client %s", 
                     self.file_writer.get_filename(), self.sender_addr)
        
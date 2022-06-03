import logging
import socket

from common.file_writer import FileWriter
from common.constants import BUFF_SIZE, MAX_NACK, ACK, MAX_WINDOW, NOT_EOF, SEC_BASE, ACK_LEN


SEQUENCE_NUMBER_BYTES = 2

class Receiver:

    '''Implementation of receiver'''

    def __init__(self, sender_addr: tuple, file_path, file_name, udp_socket):
        self.socket = udp_socket
        self.recv_base = SEC_BASE
        self.recv_buff = {}
        self.sender_addr = sender_addr
        self.file_writer = FileWriter(file_path, file_name)

    def recv_payload(self):
        ''' Returns bytes read from private socket '''
        timeout_counter = 0
        bytes_recv = 0

        while timeout_counter < MAX_NACK and bytes_recv == 0:
            try:
                bytes_recv, _ = self.socket.recvfrom(BUFF_SIZE)
            except socket.timeout as _:
                timeout_counter += 1

        if timeout_counter == MAX_NACK:
            bytes_recv = (0).to_bytes(2,'big')

        return bytes_recv

    def write_file(self, payload):
        ''' Make file_writer writes payload'''

        chunk = payload
        self.recv_base += 1

        while self.recv_base in (self.recv_buff).keys():
            chunk += self.recv_buff[self.recv_base]
            self.recv_buff.pop(self.recv_base, None)
            self.recv_base += 1

        self.file_writer.write(chunk)

    def is_error(self, sequence_number):
        ''' Checks for an error '''
        return (sequence_number == -1)

    def send_response(self, sequence_number):
        '''Sends ack for packet received'''

        bytes_sent = 0
        timeout_counter = 0

        while bytes_sent != 4 and timeout_counter < MAX_NACK:
            try:
                response = (ACK_LEN).to_bytes(2, 'big') + sequence_number.to_bytes(2, 'big')
                bytes_sent = self.socket.sendto(response, self.sender_addr)
        
            except socket.timeout:
                timeout_counter += 1

        if timeout_counter == MAX_NACK:
            return True
        return False

    def decode_packet(self,bytes_recieved):
        ''' Make correct fields from bytes package'''
        if len(bytes_recieved) == 2:
            return [-1] * 4

        length = int.from_bytes(bytes_recieved[:2],'big')
        seq_num = int.from_bytes(bytes_recieved[2:4],'big')
        eof = int.from_bytes(bytes_recieved[4:5],'big')
        payload = bytes_recieved[5:]
        
        return seq_num, length, eof, payload
        
    def packet_in_window(self,sequence_number):
        max_possible_packets = self.recv_base + MAX_WINDOW
        if (self.recv_base + sequence_number) < max_possible_packets:
            return True
        return False


    def manage_packet(self, sequence_number, payload):
        '''' Decides if the package has to be stored or wrote '''
        if sequence_number == self.recv_base:
            self.write_file(payload)
        elif self.packet_in_window(sequence_number) and sequence_number not in (self.recv_buff).keys():
            self.recv_buff[sequence_number] = payload

    def start_receiver_selective_repeat(self):
        ''' Selective Repeat RTA'''

        eof = NOT_EOF
        error = False

        while eof == NOT_EOF and not error:

            bytes_received = self.recv_payload()
            sequence_number, length, eof, payload = self.decode_packet(
                bytes_received)

            if self.is_error(sequence_number):
                self.file_writer.remove_path()
                error = True

            elif len(bytes_received) == length:
                error = self.send_response(sequence_number)

                if sequence_number >= self.recv_base and not error:
                    self.manage_packet(sequence_number, payload)

        if error:
            logging.info("Stopped receiving packets due to error")
            return
        
        logging.info("Finished uploading file {} from client {}".format(self.file_writer.get_filename(), self.sender_addr))

    def start_receiver_stop_and_wait(self):
        ''' Stop and Wait RTA '''

        eof = NOT_EOF
        error = False

        while not error:
            bytes_received = self.recv_payload()
       
            _, length, eof, payload = self.decode_packet(bytes_received)
    
            if self.is_error(_):
                error = True
            elif length == len(bytes_received):
                self.file_writer.write(payload)
                error = self.send_response(ACK)
        
        if error:
            logging.info("Stopped receiving packets due to error")
            return
        logging.info("Finished receiving file %s from client %s",
                     self.file_writer.get_filename(), self.sender_addr)


